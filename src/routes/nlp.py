from fastapi import FastAPI,APIRouter,Depends,UploadFile,status,Request,Query,HTTPException #as file have a spatial class in fast api
from fastapi.responses import JSONResponse
from .schemes.nlp import PushRequest , SearchRequest,SkillRequest,Skill_gap_Request,RunAllRequest
from controllers import NLPController
import logging
from models import ResponseSignal
from models.AssetModel import AssetModel
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
import json 
from typing import List
from models.enums.AssetTypeEnum import AssetTypeEnum
import requests

logger = logging.getLogger('uvicorn.error')

nlp_router=APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1"]
)
"""@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,PushRequest:PushRequest):
    # we need the project which contain the project_id 
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    chunk_model=ChunkModel(db_client=request.app.db_client)
    
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    if not project:
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
        "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value})

    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,

    )
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    while has_records:
        page_chunks = await chunk_model.get_project_chunk(project_id=project.id, page_no=page_no)
        if len(page_chunks):
            page_no += 1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = list (range(idx,idx+len(page_chunks)))
        idx+=len(page_chunks)
        is_inserted = nlp_controller.index_into_vector_db(
        project = project , 
        chunks = page_chunks,
        do_reset=PushRequest.do_reset,
        chunks_ids=chunks_ids,
         )
        if not is_inserted:
                return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_ERROR.value})
        inserted_items_count += len(page_chunks)
    
    return JSONResponse(
            content={
            "signal": ResponseSignal.INSERT_INTO_VECTOR_DB_SUCCESS.value,
            "inserted_items_count" : inserted_items_count
            
            })
"""

"""@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request:Request,project_id:str):
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,

    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    return JSONResponse(
            content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info" : collection_info
            
            })
"""
"""@nlp_router.post("/index/search/{project_id}")
async def search_index(request:Request,project_id:str,search_request:SearchRequest):# here i apply semantic search betwean the query (after get it's embedding) and the chunks in vector db
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    results = nlp_controller.search_vector_db_collection(#list of retrive document 
        project=project,
        text=search_request.text,
        limit=search_request.limit
        )
    if not results:
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
        "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value
            }
        )
    return JSONResponse(# need dict or list of
            content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results" : [res.dict() for res in results]
            
            })
"""

@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request:Request,project_id:str):# here i apply semantic search betwean the query (after get it's embedding) and the chunks in vector db
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
   
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)

    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    answer , full_prompt , chat_history = nlp_controller.answer_rag_question(
        project=project,
        query="extract",
        asset_record = chunk_data.chunk_text,
        limit= 2
        
    )
    s1 = json.loads(answer)
    _ = await chunk_model.update_chunk_skills(asset_record.id,s1["skills"])
    request.app.state.skills = s1["skills"]
    if not answer :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    return JSONResponse(# need dict or list of
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer" : answer,
            "full_prompt" : full_prompt,
            "chat_history" : chat_history
        
        })
@nlp_router.get("/index/retun_skills/{project_id}")
async def retun_skills(request:Request,project_id:str):
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    
    if not chunk_data or not chunk_data.skills:
        return []
    
    clean_skills = nlp_controller.split_commas(nlp_controller.extract_skills(chunk_data.skills))
    
    return clean_skills
@nlp_router.post("/index/skill_gap/{project_id}")
async def skill(request:Request,project_id:str,user_skill:SkillRequest):
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    answer , full_prompt , chat_history,mnmn = nlp_controller.skill_gap_system(
        request=request,
        query="skill_gap",
        user_skill=user_skill.user_skill,
        role=project.role
    )


    
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    
    chunk_model=ChunkModel(db_client=request.app.db_client)
    _ = await chunk_model.update_chunk_gap_skills(asset_record.id,list(answer))



    if not answer :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    return JSONResponse(# need dict or list of
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer" : list(answer),
            "full_prompt" : full_prompt,
            "chat_history" : chat_history,
            "skills":mnmn
        })

@nlp_router.get("/index/retun_gap_skills/{project_id}")
async def retun_gap_skills(request:Request,project_id:str):
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    
    if not chunk_data or not chunk_data.gap_skills:
        return []
    
    clean_skills = nlp_controller.split_commas(nlp_controller.extract_skills(chunk_data.gap_skills))
    
    return clean_skills

@nlp_router.post("/index/learning_recommendtion/{project_id}")
async def learning_recommendtion(request:Request,project_id:str,user_gap_skill:Skill_gap_Request):
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    answer = nlp_controller.learning_recommendtion(
        request=request,
        user_gap_skill=user_gap_skill,
        role=project.role
    )
    

    
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    
    chunk_model=ChunkModel(db_client=request.app.db_client)
    _ = await chunk_model.update_chunk_learning_recommendtion(asset_record.id,answer)




    if not answer :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    return JSONResponse(# need dict or list of
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer" : (answer),
            
        })


@nlp_router.get("/index/retun_learning_recommendtion/{project_id}")
async def retun_learning_recommendtion(request:Request,project_id:str):
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    
    data = chunk_data.learning_recommendtion if chunk_data else None
    
    if not data:
        return {}
    
    # If stored as raw string (old data), try to parse it
    if isinstance(data, str):
        try:
            import json, re
            # Remove markdown fences if present
            cleaned = data.replace("```json", "").replace("```", "").strip()
            # Try to extract JSON object
            start = cleaned.find('{')
            if start != -1:
                depth = 0
                for i in range(start, len(cleaned)):
                    if cleaned[i] == '{': depth += 1
                    elif cleaned[i] == '}': depth -= 1
                    if depth == 0:
                        return json.loads(cleaned[start:i+1])
            return json.loads(cleaned)
        except Exception:
            return {}
    
    return data



@nlp_router.post("/index/ats_score/{project_id}")
async def ats_score(request:Request,project_id:str):# here i apply semantic search betwean the query (after get it's embedding) and the chunks in vector db
    nlp_controller = NLPController(
        vectordb_client = request.app.vectordb_client,
        generation_client = request.app.generation_client,
        embedding_client = request.app.embedding_client,
        template_parser = request.app.template_parser,
    )
   
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)

    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    answer_score,answer_recommendetions = nlp_controller.ats_score(
        asset_record = chunk_data.chunk_text,     
    )
    _ = await chunk_model.update_chunk_ats(asset_record.id,answer_score,answer_recommendetions)

    if not answer_score  :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
            "signal": ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    return JSONResponse(# need dict or list of
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer_score" : answer_score,
            "answer_recommendetions" :answer_recommendetions
        
        })


@nlp_router.get("/index/retun_ats_score_recommendtion/{project_id}")
async def retun_ats_score_recommendtion(request:Request,project_id:str):
    project_model = await ProjectModel.create_instance(# object from ProjectModel
        db_client=request.app.db_client
    )
    
    project = await project_model.get_project_or_create_one(
            project_id=project_id # function  from object
    )
    asset_model=await AssetModel.create_instance(
        db_client=request.app.db_client)
    project_file_ids={}
    project_files=await asset_model.get_last_asset_name(asset_project_id=project.id,asset_type=AssetTypeEnum.FILE.value,)
    project_file_ids={record.id:record.asset_name for record in project_files}
    asset_id,file_id = list(project_file_ids.items())[0]
    asset_record=await asset_model.get_asset_record(asset_project_id=project.id,asset_name=file_id)
    chunk_model=ChunkModel(db_client=request.app.db_client)
    chunk_data = await chunk_model.get_chunk(asset_record.id)
    
    return chunk_data.ats_score , chunk_data.answer_recommendetions



APP_ID = "e58471d6"
APP_KEY = "a610ceeedde21bbf7f86e4b1e33dd1c3"


@nlp_router.post("/index/jops/{project_id}")
async def get_jobs(
    what: str = Query(default="developer"),
    where: str = Query(default="London"),
    country: str = Query(default="gb"),
    page: int = Query(default=1)
):

    # validation
    if not what and not where:
        raise HTTPException(
            status_code=400,
            detail="Missing search params"
        )

    try:

        response = requests.get(
            f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}",
            params={
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": 10,
                "what": what or "developer",
                "where": where or "London"
            }
        )

        data = response.json()

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "search": {
                    "what": what,
                    "where": where,
                    "country": country
                },
                "page": page,
                "results": len(data.get("results", [])),
                "data": data.get("results", [])
            }
        )

    except Exception as err:

        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(err)
            }
        )


# run:
# uvicorn main:app --reload --port 5000

@nlp_router.post("/index/run_all/{project_id}")
async def run_all(
    request: Request,
    project_id: str,
    payload: RunAllRequest
):
    skill_request = payload.skill_request
    gap_request = payload.gap_request

    # 1. extract skills
    answer_result = await answer_rag(
        request=request,
        project_id=project_id
    )

    # 2. return skills
    skills_result = await retun_skills(
        request=request,
        project_id=project_id
    )

    # 3. skill gap analysis
    gap_result = await skill(
        request=request,
        project_id=project_id,
        user_skill=skill_request
    )

    # 4. learning recommendation
    learning_result = await learning_recommendtion(
        request=request,
        project_id=project_id,
        user_gap_skill=gap_request
    )

    # 5. ats score
    ats_result = await ats_score(
        request=request,
        project_id=project_id
    )





