import pymongo
from WeaveAI.app.config import db_config
from langchain_core.documents import Document

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


