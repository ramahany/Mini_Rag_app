from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging

class QdrantDB(VectorDBInterface): 
    def __init__(self, db_path:str, distance_method:str):
        self.client = None
        self.db_path = db_path
        self.distance_method = None

        if distance_method == DistanceMethodEnums.COSINE.value : 
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value : 
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__) # class logger

    
    def connect(self):
        self.client = QdrantClient(path=self.db_path)
    
    def disconnect(self):
        self.client = None
    
    def is_collection_existed(self, collection_name):
        if not self.client: 
            self.logger.error("Client Is Not Connected")
            raise ConnectionError
        
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self):
        if not self.client: 
            self.logger.error("Client Is Not Connected")
            raise ConnectionError
        
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name):
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name):

        if self.is_collection_existed(collection_name=collection_name):
            return self.client.delete_collection(collection_name=collection_name)
    
    def create_collection(self, collection_name, embedding_size, do_reset = False):
        if do_reset:
            self.delete_collection(collection_name=collection_name)

        if not self.is_collection_existed(collection_name=collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                            size=embedding_size, 
                            distance=self.distance_method
                        )
                    )
            return True
        
        return False
    
    def insert_one(self, collection_name, text, vector, metadata = None, record_id = None):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Cannot insert into non existing collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id = record_id,
                        vector=vector,
                        payload={
                            "text": text, "metadata":metadata
                        }
                    )
                ]
            )
        except Exception as e: 
            self.logger.error(f"error while inserting one => {e}")
            return False
        return True

    def insert_many(self, collection_name, texts, vectors, metadata = None, record_ids = None, batch_size = 50):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Cannot insert into non existing collection: {collection_name}")
            return False
        
        if not metadata:
            metadata = [None] * len(vectors)

        for i in range(0, len(vectors), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            payloads = []
            for x in range(len(batch_texts)): 
                payloads.append({
                    "text": batch_texts[x], "metadata" : batch_metadata[x]
                })
            try:
                _ = self.client.upsert(
                    collection_name=collection_name,
                    points= models.Batch(
                        ids=record_ids[i:i+batch_size],
                        payloads=payloads,
                        vectors=vectors[i:i+batch_size]
                    )
                )
            except Exception as e: 
                self.logger.error(f"error while inserting batch => {e}")
                return False

        return True
    
    def search_by_vector(self, collection_name, vector, limit = 5):
        if not self.is_collection_existed(collection_name=collection_name):
            self.logger.error(f"Cannot insert into non existing collection: {collection_name}")
            return False
       
        return self.client.query_points(
            collection_name=collection_name,
            query=vector,
            with_payload=True,
            with_vectors=True,
            limit=limit
        )


        
    
    
    

    


        