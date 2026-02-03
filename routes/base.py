from fastapi import APIRouter, Depends
from helpers.config import get_settings, Settings
api_router = APIRouter(
    prefix="/api/v1", 
    tags=["Base"]
)

@api_router.get('/')
async def welcome(app_settings : Settings = Depends(get_settings)): 
    return {
        "APP_NAME" : app_settings.APP_NAME,
        "APP_VERSION" : app_settings.APP_VERSION
    }