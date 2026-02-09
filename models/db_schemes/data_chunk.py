from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel): 
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict 
    chunk_order : int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id : ObjectId


    class Config: # so the ObjectId type wont be causing problems 
        arbitrary_types_allowed = True

    
    @classmethod # indexing to search through chunks with x project id
    def get_indexes(cls): 
        return[{
            "key":[
                ("chunk_project_id", 1)
            ], 
            "name": "chunk_project_id_index_1", 
            "unique": False # cause mult chunks can have the same project id
        }]
