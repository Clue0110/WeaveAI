import os

PROJECT_ROOT=os.path.dirname(os.path.abspath(__file__))

class application_config:
    chroma_db_parent_path=os.path.join(PROJECT_ROOT,"util","db","chroma")

class llm_config:
    chat_history_redis_key="chat_history"
    chat_history_max_interactions=10

class llm_preferences:
    content_cache_embedding_model="google"
    course_query_llm="google"
    course_plan_llm="google"
    course_content_generator_llm="google"
    course_quiz_generator_llm="google"
    course_questtionnaire_generator_llm="google"

class predefined_prompts:
    prompt1="Based on the context {context} ask 3 questions whose answer is either 'YES' or 'NO', to test the user's proficieny on the topics which are prerequists to understand the context For example: If the context is related to linear regression we can as: Do you know statistics concepts like mean and average, we can ask: Do you know about standard deviation. Give it to me in a json format in 'q' 'a' format. I want you not to go beyond what context I have given. Please don't go beyond what is given as context."
    prompt2=""
    prompt3=""
    prompt4="I am giving you a set of context {context} with the following questionnaire {qa_data} and based on the given context generate a course plan module-wise and output in a json format Format being 'module' which is module number, 'title' which is module name, 'description' which is module description. You need to analyse what the user wants and check in the given information and make sure to give the exact paper where you are getting the information from. I want you not to go beyond what context I have given. Please don't go beyond what is given as context. Don't give introductory text, I need only the json and also in the end add another json element 'weekly' where you give the weekly plan for {time} weeks to complete all the modules. For every week give a quiz of 5 questions related to that particular module and also give 4 options with the right answer."
    prompt5=""
    prompt6=""
    
    generate_summary_prompt="You are an expert educator with expertise in curriculum development and Teaching. I need you to provide a detailed summary of the teaching material below. Do not use any information outside the given teaching material, and stay relevant. You are not allowed to lie. Do not leave out the essential parts, and make sure to cover them. I want you to respond directly with the requested summary in your response. Do not add any salutations or extra dialogue. Avoid all kinds of markup and only have text in the final response. The teaching material is as follows: {context}"
    
    generate_course_plan_prompt='You are an expert educator with expertise in curriculum development and Teaching. Your task is to create a comprehensive course plan for the learning materials I will provide below. You should identify the main modules and their respective submodules. Limit the maximum number of submodules in each main module to 5. Do not use any information outside the given teaching material, and stay relevant. You are not allowed to lie. The response must be a JSON file. The sample JSON file structure is provided below, along with its types. Ensure that you add descriptions for each module and submodule, which will serve as an overview for the respective module. The modules have integer numbers, and each submodule within each main module has integer numbers too.  Arrange all the data as instructed in the sample JSON structure given below. Directly respond with the JSON file in your response without additional text. The sample JSON file structure is as follows:{{ "module_number1-should be an integer":{{ "module_number": "same as the module number in the key","module_title": "module_title -String", "description": "description - String","submodules":{{ "submodule_number: should be a simple integer": {{ "module_number": "same as the submodule number key-String","module_title": "submodule_title - String", "description": "description - String",}},"submodule_number: should be a simple integer": {{ "module_number": "same as the submodule key-String", "module_title": "submodule_title - String", "description": "description - String" }} }} }} }}. The learning material is as follows: {context}'

    categorize_course_content_prompt="You are an expert educator who specializes in curriculum development and teaching. Your task is to categorize the course content based on the provided course plan and create a mapping JSON file as a result. You need to use a course plan JSON file, which I will provide as one of the inputs. The course plan JSON is an array of submodules that are in a course. Next, I will also input another JSON file, which is also a list of course content chunks, where the key is the chunk number. Your task is to map each course content chunk to a single module and submodule from the first course plan JSON file. The resultant JSON file will have the key as the chunk key and the value as the module code. Do not use any information outside the given information, and stay relevant. You are not allowed to lie. The response must be a JSON file without additional text. The first JSON file is: {mapping} The second JSON file is: {context}"

    course_query_prompt="You are an expert educator and skilled at answering questions from students. Your task is to answer a student's question as an educator using the learning material that will be provided. Do not use any information outside the given learning material, and stay relevant. You are not allowed to lie. I want you to directly respond to the student's question. The Teaching Material is as follows: {context}. This is the Chat History you had with the student so far: {chat_history}. Now, using the learning material from the above, answer the following question asked by a student: {query}. Avoid all kinds of markup and only have text in the final response."

class db_config:
    mongo_db_uri = "mongodb://localhost:27017"
    mongo_db_name = "WeaveAI"
    mdb_cache_content_collection_name = "content_cache"
    vdb_cache_content_collection_name = "content_cache"
    mdb_cache_summary_collection_name = "summary_cache"
    course_config = "course_config"
    course_quiz = "course_quiz"
    course_questionnaire = "course_questionnaire"

    redis_host="localhost"
    redis_port=6379
    redis_db=0
    redis_password=None #str
    redis_decode_responses=True

