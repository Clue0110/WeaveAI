from langchain_community.document_loaders import YoutubeLoader

def youtube_extract_transcript(video_url):
    loader = YoutubeLoader.from_youtube_url(video_url, add_video_info=False)
    return loader.load() #Returns a List of Document objects

