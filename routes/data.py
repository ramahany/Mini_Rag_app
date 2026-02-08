from fastapi import APIRouter, UploadFile, status, Depends, Request
from fastapi.responses import JSONResponse
from controllers import DataController, ProjectController, ProcessController
from helpers.config import get_settings, Settings
from models import ResponseSignal
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel

from models.db_schemes import DataChunk
import aiofiles
import os
import logging


logger = logging.getLogger('uvicorn.error')


data_router = APIRouter(
    prefix='/api/v1/data',
    tags=['api_v1', "data"]
)

# Uploading the file end point 
@data_router.post('/upload/{project_id}')
async def upload_data(request : Request, project_id : str, file : UploadFile,
                      app_settings :Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    data_controller = DataController()
    is_valid, signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid : 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content = {
                "signal" : signal
            }

        )
    proj_dir_path = ProjectController().get_project_dir(project_id=project_id) # this is the dir to store the file
    # file_path = os.path.join(proj_dir_path, file.filename) # while this is the path of the file you want to write
    new_file_path, file_id = data_controller.generate_unique_filepath(orignal_file_name=file.filename, project_id=project_id)


    try:
        async with aiofiles.open(new_file_path, 'wb') as f : # wb writing binary 
            while chunk := await file.read(get_settings().FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk) # writing in the file 1 chunck at a time (better memory use)
    except Exception as e : 
        logger.log(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content = {
                "signal" : ResponseSignal.FILE_UPLOAD_FAILED.value
            }

        )

    return JSONResponse(
            content={
                "signal" : ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file ID" : file_id, 
                # "project_id" : str(project.id)
                }
        )


# processing the file endpoint 
@data_router.post('/process/{project_id}')
async def process_file(request :Request , project_id: str , process_request: ProcessRequest): 
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)


    file_chunks = ProcessController(project_id=project_id).process_file_content(file_id=file_id, 
                                                                                   chunk_size=chunk_size, 
                                                                                   overlap_size=overlap_size)
    
    if file_chunks == None or len(file_chunks) == 0 : 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={
                "signal" : ResponseSignal.FILE_PROCESS_FAILED.value
            }
        )

    
    # loading the chunks in the database

    file_chunks_recordes =[
        DataChunk(
            chunk_text = chunk.page_content,
            chunk_metadata =  chunk.metadata,
            chunk_order = i+1,
            chunk_project_id = project.id 
        )
        for i, chunk in enumerate(file_chunks)
    ]

    del_chunks = None

    if do_reset == 1 : # we did this after we loaded the chunks so that u dont just delete the already existing chunks before hand
        del_chunks = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )


    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_recordes)

    return JSONResponse(
        content={
            "signal" : ResponseSignal.FILE_PROCESS_SUCCESS.value, 
            "inserted_chunks": no_records,
            "deleted_chunks" : del_chunks
        }
    )