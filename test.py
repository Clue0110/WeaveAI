from WeaveAI.app.util.llm import *
import requests
from WeaveAI.app.util.video_utils import youtube_extract_transcript
import sys


#transcript=youtube_extract_transcript("https://www.youtube.com/watch?v=xlVX7dXLS64")
#chunks=get_chunks_from_documents(transcript)

# RAG Flow
#lamma_llm=llm(model="llama")
lamma_llm=llm(model="google")
#lamma_llm.add_to_vectorstore(chunks)
lamma_llm.initialize_retriever(search_kwargs={"k":1000000})
query="What does BFS stand for?"
response=lamma_llm.fetch_data(query)
#print(response)


query="Can you use the information here: ${data} to answer the question: What is BFS full form?"
res=lamma_llm.execute_llm_query(template=query,params={"data":str(response)})
#print(type(res))
print(res.content)


query="Based on the context {response} ask 3 questions whose answer is either 'YES' or 'NO', to test the user's proficieny on the topics which are prerequists to understand the context For example: If the context is related to linear regression we can as: Do you know statistics concepts like mean and average, we can ask: Do you know about standard deviation. Give it to me in a json format in 'q' 'a' format. I want you not to go beyond what context I have given. Please don't go beyond what is given as context"
res=lamma_llm.execute_llm_query(template=query,params={"response":str(response)})
print(res.content)

query="Do you remember what i asked before?"
res=lamma_llm.execute_llm_query(template=query,params={})
print(res.content)