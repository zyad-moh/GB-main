# for u ploaded file ids to apply process on it 
from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")# _ refer that the object is private sol : make alies
    asset_project_id:ObjectId
    asset_type :str = Field(...,min_length=1) # file or url , three dots mean that field / column is required
    asset_name: str = Field(...,min_length=1)
    asset_size: int = Field(ge=0, defult=None)
    asset_config: dict = Field(default=None)# for future work
    asset_puehed_at:datetime = Field(default=datetime.utcnow) #put the time of creation in mongo db

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return[
            {
                "key":[(
                    "asset_project_id",1
                )],
                "name": "asset_project_id_index_1",
                "unique" :False
            },
            # i need assets with spacific project id and with that spacific name so i need to index the name
            {
                "key":[(
                    "asset_project_id",1
                ),
                ("asset_name",1)
                ],
                "name": "asset_project_id_name_index_1",
                "unique" :True # the index from asset_project_id + asset_name is must be unique
            }
        ]