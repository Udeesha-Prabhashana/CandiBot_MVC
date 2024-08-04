import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '_5#y2L"F4Q8z\n\xec]/')
    GEMINI_API_ENDPOINT = os.getenv('GEMINI_API_ENDPOINT')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME')
    MONGO_URI = os.getenv('MONGO_URI')
