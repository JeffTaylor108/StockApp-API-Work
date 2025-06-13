import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

# get mongo URI from env
load_dotenv()
uri = os.getenv("MONGO_URI")

# create client and connect to server
client = MongoClient(uri)

def insert_document():
    collection = client.sample_guides.planets
    test_doc = {
        "name": "new planet",
        "orderFromSun": 100,
        "hasRings": True
    }
    collection.insert_one(test_doc)

    documents = collection.find({})
    for document in documents:
        print(document)

try:
    collections = client.sample_guides.list_collection_names()
    print(collections)

    # insert_document()

except Exception as e:
    print(e)