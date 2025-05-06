from fastapi import FastAPI, HTTPException, Response, status, Request, File, UploadFile
from pydantic import BaseModel
import requests
from WeaveAI.app.util.llm import *
from WeaveAI.app.config import *
import json
import io
from WeaveAI.app.core.content_mgmt import *
from WeaveAI.app.core.chatbot import *
import logging
from fastapi.responses import StreamingResponse, FileResponse
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS

import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}


@app.post("/add_resources")
async def add_course_content(request: Request):
    # Input needs to have a list of resources
    # Each array item is of the form {"type":"","url":""}
    try:
        resources = await request.json()
        summaries=[]
        for resource in resources["resource_list"]:
            content=cache_content_youtube(resource["url"],collection_name=db_config.course_content_raw,model=llm_preferences.content_cache_embedding_model)
            summary=generate_summary_with_llm(content=content,model=llm_preferences.course_summarizer_llm)
            summaries.append({"resource":resource, "summary":summary})
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
    
@app.post("/setup_course")
async def setup_course(request: Request):
    try:
        course_config=get_course_config()
        course_config.pop("_id",None)
        categorize_course_content(course_config=course_config)
        response_payload={"message":"Successfully Fetched Courseplan","data":course_config}
    except Exception as e:
        response_payload={"message":f"Exception in method create_courseplan(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.get("/courseplan")
async def get_courseplan(request: Request):
    try:
        course_config=get_course_config() #Debug
        course_config.pop("_id",None)
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
    
@app.get("/content")
async def get_submodule_content(request: Request):
    try:
        request_payload=await request.json()
        module=request_payload["module"]
        submodule=request_payload["submodule"]
        module_code=f"content_{module}_{submodule}"
        content=fetch_submodule_content(module_code)
        print(content)
        response_payload={"message":"Succesfully Retrieved Submodule Payload",
                          "content":content}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in get__submodule_content(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.post("/quiz")
async def generate_quiz(request: Request):
    try:
        request_payload=await request.json()
        module=request_payload["module"]
        submodule=request_payload["submodule"]
        print("Here1")
        save_quiz=request_payload["save"]
        print("Here2")
        module_code=f"quiz_{module}_{submodule}"
        print("Here3")
        course_config=get_course_config()
        course_config.pop("_id",None)
        print("Here4")
        collection_name=course_config[str(module)]["submodules"][str(submodule)]["mongo_db_details"]["collection_name"]
        print("Here5")
        quiz_content=generate_submodule_quiz(mdb_collection_name=collection_name)
        print(f"Generated Submodule Quiz for {module_code}")
        if save_quiz==True:
            save_submodule_quiz(module_code=module_code, json_content=quiz_content)
            print(f"Saved Quiz: {module_code}")
        response_payload={"message":"Succesfully Retrieved Submodule Quiz",
                          "content":quiz_content,
                          "save":save_quiz}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in generate_quiz(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.get("/quiz")
async def get_quiz(request: Request):
    try:
        request_payload=await request.json()
        module=request_payload["module"]
        submodule=request_payload["submodule"]
        module_code=f"quiz_{module}_{submodule}"
        quiz_content=get_submodule_quiz(module_code=module_code)
        response_payload={"message":"Succesfully Retrieved Submodule Quiz",
                          "content":quiz_content}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in get_quiz(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)

@app.get("/podcast")
async def get_podcast_script(request: Request):
    try:
        request_payload=await request.json()
        module=request_payload["module"]
        submodule=request_payload["submodule"]
        module_code=f"podcast_{module}_{submodule}"
        course_config=get_course_config()
        collection_name=course_config[str(module)]["submodules"][str(submodule)]["mongo_db_details"]["collection_name"]
        podcast_content=generate_podcast_episode(module=module,sub_module=submodule,mdb_collection_name=collection_name)
        response_payload={"message":"Succesfully Retrieved Submodule Quiz",
                          "content":podcast_content}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in get_quiz(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)
    
@app.get("/chatbot")
async def get_chatbot_response(request: Request):
    try:
        request_payload=await request.json()
        #print(request_payload,type(request_payload))
        query=request_payload["query"]
        query_response=answer_course_query(query=query, with_history=True)
        response_payload={"message":"Succesfully Retrieved Response From Chatbot",
                          "response":query_response}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        response_payload={"message":f"Exception in get_chatbot_response(). Error: {e}"}
        return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=500)

def transcribe_audio(audio_bytes: bytes, language: str = "en-US") -> str:
    """
    Transcribes audio bytes to text using SpeechRecognition.
    Handles audio format conversion using pydub.
    """
    recognizer = sr.Recognizer()
    try:
        # Load audio data from bytes using pydub
        # This automatically detects the format (wav, mp3, ogg, etc. if ffmpeg is installed)
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Export to WAV format in memory, as Recognizer prefers WAV
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0) # Reset buffer position to the beginning

        # Use the WAV data with SpeechRecognition AudioFile
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source) # Read the entire audio file

        # Recognize speech using Google Web Speech API (requires internet)
        # Other engines like recognize_whisper (offline, needs setup) or
        # recognize_sphinx (offline, less accurate) can be used.
        logger.info(f"Attempting to transcribe audio using Google Web Speech API (language: {language})...")
        text = recognizer.recognize_google(audio_data, language=language)
        logger.info(f"Transcription successful: {text}")
        return text

    except sr.UnknownValueError:
        logger.error("Speech Recognition could not understand audio")
        raise HTTPException(status_code=400, detail="Could not understand audio")
    except sr.RequestError as e:
        logger.error(f"Could not request results from Speech Recognition service; {e}")
        raise HTTPException(status_code=503, detail=f"Speech Recognition service unavailable: {e}")
    except Exception as e:
        # Catch other potential errors (e.g., pydub format issues)
        logger.error(f"Error during audio processing or transcription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")
    
def synthesize_speech(text: str, language: str = "en") -> io.BytesIO:
    """
    Converts text to speech audio bytes (MP3 format) using gTTS.
    """
    try:
        logger.info(f"Synthesizing speech for text: {text} (language: {language})")
        tts = gTTS(text=text, lang=language, slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0) # Rewind the buffer
        logger.info("Speech synthesis successful.")
        return audio_fp
    except Exception as e:
        logger.error(f"Error during speech synthesis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to synthesize speech: {e}")

@app.post("/chatbot")
async def get_chatbot_voice_response(
    request: Request, # Access request details if needed (e.g., headers)
    audio_file: UploadFile = File(..., description="Voice note file (e.g., wav, mp3, m4a)")):

    try:
        audio_bytes = await audio_file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Received empty audio file.")
        logger.info(f"Read {len(audio_bytes)} bytes from uploaded file.")
    except Exception as e:
        logger.error(f"Error reading upload file: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error reading audio file: {e}")
    finally:
        await audio_file.close() # Ensure file handle is closed

    transcribed_text = transcribe_audio(audio_bytes, language="en-US") # Example language

    try:
        llm_response_text = answer_course_query(query=transcribed_text, with_history=True)
        if not llm_response_text:
             # Handle cases where LLM gives no response gracefully
             logger.warning("LLM returned an empty response.")
             # Decide how to handle: maybe synthesize a default message?
             llm_response_text = "I don't have a response for that right now."
             # Or raise an error:
             # raise HTTPException(status_code=500, detail="LLM failed to generate a response.")
    except Exception as e:
        logger.error(f"Error getting response from LLM function: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM interaction failed: {e}")
    
    response_audio_fp = synthesize_speech(llm_response_text, language="en")
    logger.info("Streaming synthesized audio response.")
    return StreamingResponse(
        response_audio_fp,
        media_type="audio/mpeg", # gTTS produces MP3
        headers={
            # Optional: Suggest a filename to the client
            'Content-Disposition': 'inline; filename="response.mp3"'
        }
    )

@app.post("/podcast")
async def post_podcast(request: Request):
    try:
        request_payload=await request.json()
        module=request_payload["module"]
        submodule=request_payload["submodule"]
        module_code=f"podcast_{module}_{submodule}"
        course_config=get_course_config()
        collection_name=course_config[module]["submodules"][submodule]["mongo_db_details"]
        podcast_path=create_podcast(module=module,sub_module=submodule,mdb_collection_name=collection_name)

        logger.info(f"File found. Sending '{podcast_path}'...")
        return FileResponse(
            path=podcast_path,
            media_type='audio/mpeg', # Explicitly set MIME type for robustness
            filename=os.path.basename(podcast_path) # Sets the filename in Content-Disposition header
            # Optional: Control Content-Disposition more explicitly if needed
            # headers={"Content-Disposition": f"attachment; filename={os.path.basename(PODCAST_FILE_PATH)}"} # Force download
            # headers={"Content-Disposition": f"inline; filename={os.path.basename(PODCAST_FILE_PATH)}"} # Suggest inline playback
        )
        #return Response(content=json.dumps(response_payload, indent=4), media_type="application/json", status_code=200)
    except Exception as e:
        logger.error(f"Error in post_podcast(): {e}")
        raise HTTPException(status_code=500, detail=f"Server Error: {e}")

######################################################################################################################################################################################





