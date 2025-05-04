from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
import requests
from WeaveAI.app.util.llm import *
from WeaveAI.app.config import *
import json
from WeaveAI.app.core.content_mgmt import *
#from app.core.llm import llm
#from app.config import *


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/add_resources")
async def add_course_content(request: Request):
    # Input needs to have a list of resources
    # Each array item is of the form {"type":"","url":""}
    try:
        resource_list = await request.json()
        summaries=[]
        for resource in resource_list:
            content=cache_content_youtube(resource["url"],collection_name=db_config.course_content_raw,model=llm_preferences.content_cache_embedding_model)
            summary=generate_summary_with_llm(content=content,model=llm_preferences.course_summarizer_llm)
            summary.append({"resource":resource, "summary":summary})
        cache_summary_content_batch(summary_payload_batch=summaries,collection_name=db_config.course_summaries)
        response_payload={"message":"Successfully Cached Course Content. Ready to generate Course plan"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in method add_course_content(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)

@app.post("/courseplan")
async def create_courseplan(request: Request):
    try:
        summaries=get_all_summaries_content()
        summaries_text=[]
        for summary in summaries:
            summaries_text.append(summary["summary"])
        courseplan=generate_courseplan(course_summaries=summaries_text)
        course_config=create_collection_names(course_config=courseplan)
        save_course_config(course_config)
        response_payload={"message":"Successfully Created Course Plan. Ready to generate Course Content"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in method create_courseplan(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.get("/courseplan")
async def get_courseplan(request: Request):
    try:
        course_config=get_course_config()
        response_payload={"message":"Successfully Fetched Courseplan","data":course_config}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in method get_courseplan(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.post("/content")
async def generate_content(request: Response):
    try:
        generate_all_submodule_content()
        response_payload={"message":"Successfully Created Course Content for all submodules."}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in method generate_content(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    





######################################################################################################################################################################################
   

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




