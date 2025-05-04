import pymongo
import redis
from WeaveAI.app.config import db_config
from langchain_core.documents import Document
import json

class mongo_db:
    def __init__(self, db_name=db_config.mongo_db_name):
        self.uri = db_config.mongo_db_uri
        self.db_name = db_name
        self._connect()

    def _connect(self):
        try:
            self.client=pymongo.MongoClient(self.uri)
            self.client.admin.command('ping')
            self.db=self.client[self.db_name]
            print(f"Using MongoDB Database: {self.db_name}")
        except Exception as e:
            print(f"Error in mongo_db._connect() connecting to MongoDB: {e}")
            self.client = None
            self.db = None
            raise e
        
    def validate_connection(self):
        if self.db is None:
            print("Database connection not established.")
            return False
        return True
        
    def convert_langchain_doc_to_json(self, document: Document):
        json_document={
            "page_content": document.page_content,
            "metadata": document.metadata
        }
        return json_document
    
    def convert_json_to_langchain_doc(self, json_document):
        document= Document(
            page_content=json_document.get("page_content", ""),
            metadata=json_document.get("metadata", {})
        )
        return document
    
    def add_langchain_document(self, collection_name: str, document: Document):
        json_document=self.convert_langchain_doc_to_json(document)
        try:
            result= self.add_json(collection_name, json_document)
            return result
        except Exception as e:
            print(f"Error in mongo_db.add_langchain_document() adding document: {e}")
            raise e
    
    def add_json(self, collection_name, json_document):
        if not self.validate_connection():
            return None
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(json_document)
            return result.inserted_id
        except Exception as e:
            print(f"Error in mongo_db.add_json() inserting document: {e}")
            raise None
        
    def add_langchain_documents_batch(self, collection_name, documents):
        json_documents=[]
        for document in documents:
            json_document=self.convert_langchain_doc_to_json(document)
            json_documents.append(json_document)
        try:
            result = self.add_json_batch(collection_name, json_documents)
            return result
        except Exception as e:
            print(f"Error in mongo_db.add_documents_batch() adding documents: {e}")
            raise e
    
    def add_json_batch(self, collection_name, json_documents):
        if not self.validate_connection():
            return None
        try:
            collection = self.db[collection_name]
            result=collection.insert_many(json_documents)
            return result.inserted_ids
        except Exception as e:
            print(f"Error in mongo_db.add_documents_batch() inserting documents: {e}")
            raise None
        
    def get_all_langchain_documents(self, collection_name, with_ids=False):
        try:
            result = self.get_all_json_documents(collection_name)
            if result is None:
                return None
            lanchain_documents = []
            for json_document in result:
                document = self.convert_json_to_langchain_doc(json_document)
                if with_ids:
                    lanchain_documents.append({"id": str(json_document.get("_id")), "document": document})
                else:
                    lanchain_documents.append(document)
            return lanchain_documents
        except Exception as e:
            print(f"Error in mongo_db.get_all_langchain_documents() retrieving documents: {e}")
            raise None
    
    def get_json_documents_with_filter(self, collection_name, filter):
        """
        Fetches documents from a specified MongoDB collection based on a filter.

        Args:
            collection_name: The name of the collection to query within the database.
            filter: A dictionary specifying the query criteria (e.g., {"field": "value"}).
                    An empty dictionary {} will match all documents in the collection.

        Returns:
            A list of documents (as dictionaries) matching the filter criteria.
            Returns an empty list if no documents match the filter.
            Returns None if a connection error or operation failure occurs.
        """
        if not self.validate_connection():
            return None
        try:
            collection = self.db[collection_name]
            document_cursor=collection.find(filter)
            documents_list=list(document_cursor)
            return documents_list
        except Exception as e:
            print(f"Error in mongo_db.get_json_documents_with_filter() retrieving documents: {e}")
            raise None
    
    def get_all_json_documents(self, collection_name):
        if not self.validate_connection():
            return None
        try:
            collection = self.db[collection_name]
            document_cursor=collection.find()
            documents_list = list(document_cursor)
            print(f"Retrieved {len(documents_list)} documents from collection '{collection_name}'.")
            return documents_list
        except Exception as e:
            print(f"Error in mongo_db.get_all_documents() retrieving documents: {e}")
            raise None

    def delete_one_document(self, collection_name, id=None,name=None):
        if not self.validate_connection():
            return None
        if id is not None:
            filter_query = {"_id": pymongo.ObjectId(id)}
        elif name is not None:
            filter_query = {"name": name}
        else:
            print("Either 'id' or 'name' must be provided to delete a document.")
            return None

        try:
            collection = self.db[collection_name]
            result = collection.delete_one(filter_query)
            return result.deleted_count
        except Exception as e:
            print(f"Error in mongo_db.delete_one_document() deleting document: {e}")
            raise None
        
    def delete_all_langchain_documents(self, collection_name):
        try:
            result=self.delete_all_json_documents(collection_name)
            return result
        except Exception as e:
            print(f"Error in mongo_db.delete_all_langchain_documents() deleting documents: {e}")
            raise None
    
    def delete_all_json_documents(self, collection_name):
        if not self.validate_connection():
            return None
        try:
            collection = self.db[collection_name]
            result = collection.delete_many({})
            print(f"Deleted {result.deleted_count} documents from collection '{collection_name}'.")
            return result.deleted_count
        except Exception as e:
            print(f"Error in mongo_db.delete_all_documents() deleting documents: {e}")
            raise None
        
    def delete_collection(self, collection_name):
        if not self.validate_connection():
            return None
        try:
            if collection_name in self.db.list_collection_names():
                self.db.drop_collection(collection_name)
                print(f"Successfully deleted collection: '{collection_name}'.")
            else:
                print(f"Collection '{collection_name}' does not exist.")
        except Exception as e:
            print(f"Error in mongo_db.delete_collection() deleting collection: {e}")
            raise None
        
    def close_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")
        else:
            print("No MongoDB connection to close.")


class redis_db:
    def __init__(self):
        """
        Initializes the Redis connection.

        Args:
            host (str): Redis server host. Defaults to 'localhost'.
            port (int): Redis server port. Defaults to 6379.
            db (int): Redis database number. Defaults to 0.
            password (str, optional): Password for Redis authentication. Defaults to None.
            decode_responses (bool): Whether to decode responses from Redis (e.g., bytes to strings).
                                     Defaults to True for easier handling of string data.
        """
        self.host = db_config.redis_host
        self.port = db_config.redis_port
        self.db = db_config.redis_db
        self.password = db_config.redis_password
        self.decode_responses = db_config.redis_decode_responses
        self.client = None
        self._connect()

    def _connect(self):
        """Establishes the connection to the Redis server."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_timeout=5 # Add a timeout for connection attempts
            )
            # Test the connection
            self.client.ping()
            print(f"Successfully connected to Redis at {self.host}:{self.port}, DB: {self.db}")
        except Exception as e:
            print(f"An unexpected error occurred during connection: {e}")
            self.client = None

    def is_connected(self) -> bool:
        """Checks if the client is connected to Redis."""
        if not self.client:
            return False
        try:
            return self.client.ping()
        except redis.exceptions.ConnectionError:
            return False
        
    def create(self, key: str, value, use_json: bool = False) -> bool:
        """
        Creates a new key-value pair in Redis.
        If the key already exists, its value will be overwritten.

        Args:
            key (str): The key to store the data under.
            value: The value to store. Can be string, bytes, int, float.
                   If use_json is True, it can be a dict or list.
            use_json (bool): If True, serialize 'value' to JSON before storing.
                             Defaults to False.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if not self.is_connected():
            print("Error: Not connected to Redis.")
            return False
        try:
            data_to_store = json.dumps(value) if use_json else value
            return self.client.set(key, data_to_store)
        except TypeError as e:
            print(f"Error: Could not serialize value for key '{key}'. Ensure it's JSON serializable if use_json=True. Error: {e}")
            return False
        except Exception as e:
            print(f"Error in redis_db.create(): {e}")
            return False
        
    def read(self, key: str, parse_json: bool = False):
        """
        Reads the value associated with a key from Redis.

        Args:
            key (str): The key whose value needs to be retrieved.
            parse_json (bool): If True, attempt to parse the retrieved value as JSON.
                               Defaults to False.

        Returns:
            The value associated with the key, or None if the key doesn't exist
            or an error occurred. If parse_json is True and successful, returns
            the parsed Python object (dict/list).
        """
        if not self.is_connected():
            print("Error: Not connected to Redis.")
            return None
        try:
            value = self.client.get(key)
            if value is None:
                # Key doesn't exist, which is not an error state
                return None

            if parse_json:
                try:
                    # Assumes decode_responses=True was used in init
                    return json.loads(value)
                except json.JSONDecodeError:
                    print(f"Warning: Value for key '{key}' is not valid JSON, returning as string.")
                    return value # Return raw value if JSON parsing fails
            else:
                # Value is already decoded to string if decode_responses=True
                # If decode_responses=False, value would be bytes here
                return value
        except Exception as e:
            print(f"Error: redis_db.read(), Error reading key '{key}': {e}")
            return None
        
    def update(self, key: str, value, use_json: bool = False) -> bool:
        """
        Updates the value for an existing key.
        Note: In Redis, SET performs an overwrite, so this is functionally
              identical to create(). This method is provided for semantic clarity.
              You could add a check to ensure the key exists first if needed.

        Args:
            key (str): The key whose value needs to be updated.
            value: The new value to store.
            use_json (bool): If True, serialize 'value' to JSON. Defaults to False.


        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        # create directly overwrites thekey if it exists, so its fine
        return self.create(key, value, use_json=use_json)
    
    def delete(self, key: str) -> bool:
        """
        Deletes a key-value pair from Redis.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if the key was deleted, False if the key didn't exist or an error occurred.
        """
        if not self.is_connected():
            print("Error: Not connected to Redis.")
            return False
        try:
            # DEL returns the number of keys deleted (0 or 1 in this case)
            deleted_count = self.client.delete(key)
            return deleted_count > 0
        except Exception as e:
            print(f"Error: redis_db.delete(), Error deleting key '{key}': {e}")
            return False
        
    def exists(self, key: str) -> bool:
        """
        Checks if a key exists in Redis.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise or if disconnected.
        """
        if not self.is_connected():
            print("Error: Not connected to Redis.")
            return False
        try:
            # EXISTS returns the number of keys that exist (0 or 1 here)
            return self.client.exists(key) > 0
        except Exception as e:
            print(f"Error checking existence for key '{key}': {e}")
            return False
        
    def set_with_ttl(self, key: str, value, ttl_seconds: int, use_json: bool = False) -> bool:
        """
        Sets a key-value pair with a Time-To-Live (TTL) in seconds.
        The key will automatically expire after ttl_seconds.

        Args:
            key (str): The key to store.
            value: The value to store.
            ttl_seconds (int): The time-to-live in seconds.
            use_json (bool): If True, serialize 'value' to JSON. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_connected():
            print("Error: Not connected to Redis.")
            return False
        try:
            data_to_store = json.dumps(value) if use_json else value
            # Use setex for simplicity if value is string/bytes
            # Or use set with ex parameter for more general types
            # return self.client.setex(key, ttl_seconds, data_to_store)
            return self.client.set(key, data_to_store, ex=ttl_seconds)
        except TypeError as e:
             print(f"Error: Could not serialize value for key '{key}'. Ensure it's JSON serializable if use_json=True. Error: {e}")
             return False
        except Exception as e:
            print(f"Error in redis_db.set_with_ttl, Error setting key '{key}' with TTL: {e}")
            return False
        
    def close_connection(self):
        """Closes the Redis connection if it's open."""
        if self.client:
            try:
                self.client.close()
                print("Redis connection closed.")
                self.client = None
            except Exception as e:
                print(f"Error closing Redis connection: {e}")
