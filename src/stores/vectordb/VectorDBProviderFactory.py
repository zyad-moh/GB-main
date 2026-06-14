from .provider import QdrantDBProvider
from.VectorDBEnums import VectorDBEnums
from controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self, config):#config to take the config fo DB
        self.config=config
        self.BaseController =BaseController()
    def create(self, provider:str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path=self.BaseController.get_database_path(self.config.VECTOR_DB_PATH)# note that self.config.VECTOR_DB_PATH is refer to the db name npt path
            return QdrantDBProvider(
                
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        return None
