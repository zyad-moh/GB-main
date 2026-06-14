# responsble for the project collection
from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super() .__init__(db_client=db_client) #here i pass db_clients to BaseDataModel (عشان يفضل شغال) 
        self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
# now i have the collectoin lets make some process 1-creat project field
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init 
        await  instance.init_collection()# to create indices
        return instance   
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes=Project.get_indexes()
            for index in indexes:# here we make for loop and list as if we have more than one index in the collection like index 1 on project id and index 2 on order or any thing else
               await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])

    async def  create_project(self,project:Project):# let'ss use the scheme this function will take object from project(pydantic) to insert it
        result=await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))#await for motor , each document in collectoin have extra _id or could say inserted with id 
        project.id=result.inserted_id  # when insert data _id musn't be there as if he exist it's prevent mongo to create _id
        return project # what if _id doesn't exist in result.inserted_id sol (get/create)

    async def  get_project_or_create_one(self,project_id:str):# let'ss use the scheme this function will take object from project(pydantic) to insert it
        print("ENTER FUNCTION")
        record= await self.collection.find_one({
            "project_id":project_id # field named project_id with type project_id
        })
        print("AFTER FIND_ONE")
        print(record)
        if record is None:
            project=Project(project_id=project_id)#دا كله عشان اقوله خزن ال بروجكت اى دى بس تبع ال scheme 
            project=await self.create_project(project=project)
            return project
        print("BEFORE PYDANTIC")
        return Project(**record)#record is dict but i need it to be from project type
        #don't use get_all without paggination # like in google split all 100 search result in 10 pages 
    async def get_all_projects(self, page: int=1, page_size: int=10):#number of pages and page_size    
        # count total number of documents
        total_documents = await self.collection.count_documents({})
        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0:
           total_pages += 1
        cursor = self.collection.find().skip((page-1)* page_size).limit(page_size)#cursor(is a list) for payload and memory efficient
        projects = []
        async for document in cursor:
           projects.append(
           Project( ** document)
           )
        return projects, total_pages #!!!!!!!!!!!!

"""Short, clear answer

MongoDB will generate 10 DIFFERENT _id values
even if:

all 10 files are uploaded

in the same request

with the same project_id = 1

_id is per document, not per request, not per project."""