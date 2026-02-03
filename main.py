from fastapi import FastAPI
from routes import base, data
import os

app = FastAPI()
app.include_router(base.api_router)
app.include_router(data.data_router)
