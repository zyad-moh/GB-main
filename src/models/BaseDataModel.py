from helpers.config import get_settings,settings
class BaseDataModel:
    def __init__(self,db_client:object):
        self.db_client=db_client # Here, db_client is an object that allows you to interact with your database
        self.app_settings=get_settings

   