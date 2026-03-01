from fastapi import FastAPI
from routes import base, data
import os
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    llm_provider_factory = LLMProviderFactory(settings)
    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

    yield

    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

# app = FastAPI()
# old deprecated 
# @app.on_event("startup")
# async def startup_db_client():
#     settings = get_settings()
#     app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
#     app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

# @app.on_event("shutdown")
# async def shutdown_db_client():
#     app.mongo_conn.close()

## another way 
#app.router.lifespan.on_startup.append(startup_function) same for shutdown

app.include_router(base.api_router)
app.include_router(data.data_router)
