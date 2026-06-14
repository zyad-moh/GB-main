from pymongo.errors import DuplicateKeyError

from .BaseDataModel import BaseDataModel
from .db_schemes import ProcessedEmail
from .enums.DataBaseEnum import DataBaseEnum


class ProcessedEmailModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROCESSED_EMAIL_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        collection_names = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROCESSED_EMAIL_NAME.value not in collection_names:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROCESSED_EMAIL_NAME.value]

        for index in ProcessedEmail.get_indexes():
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"],
            )

    async def is_processed(self, message_id: str) -> bool:
        record = await self.collection.find_one({"message_id": message_id}, {"_id": 1})
        return record is not None

    async def mark_processed(self, processed_email: ProcessedEmail) -> bool:
        try:
            await self.collection.insert_one(
                processed_email.dict(by_alias=True, exclude_none=True, exclude={"id"})
            )
            return True
        except DuplicateKeyError:
            return False

    async def count_processed(self) -> int:
        return await self.collection.count_documents({})
