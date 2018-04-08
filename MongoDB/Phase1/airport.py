from pymongo import MongoClient
from requests import get
import json

client = MongoClient()
db = client['BruttoCluster']

f = open("airports.json", 'r')
data = json.loads(f.read())

base = db.posts.insert_many(data)
