from fastapi import APIRouter, UploadFile, status, Depends
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController
from helpers.config import get_settings, Settings
from models import ResponseSignal
import aiofiles
import os

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1', "data"]
)

@data_router.get('/upload/{project_id}')
async def upload_data(project_id : str, file : UploadFile,
                      app_settings :Settings = Depends(get_settings)):

    is_valid, signal = DataController().validate_uploaded_file(file=file)

    if not is_valid : 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content = {
                "signal" : signal
            }

        )
    proj_dir_path = ProjectController().get_project_dir(project_id=project_id) # this is the dir to store the file
    file_path = os.path.join(proj_dir_path, file.filename) # while this is the path of the file you want to write


    async with aiofiles.open(file_path, 'wb') as f : # wb writing binary 
        while chunk := await file.read(get_settings().FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk) # writing in the file 1 chunck at a time (better memory use)

    return JSONResponse(
            content={
                "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value
                }
        )
