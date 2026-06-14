from .BaseDataModel import BaseDataModel
from .db_schemes import Interview
from .enums.DataBaseEnum import DataBaseEnum

class InterviewModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_INTERVIEW_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        collection_names = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_INTERVIEW_NAME.value not in collection_names:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_INTERVIEW_NAME.value]
            indexes = Interview.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_interview(self, interview: Interview):
        result = await self.collection.insert_one(interview.dict(by_alias=True, exclude_unset=True))
        interview.id = result.inserted_id
        return interview

    async def get_interview_by_id(self, interview_id: str):
        record = await self.collection.find_one({"interview_id": interview_id})
        if record is None:
            return None
        return Interview(**record)

    async def update_interview(self, interview: Interview):
        interview.updated_at = interview.updated_at or interview.created_at
        await self.collection.update_one(
            {"interview_id": interview.interview_id},
            {"$set": interview.dict(by_alias=True, exclude_none=True, exclude={"id"})},
        )
        return interview
