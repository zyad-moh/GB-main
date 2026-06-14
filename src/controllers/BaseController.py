#all controller may want to see app settings (.env,config) , 
#so we will load it in base controller as rest controoler will see it
from helpers.config import get_settings , settings 
import os
import random
import string
# we will but get_settings as a constractor as when base controller is called then the caller (any other controoler ) get acces get_settings
class BaseController():
    
    def __init__(self):
        self.app_settings=get_settings()
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )#path of progect directory
        self.files_dir = os.path.join(self.base_dir,"assets/files")
    
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"# project ->assets -> database
        )

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_database_path(self,db_name):
        database_path=os.path.join(
            self.database_dir,db_name ## project ->assets -> database -> db_name ,,,, db_name come from config VECTOR_DB_path
        )
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path