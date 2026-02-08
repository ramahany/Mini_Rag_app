from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne ## this is not the operation this is the discription, away to handle many chunks in batches

class ChunkModel(BaseDataModel): 

    def __init__(self, db_client:object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    
    @classmethod
    async def create_instance(cls, db_client:object): 
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self): 
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections: 
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes: 
                await self.collection.create_index(
                    index["key"],
                    name=index["name"], 
                    unique = index["unique"]
                )
    
    async def create_chunk(self, chunk:DataChunk): 
        record = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = record.inserted_id
        return chunk 
    
    async def get_chunk(self, chunk_id : str): 
        record = await self.collection.find_one({
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

            await self.collection.bulk_write(operations)
        
        return len(chunks)
    
    # deleting all chunks in project using project_id for the doreset = 1 option 
    async def delete_chunks_by_project_id(self, project_id : ObjectId): 
        result = await self.collection.delete_many({
            "chunk_project_id" : project_id
        })

        return result.deleted_count



    
