from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
import requests
from WeaveAI.app.util.llm import *
from WeaveAI.app.config import *
import json
#from app.core.llm import llm
#from app.config import *


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/add_course_content_resource")
def add_course_content(request: Request):
    pass
   

@app.get("/tailor_questionnaire")
def get_tailor_questionnaire():
    llm_query=predefined_prompts.prompt1
    data_retrieval_query=predefined_prompts.prompt2
    gemini_llm=llm(model="google")
    gemini_llm.initialize_retriever(search_kwargs={"k":1000000})
    context=gemini_llm.fetch_data(data_retrieval_query)
    # Executing LLM Query
    llm_response=gemini_llm.execute_llm_query(template=llm_query,params={"context":str(context)})
    # Extract QA JSON from LLM Response
    qa_json=extract_json_from_llm_response(llm_response,"google")
    
    # Send the QA JSON to UI
    http_response={"message":qa_json}
    #return http_response
    return Response(content=json.dumps(http_response,indent=4), media_type="application/json")

@app.post("/tailor_questionnaire")
async def store_tailor_questionnaire(request: Request):
    #Read the JSON from POST payload
    qa_json= await request.json()

    #Store this QA json in database
    with open("questionnaire.json", "w") as json_file:
        json.dump(qa_json, json_file, indent=4)
    
    return {"message": "Questionnaire saved successfully.", "data": qa_json}

@app.get("/questionnaire")
def get_questionnaire():
    with open("questionnaire.json", "r") as json_file:
        data = json.load(json_file)
    return data

@app.get("/generate_courseplan")
def generate_courseplan():
    # get the QA content from database
    with open("questionnaire.json", "r") as json_file:
        qa_data = json_file.read()

    data_retrieval_query=predefined_prompts.prompt3
    gemini_llm=llm(model="google")
    gemini_llm.initialize_retriever(search_kwargs={"k":1000000})
    context=gemini_llm.fetch_data(data_retrieval_query)

    llm_query=predefined_prompts.prompt4
    llm_response=gemini_llm.execute_llm_query(template=llm_query,params={"context":str(context),"qa_data":str(qa_data),"time":"5"})
    #Extract json from LLM Response
    course_plan_json=extract_json_from_llm_response(llm_response,"google")
    #Store this course plan JSON in database
    with open("courseplan.json", "w") as json_file:
        json.dump(course_plan_json, json_file, indent=4)
    #Send the JSON to UI
    return Response(content=json.dumps(course_plan_json,indent=4), media_type="application/json")

@app.get("/courseplan")
def get_courseplan():
    # get the course plan content from database
    # Send the JSON to UI

    with open("courseplan.json", "r") as json_file:
        data = json.load(json_file)
    return data




