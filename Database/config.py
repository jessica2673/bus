import datetime, os, secrets
from dotenv import load_dotenv
from Database.crud import *
from pymongo.server_api import ServerApi

load_dotenv()

from pymongo.mongo_client import MongoClient

uri = f"mongodb+srv://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@cluster0.uoprf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.ChatPulse