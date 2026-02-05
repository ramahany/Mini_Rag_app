from fastapi import FastAPI
from routes import base, data
import os
from helpers.config import get_settings
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

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
    

app.include_router(base.api_router)
app.include_router(data.data_router)
