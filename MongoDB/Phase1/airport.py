from pymongo import MongoClient
import json

client = MongoClient()
db = client['airports']

f = open("airports.json", 'r')
data = json.loads(f.read())

base = db.location.insert(data)
