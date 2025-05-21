import json
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
if not mongodb_uri:
    raise Exception("MONGODB_URI not set in environment")

client = MongoClient(mongodb_uri)
db = client["LibraryManager"]

def load_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

db.books.insert_many(load_json("mongodb/books.json"))
db.customers.insert_many(load_json("mongodb/customers.json"))
db.borrows.insert_many(load_json("mongodb/borrows.json"))
db.authors.insert_many(load_json("mongodb/authors.json"))
db.publishers.insert_many(load_json("mongodb/publishers.json"))
db.genres.insert_many(load_json("mongodb/genres.json"))

print("Data seeded successfully.")
