from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne ## this is not the operation this is the discription, away to handle many chunks in batches

class ChunkModel(BaseDataModel): 

    def __init__(self, db_client):
        super().__init__(db_client=db_client)
        self.connection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
    
    async def create_chunk(self, chunk:DataChunk): 
        record = await self.connection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = record.inserted_id
        return chunk 
    
    async def get_chunk(self, chunk_id : str): 
        record = await self.connection.find_one({
            "id" : ObjectId(chunk_id)
        })

        return None if record is None else DataChunk(**record)
    
    # load chunks in batches (memo efficient), instead of using insert_many using mongo
    async def insert_many_chunks(self, chunks: list, batch_size : int = 100): 
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.connection.bulk_write(operations)
        
        return len(chunks)
    
    # deleting all chunks in project using project_id for the doreset = 1 option 
    async def delete_chunks_by_project_id(self, project_id : ObjectId): 
        result = await self.connection.delete_many({
            "chunk_project_id" : project_id
        })

        return result.deleted_count



    
