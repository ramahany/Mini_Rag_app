from fastapi import APIRouter, UploadFile
from controllers import DataController

data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1', "data"]
)

@data_router.get('/upload/{project_id}')
async def upload_data(project_id : str, file : UploadFile):
    data_controller = DataController()
    is_valid, msg = data_controller.validate_uploaded_file(file=file)
    return {
        "ID" : project_id,
        "Status" : 200 if is_valid else 400,
        "msg" : msg
    }

