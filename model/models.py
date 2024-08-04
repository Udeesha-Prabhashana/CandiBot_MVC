from pymongo import MongoClient, errors
from pymongo.server_api import ServerApi
import os
import certifi
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Load environment variables for database configuration
DATABASE_NAME = os.getenv('DATABASE_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
MONGO_URI = os.getenv('MONGO_URI')

# Create a MongoDB client with SSL/TLS configuration
client = MongoClient(
    MONGO_URI,
    server_api=ServerApi('1'),  # Use Server API version 1
    serverSelectionTimeoutMS=5000,  # Timeout for server selection
    tls=True,  # Enable TLS (SSL)
    tlsCAFile=certifi.where()  # Path to CA certificates for TLS
)

# Access the specified database and collection
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

class ScoreDocument:
    def __init__(self, name, score, HR_questions):
        # Initialize a ScoreDocument instance
        self.name = name
        self.score = score
        self.HR_questions = HR_questions
    
    def to_dict(self):
        # Convert the ScoreDocument instance to a dictionary
        return {
            'name': self.name,
            'score': self.score,
            'HR_questions': self.HR_questions
        }
    
    @staticmethod
    def insert(document):
        # Insert a ScoreDocument instance into the MongoDB collection
        try:
            collection.insert_one(document.to_dict())
            print("Database insert successful")  # Log success message
        except Exception as e:
            print(f"Database insert failed: {e}")  # Log error message

    @staticmethod
    def get_all():
        # Retrieve all documents from the MongoDB collection
        try:
            return list(collection.find())
        except Exception as e:
            print(f"Database query failed: {e}")  # Log error message
            return []  # Return an empty list if query fails
