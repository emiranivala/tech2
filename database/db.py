from pymongo import MongoClient
from pymongo.collection import Collection
from config import DB_URI

class MongoDB:
    """
    A wrapper class for MongoDB operations.
    """
    def __init__(self, db_uri: str, db_name: str, collection_name: str, max_pool_size: int = 50):
        # Create a MongoClient with connection pooling
        self.client = MongoClient(db_uri, maxPoolSize=max_pool_size, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.collection: Collection = self.db[collection_name]
    
    def find_one(self, query: dict) -> dict:
        """
        Finds a single document matching the query.
        """
        return self.collection.find_one(query)
    
    def insert_one(self, document: dict):
        """
        Inserts a document into the collection.
        """
        return self.collection.insert_one(document)
    
    def update_one(self, query: dict, update: dict, upsert: bool = False):
        """
        Updates a single document matching the query.
        """
        return self.collection.update_one(query, update, upsert=upsert)
    
    def delete_one(self, query: dict):
        """
        Deletes a single document matching the query.
        """
        return self.collection.delete_one(query)

# Initialize the database connection for sessions.
database = MongoDB(DB_URI, "userdb", "sessions")
