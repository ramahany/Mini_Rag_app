from fastapi import APIRouter
import os
api_router = APIRouter(
    prefix="/api/v1", 
    tags=["Base"]
)
@api_router.get('/')
async def welcome(): 
    return {
        "APP_NAME" : os.environ['APP_NAME'],
        "APP_VERSION" : os.environ['APP_VERSION']
    }