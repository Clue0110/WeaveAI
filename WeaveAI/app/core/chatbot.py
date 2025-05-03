from WeaveAI.app.util.video_utils import youtube_extract_transcript
from WeaveAI.app.util.llm import *
from WeaveAI.app.config import *
from WeaveAI.app.util.db_utils import *

def answer_course_query(query: str, with_history: bool = False):
    # First get appropriate context using RAG
    query_llm = llm(model=llm_preferences.course_query_llm, collection_name=db_config.vdb_cache_content_collection_name)
    query_llm.initialize_retriever(search_kwargs={"k":75})
    query_context_chunks = query_llm.fetch_data(query)
    query_context = ""
    for chunk in query_context_chunks:
        query_context += chunk.page_content

    # Fetch conversation history if required
    chat_history=get_chatbot_interaction_history_string()

    # Now use the context to answer the query
    query_payload ={"context": query_context, "query": query, "chat_history": chat_history}
    llm_response= query_llm.execute_llm_query(template=predefined_prompts.course_query_prompt, params=query_payload)
    return llm_response


def add_chatbot_interaction_to_history(user_query: str, llm_response:str):
    '''
    Adds the Chatbot interaction to the Database

    Args:
        user_query (str): The query asked to the LLM
        llm_response (str): The response from LLM

    Returns:
        bool: True if success or False if an error was encountered
    '''
    try:
        r_db=redis_db()
        # Fetch Existing Chat History
        chat_history=r_db.read(key=llm_config.chat_history_redis_key,parse_json=True)
        if chat_history is None:
            chat_history={"interactions":[]}
        # Assert Max Interactions
        if len(chat_history["interactions"])>llm_config.chat_history_max_interactions:
            chat_history["interactions"]=chat_history["interactions"][1:]
        # Update Existing Chat History
        interaction=f"Question: {user_query} | Response: {llm_response}"
        chat_history["interactions"].append(interaction)
        r_db.update(key=llm_config.chat_history_redis_key,value=chat_history,use_json=True)
        r_db.close_connection()
    except Exception as e:
        print(f"Error in chatbot.add_chatbot_interaction_to_history(), Error Message: {e}")
        return False
    return True

def get_chatbot_interaction_history_string():
    '''
    Fetched the Chatbot Chat History as a String

    Returns:
        str: Returns "" if no chat_history or the entire chat_history as a string
        None: If any error was encountered
    '''
    try:
        r_db=redis_db()
        chat_history=r_db.read(key=llm_config.chat_history_redis_key,parse_json=True)
        r_db.close_connection()
        return "\n".join(chat_history["interactions"]) if chat_history is not None else ""
    except Exception as e:
        print(f"Error in chatbot.get_chatbot_interaction_history_string(), Error Message: {e}")
        return None