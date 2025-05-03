from WeaveAI.app.util.video_utils import youtube_extract_transcript
from WeaveAI.app.util.llm import *
from WeaveAI.app.config import *
from WeaveAI.app.util.db_utils import *

def cache_content_youtube(url: str, collection_name: str, model: str):
    #video_transcript=youtube_extract_transcript(url)
    video_transcript=open("C:/Akilesh/Exp Lab/BuddyAI/transcript.txt","r").read()
    chunks=get_chunks_from_documents([Document(page_content=video_transcript, metadata={"source": url})])
    #Insert the chunks into the MongoDB Database
    try:
        db_conn=mongo_db()
        db_conn.add_langchain_documents_batch(
            collection_name=collection_name, 
            documents=chunks
        )
        db_conn.close_connection()
    except Exception as e:
        print(f"Error: cache_content_youtube() in caching content to MongoDB: {e}")
        return None
    #Insert the chunks into the Vector Database
    llm_model=llm(model=model, collection_name=collection_name)
    llm_model.add_to_vectorstore(documents=chunks)
    return video_transcript

def generate_summary_with_llm(content: str, model: str):
    #Generating Summary
    llm_model=llm(model=model)
    #Prompt for Summary Generation
    summary_prompt=predefined_prompts.generate_summary_prompt
    video_summary=llm_model.execute_llm_query(template=summary_prompt, params={"context": content})
    return video_summary

def cache_summary_content(summary_payload: json, collection_name: str):
    """
    Cache the summary content into the MongoDB database.
    :param summary: The summary content to cache.
    :param collection_name: The name of the collection in MongoDB.
    :return: A dictionary containing the summary and collection name.
    """
    # TEST: Insert the summary into the MongoDB Database
    try:
        db_conn = mongo_db()
        db_conn.add_json(collection_name=collection_name,json_document=summary_payload)
        db_conn.close_connection()
    except Exception as e:
        print(f"Error: cache_summary_content() in caching content to MongoDB: {e}")
        return None
    
def cache_summary_content_batch(summary_payload_batch: list, collection_name: str):
    """
    Cache multiple summary content into the MongoDB database.
    :param summary: The summary content to cache.
    :param collection_name: The name of the collection in MongoDB.
    :return: A dictionary containing the summary and collection name.
    """
    # TEST: Insert the summary into the MongoDB Database
    try:
        db_conn = mongo_db()
        db_conn.add_json_batch(collection_name=collection_name,json_documents=summary_payload_batch)
        db_conn.close_connection()
    except Exception as e:
        print(f"Error: cache_summary_content_batch() in caching content to MongoDB: {e}")
        return None

def generate_courseplan(course_summaries: list, model: str):
    """
    Generate a course plan based on the provided course summaries.
    :param course_summaries: List of course summaries.
    :param model: The LLM model to use for generating the course plan.
    :return: Course plan as a JSON.
    """

    # Converting a List of Summaries to a Single String
    summaries_string = "\n".join(course_summaries)

    # Asking LLM to Generate Course Plan
    llm_model = llm(model=model)
    # TEST: Write Prompt for Course Plan Generation
    course_plan_prompt = predefined_prompts.generate_course_plan_prompt
    llm_response = llm_model.execute_llm_query(template=course_plan_prompt, params={"context": summaries_string})
    # Convert the response into a valid JSON format and return it
    course_plan=extract_json_from_llm_response(llm_response, model)
    return course_plan

def create_collection_names(course_config: dict):
    """
    Create collection names for vector databases and submodules in the course configuration.
    :param course_config: The course configuration dictionary.
    :return: Updated course configuration with collection names for vector databases and submodules.
    """
    for module in course_config:
        module_vector_db_details={
            "collection_name": "VDB_M_"+module,
            "num_chunks":0,
            "embedding_model":""
        }
        course_config[module]["vector_db_details"]=module_vector_db_details
        for submodule in course_config[module]["submodules"]:
            submodule_collection_name="VDB_S_"+module+"_"+submodule
            submodule_vector_db_details={
                "collection_name": submodule_collection_name,
                "num_chunks":0,
                "embedding_model":""
            }
            submodule_content_details={
                "collection_name": submodule_collection_name
            }
            course_config[module]["submodules"][submodule]["vector_db_details"]=submodule_vector_db_details
            course_config[module]["submodules"][submodule]["mongo_db_details"]=submodule_content_details
    return course_config

def categorize_course_content(course_config: dict, cache_collection_name: str, em_model=None, model="google"):
    """
    Categorize the course content based on the provided configuration and cache content.
    :param course_config: The course configuration dictionary.
    :param cache_content: The cached content dictionary.
    :param em_module: The embedding model to use for the main module.
    :param em_submodule: The embedding model to use for submodules.
    :return: Updated course configuration with categorized content.
    """
    #course_map=[]
    course_map={}
    # Create Course Map:
    for module in course_config:
        for submodule in course_config[module]["submodules"]:
            #course_map.append({
            #    "module_code": module+"_"+submodule,
            #    "submodule_name": course_config[module]["submodules"][submodule]["module_title"],
            #    "module_name": course_config[module]["module_title"]
            #})
            course_map[module+"_"+submodule] = {
                "module_code": module+"_"+submodule,
                "submodule_name": course_config[module]["submodules"][submodule]["module_title"],
                "module_name": course_config[module]["module_title"]
            }

    all_chunks = {}
    try:
        db_conn = mongo_db()
        cache_content_chunks= db_conn.get_all_langchain_documents(collection_name=cache_collection_name)
        db_conn.close_connection()
        key_prefix = "Chunk"
        chunk_counter=1
        for chunk in cache_content_chunks:
            all_chunks[key_prefix + str(chunk_counter)] = chunk.page_content
            chunk_counter += 1
    except Exception as e:
        print(f"Error: categorize_course_content() in fetching cached content from MongoDB: {e}")
        return None
    
    # Categorize Content
    # Module Collection name can be accessed by
    # module, submodule = module_code.split("_")
    # collection_name = course_config[module]["submodules"][submodule]["vector_db_details"]["collection_name"]

    llm_model = llm(model=model)
    categorize_course_content_prompt = predefined_prompts.categorize_course_content_prompt
    llm_response = llm_model.execute_llm_query(template=categorize_course_content_prompt, params={"context": all_chunks, "mapping": course_map})
    category_mapping = extract_json_from_llm_response(llm_response, model)

    # Do batch wise categorization and insert
    # Get all the chunks categorized by the table name, and parallely add them to their own vector database
    # Referenced by the collection name in the course_config

    reverse_module_mapping = {}
    for chunk_num, module_code in category_mapping.items():
        if reverse_module_mapping.get(module_code) is None:
            reverse_module_mapping[module_code] = []
        reverse_module_mapping[module_code].append(chunk_num)
    #print("Reverse Module Mapping: ", reverse_module_mapping)

    # Save Course Content in MongoDB
    for module_code, chunk_list in reverse_module_mapping.items():
        module, submodule = module_code.split("_")
        mdb_collection_name = course_config[module]["submodules"][submodule]["mongo_db_details"]["collection_name"]
        vdb_collection_name = course_config[module]["submodules"][submodule]["vector_db_details"]["collection_name"]
        try:
            #llm_em_model = llm(model=em_model, collection_name=vdb_collection_name)
            vdb_doc_list=[]
            db_conn = mongo_db()
            for chunk_num in chunk_list:
                chunk_content = all_chunks[chunk_num]
                document = Document(page_content=chunk_content, metadata={"source": mdb_collection_name})
                db_conn.add_langchain_document(collection_name=mdb_collection_name, document=document)
                vdb_doc_list.append(document)
            db_conn.close_connection()
            #llm_em_model.add_to_vectorstore(documents=vdb_doc_list)

        except Exception as e:
            print(f"Error: categorize_course_content() in adding documents to MongoDB: {e}")
            return None

    return True

    


