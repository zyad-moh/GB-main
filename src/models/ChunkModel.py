# responsble for the chunk collection
from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne # type of action(insert_one)
class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super() .__init__(db_client=db_client) #here i pass db_clients to BaseDataModel (عشان يفضل شغال) 
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]# to access mongo db
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init 
        await  instance.init_collection()# to create indices
        return instance   
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]#   كدا انا معايا الكولكشن collectoin named project in mongo db   بشاور على ال  ,     
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])

    async def create_chunk(self,chunk:DataChunk):#take model with type DataChunk and insert in DB
       result=await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))#we will take convert to dict to be able to get into DB
       chunk._id=result.inserted_id
       return chunk
    async def get_chunk(self,chunk_asset_id:str):#
        result=await self.collection.find_one({

            "chunk_asset_id":ObjectId(chunk_asset_id)
        })
        if result is None:
            return None
        return DataChunk(**result)
    # if i insert chunk step by step it is not memory effeiciant sol batch write i pass data in form of batches 
    
    async def update_chunk_skills(self,chunk_asset_id:str,skills:list):#
        result=await self.collection.update_one({
            "chunk_asset_id":ObjectId(chunk_asset_id)
        },
        {
            "$set":{"skills":skills}
        }
        )
        if result is None:
            return None
        
    async def update_chunk_gap_skills(self,chunk_asset_id:str,gap_skills:list):#
        result=await self.collection.update_one({
            "chunk_asset_id":ObjectId(chunk_asset_id)
        },
        {
            "$set":{"gap_skills":gap_skills}
        }
        )
        if result is None:
            return None

    async def update_chunk_learning_recommendtion(self,chunk_asset_id:str,learning_recommendtion:list):#
        result=await self.collection.update_one({
            "chunk_asset_id":ObjectId(chunk_asset_id)
        },
        {
            "$set":{"learning_recommendtion":learning_recommendtion}
        }
        )
        if result is None:
            return None

    async def update_chunk_ats(self,chunk_asset_id:str,answer_score,answer_recommendetions):#
        result=await self.collection.update_one({
            "chunk_asset_id":ObjectId(chunk_asset_id)
        },
        {
            "$set":{"ats_score":answer_score,
                    "answer_recommendetions":answer_recommendetions
            }
        }
        )
        if result is None:
            return None
    
    async def insert_many_chunks(self,chunks:list,batch_size:int=100):
       for i in range(0,len(chunks),batch_size):
          batch=chunks[i:i+batch_size]# at each itire batch contain diff chunks with size 100 
          operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
          ] 
          await self.collection.bulk_write(operations)#??
       return len(chunks)  
    async def delete_chunk_by_project_id(self,project_id:ObjectId):#delet chunk by project id
        result=await self.collection.delete_many(
            { "chunk_project_id" : project_id}
        )
        return result.deleted_count    
    async def get_project_chunk(self,project_id:ObjectId,page_no:int=1,page_size:int=50):
        records = await self.collection.find( # i have to make skip to prevent 
            {"chunk_project_id" : project_id}
        ).skip(
                (page_no-1) * page_size
                ).limit(page_size).to_list(length=None)
        
        return [
            DataChunk(**record)
            for record in records
        ]
        #So record is coming from an async function but is being used without await.

"""
❓ السؤال المهم:

إزاي هيعمل indexing على collection مش موجودة؟

✅ الإجابة:

👉 MongoDB بيخلق collection تلقائيًا عند أول عملية write أو index

"""

