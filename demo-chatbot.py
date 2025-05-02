from WeaveAI.app.util.llm import *
import requests
from WeaveAI.app.util.video_utils import youtube_extract_transcript
from collections import deque

max_length=10
chat_history=deque() # Store the last 5 conversations

def add_convo_to_chat_history(user_input, bot_response):
    if len(chat_history)>=max_length:
        chat_history.popleft()
    chat_history.append({"user": user_input, "bot": bot_response})
def get_convo_from_chat_history():
    return str(chat_history)

llm_prompt="You are an AI tutor and a Course Assistant for this course. You will help answer questions about the course. Here are the set of documents that provide the context: {context}. Here is our previous chat history so far {chat_history} if i ask about my previous conversations or questions. Please use the context from before and answer the following question: {query}"

#transcript=youtube_extract_transcript("https://www.youtube.com/watch?v=WbzNRTTrX0g")
#chunks=get_chunks_from_documents(transcript)

google_llm=llm(model="google",collection_name="test3")
#google_llm.add_to_vectorstore(chunks)
google_llm.initialize_retriever(search_kwargs={"k":15})

print("Hello! How Can I help you?")
while True:
    print("---------------------------------")
    query=input("Query: ").strip()
    if query.lower()=="q":
        break

    # Get Context
    context=google_llm.fetch_data(query)
    # Execute LLM Query
    llm_response=google_llm.execute_llm_query(template=llm_prompt,params={
        "context":str(context),
        "query":query,
        "chat_history":get_convo_from_chat_history()
    })
    print("WeaveAI: ",llm_response.content)    # Add to chat history
    add_convo_to_chat_history(query, llm_response.content)
