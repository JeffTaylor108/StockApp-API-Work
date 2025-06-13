import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient


def initialize_mongo_client():
    # get mongo URI from env
    load_dotenv()
    uri = os.getenv("MONGO_URI")

    # create client and connect to server
    client = MongoClient(uri)

    return client