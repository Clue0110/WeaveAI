import WeaveAI.app.core.content_mgmt as content_mgmt
import pprint

if __name__ == "__main__":
    cache_content_collection_name = "youtube_content_cache"
    cache_summary_collection_name = "youtube_summary_cache"
    model_name = "google"
    # Cache YouTube content
    video_transcript = content_mgmt.cache_content_youtube(url="", collection_name=cache_content_collection_name, model=model_name)
    video_summary= content_mgmt.generate_summary_with_llm(content=video_transcript, model=model_name)
    content_mgmt.cache_summary_content(summary_payload={"summary":video_summary, "url":"test"}, collection_name=cache_summary_collection_name)
    course_plan= content_mgmt.generate_courseplan(course_summaries=[video_summary], model=model_name)
    print("Course Plan:")
    #pprint.pprint(course_plan)
    course_plan = content_mgmt.create_collection_names(course_config=course_plan)
    print("Course Config:")
    #pprint.pprint(course_plan)

    mapping= content_mgmt.categorize_course_content(course_config=course_plan,  model=model_name, cache_collection_name=cache_content_collection_name, em_model=model_name)
    print("Course Mapping:")
    pprint.pprint(mapping)
