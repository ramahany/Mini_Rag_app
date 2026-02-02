from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
from routes import base
import os

app = FastAPI()
app.include_router(base.api_router)
