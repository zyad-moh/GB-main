# for functions
from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import Asset
from bson import ObjectId 
class AssetModel(BaseDataModel):# i need to inheret from base model to access db_client
   def __init__(self, db_client: object):
        super() .__init__(db_client=db_client)# come from db_client=request.app.db_client
        self.collection=db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]# means that self.collection now points to the "assets" collection in your MongoDB.  
   
   @classmethod
   async def create_instance(cls,db_client:object):
        instance = cls(db_client)# call init 
        await  instance.init_collection()# to create indices
        return instance   
   async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collection:
            self.collection=self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]#   كدا انا معايا الكولكشن collectoin named project in mongo db   بشاور على ال  ,     
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"],name=index["name"],unique=index["unique"])

   async def create_assets(self,asset:Asset):
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True)) #Means: “Execute an INSERT query on MongoDB and store the response in result
        asset.id = result.inserted_id

        return asset
   async def get_all_project_assets(self,asset_project_id:str,asset_type:str):
        records = await self.collection.find({
          "asset_project_id":ObjectId(asset_project_id )if isinstance(asset_project_id, str) else asset_project_id,
          "asset_type":asset_type,
          }).to_list(length=None)
        return[
          Asset(**record)# return record based on Asset pydantic model
          for record in records
        ]
        #the stringed one refer to the column in the collection but tha variabled one refer to  the project id come from the request , ObjectId(asset_project_id ) casting convert from str to ObjectId 
   async def get_asset_record(self,asset_project_id:str,asset_name:str):
        record = await self.collection.find_one({
          "asset_project_id":ObjectId(asset_project_id)if isinstance(asset_project_id, str) else asset_project_id,
          "asset_name":asset_name,
          })
        if record:  
          return Asset(**record)# return record based on Asset pydantic model
        return None


   async def get_last_asset_name(self, asset_project_id: str, asset_type: str):
          record = await self.collection.find_one(
               {
                    "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
                    "asset_type": asset_type
               },
               sort=[("_id", -1)]  # sort descending to get the latest inserted document
          )

          return[
          Asset(**record)# return record based on Asset pydantic model
        ]

          return None