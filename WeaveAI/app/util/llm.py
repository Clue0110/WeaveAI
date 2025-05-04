from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

import json


from WeaveAI.app.config import *
import os

def get_chunks_from_documents(documents: list, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(documents)
    return chunks

def extract_json_from_llm_response(llm_response,model):
    if model=="google":
        json_text=llm_response[7:-3]
        return json.loads(json_text)
    
def extract_html_from_llm_response(llm_response,model):
    if model=="google":
        html_text=llm_response[8:-3]
        return html_text

class llm:
    def __init__(self, model="llama", collection_name=None):
        self.model=model
        if collection_name is None:
            collection_name = "LLM-"+self.model+"VS"
        self.collection_name=collection_name
        self.vector_store_path=os.path.join(application_config.chroma_db_parent_path,self.collection_name)
        self.initialize_embeddings()
        self.initialize_vectorstore()
        self.initialize_llm()

    def initialize_llm(self):
        if self.model=="llama":
            self.llm_model=OllamaLLM(model="llama3.2")
        if self.model=="google":
            self.llm_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
            #self.llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

    def execute_llm_query(self,template,params=None): #params -> dict for template keys
        if self.model=="llama":
            prompt=ChatPromptTemplate.from_template(template)
            chain=prompt | self.llm_model
            response=chain.invoke(params)
            return response
        if self.model=="google":
            prompt=ChatPromptTemplate.from_template(template)
            chain=prompt | self.llm_model
            response=chain.invoke(params)
            return response.content

    def initialize_embeddings(self):
        if self.model=="llama":
            self.embedding_function=OllamaEmbeddings(model="mxbai-embed-large")
        if self.model=="google":
            gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            self.embedding_function=gemini_embeddings


    def initialize_vectorstore(self):
        self.vector_store=Chroma(collection_name=self.collection_name, 
                                  embedding_function=self.embedding_function, 
                                  persist_directory=self.vector_store_path)
    
    def initialize_retriever(self, search_kwargs=None, search_type=None):
        if search_kwargs is None:
            search_kwargs={
                "k":10
                #"score_threshold":0.5,
                #"fetch_k":20,
                #"filter":None,
            }
        if search_type is None:
            search_type="similarity"
        
        self.retriever=self.vector_store.as_retriever(search_kwargs=search_kwargs, search_type=search_type)

    def fetch_data(self, query):
        if self.retriever is None:
            self.initialize_retriever()
        fetched_data=self.retriever.invoke(input=query)
        return fetched_data
        
    def add_to_vectorstore(self,documents=None):
        self.vector_store.add_documents(documents=documents)

    