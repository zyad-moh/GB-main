# this for upload 
from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request #as file have a spatial class in fast api
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,settings
from controllers import DataController,ProjectController,ProcessController #don't forget i accessed them easly because of __init__ files
import aiofiles                                          
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel#contain functions like create
from models.db_schemes import DataChunk,Asset
from models.enums.AssetTypeEnum import AssetTypeEnum
logger = logging.getLogger('uvicorn.error')
data_router=APIRouter( # prefix for end point
   prefix="/api/v1/data",
   tags=["api_v1","data"],
)
# project id : when make procces like upload file i (user) should tell system what is project id 
#function for end point 
@data_router.post("/upload/{project_id}")# end point , recieve file then upload it to the system
async def upload_data(request:Request,project_id:str,file:UploadFile,
                     app_settings:settings=Depends(get_settings)): 
   
   project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
   project=await project_model.get_project_or_create_one( #await to able to collect results
      project_id=project_id
   )#here we store project_id in mongodb using projectmodel based on db_scheme (project)
   isvalid,res=DataController().validate_uploaded_file(file=file) 
   
   if not isvalid:
      return JSONResponse(# for change 200ok in false response to
         status_code=status.HTTP_400_BAD_REQUEST,
         content={
            "signal":res
         }
      )
   
   file_path,file_id=DataController().generate_unique_filepath(orig_file_name=file.filename,project_id=project_id)
   project_dir_path=ProjectController().get_project_path(project_id=project_id)#for saaaaaaveeeeee storeeeee the file which uploaded from user
   """file_path=os.path.join(
      project_dir_path,
      file.filename
   )"""#path of uploaded file on my disk
   try:
    async with aiofiles.open(file_path,"wb") as f: #If the file does not exist → it is created
       while chunk:=await file.read(app_settings.FILE_DEFULT_CHUNK_SIZE):
         await f.write(chunk) #this code creates an empty file on disk and then fills it chunk by chunk with the contents of the uploaded file.
   except Exception as e:
      logger.error(f"Error while uploading file: {e}")# contain the hidden info (error not showen to user)
      return JSONResponse(# for change 200ok in false response to
         status_code=status.HTTP_400_BAD_REQUEST,
         content={
            "signal":ResponseSignal.FILE_UPLOAD_FAILED.value
         }
      )
   asset_model=await AssetModel.create_instance(db_client=request.app.db_client)# that create the collection if not exist not creaate the the document
   asset_resource =Asset(
      asset_project_id=project.id,
      asset_type=AssetTypeEnum.FILE.value,
      asset_name=file_id,
      asset_size=os.path.getsize(file_path)
   )# it's just the parameter of assets
   asset_record = await asset_model.create_assets(asset=asset_resource )

   return JSONResponse(
       content={
           "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
           "file id": str(asset_record.id),
           #"project_id":str(project._id)
         }
         )
   

@data_router.post("/process/{project_id}")
async def procces_endpoint(request:Request,project_id:str , Proccess_Request: ProcessRequest):#Proccess_Request it's like (file_id,chunk_size,over_lap,do_reset -> parameters came with request in postman->body->raw) but it's processed
   # file_id=Proccess_Request.file_id 
   chunk_size=Proccess_Request.chunk_size
   overlap_size=Proccess_Request.overlap_size
   do_reset=Proccess_Request.do_reset

   project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
   project=await project_model.get_project_or_create_one( #await to able to collect results
      project_id=project_id
   )

   project_file_ids={}
   asset_model=await AssetModel.create_instance(
      db_client=request.app.db_client)# here to connect to mongo db 
   if Proccess_Request.file_id:
      asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=Proccess_Request.file_id)
      if asset_record is None: 
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
               "signal":ResponseSignal.FILE_ID_ERROR.value,
            }
         )
      project_file_ids = {asset_record.id:asset_record.asset_name}#asset_name for apply process of chunking amd id for show recourse
   else:
      project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,) # note when create asset we use the mongodb id(the id made for each project_id) not the request id
      project_file_ids={record.id:record.asset_name for record in project_files}# from asset collection store only the file_id(asset_name)and asset id of the spacified project.id,asset_type note project.id,asset_type contain many files
   # we used .asset_name instade of["asset_name"] as now record is pydantic model 
   if len(project_file_ids) == 0: 
      return JSONResponse(
         status_code=status.HTTP_400_BAD_REQUEST,
         content={
            "signal":ResponseSignal.NO_FILES_ERROR.value,
         }
      )
   # i need to apply the below code on all element (file_id) in project_file_ids 
   Process_Controller=ProcessController(project_id=project_id)
   chunk_model=ChunkModel(db_client=request.app.db_client)# obj from ChunkModel cladd which have functions like delete 

   if do_reset == 1:
         _ = await chunk_model.delete_chunk_by_project_id(# i need to konw how function runed also i didn't call the _ ????? 
            project_id=project.id# mesh 1 ao 2 elly bib2o mawgodin fe el requset la da el project id in mongo db
         )
   no_records = 0
   no_files=0
   for asset_id,file_id in project_file_ids.items():
      file_content=Process_Controller.get_file_content(file_id=file_id)

      if file_content is None:# may be error when get file from source 
         logger.error(f"error while processing {file_id}")
         continue

      file_chunks =Process_Controller.procces_file_content(file_content=file_content,file_id=file_id,chunk_size=chunk_size,overlap_size=overlap_size)
      
      if file_chunks is None or len(file_chunks) == 0:
         return JSONResponse(
               status_code=status.HTTP_400_BAD_REQUEST,
               content={
                  "signal": ResponseSignal.PROCESSING_FAILED.value
               }
         )
      # i need to convert each chunk to object of data chunk
      file_chunks_records=[
         DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
            chunk_asset_id =asset_id #id of file which defiend from mongo to know from which asset this chunk is come (you will find many chunk related to one asset) , instad of open recourse to see recourse of file(asset) 
         )
         for i,chunk in enumerate(file_content)# file_content   it was file_chunks
      ]
      
      

      no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
      no_files +=1
   return JSONResponse(
      {
         "signal" : ResponseSignal.PROCESSING_SUCCESS.value,
         "inserted_chunks" : no_records,
         "processed_files" : no_files
      }

   )
# note here (async def upload_data) i get uploaded file , i need to validate it (logic -> controller )
# chunk by chunk it's similar data augmantation you know !!!
#Lazy loading , Streaming data instead of loading all at once
#raise TypeError(f'Object of type {o.__class__.__name__} '
#   TypeError: Object of type ResponseSignal is not JSON serializable 
# return {"signal": ResponseSignal.FILE_TYPE_NOT_SUPPORTED} should be FILE_TYPE_NOT_SUPPORTED.value
""""1️⃣ mongo_data:/data/db

This is the Docker named volume.

It tells Docker where MongoDB stores its data inside the container.

Example from docker-compose.yml:

volumes:
  - mongo_data:/data/db


✅ This has nothing to do with the connection URL.
It is purely for persistent storage inside Docker.

2️⃣ MONGODB_URL

This is the connection string your app uses to talk to MongoDB.

It does not refer to the volume name.

It refers to where MongoDB is listening, which depends on your host or Docker network."""
#request:Request:you need to know each info about comming request ,and contain the app in main
