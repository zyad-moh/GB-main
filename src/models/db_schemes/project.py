from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
#مواصفات لشكل الداتا هتكون عاملة ازاى
class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")# _ refer that the object is private sol : make alies
    project_id: str = Field(..., min_length=1)
    email:str = Field(..., min_length=1)
    password:str = Field(..., min_length=1)
    role:str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[("project_id",1)], # we make list as we could include one or more key  project_id ia the field or column we will apply indedxing on it 1 -> desc
                "name": "project_id_index_1",
                "unique": True # project id must be unique

            }
        ]