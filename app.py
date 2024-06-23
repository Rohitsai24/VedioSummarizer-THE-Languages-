import streamlit as st
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import translate_v2 as translate
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

load_dotenv()  # Load environment variables

# Configure Google Translate API client
translate_client = translate.Client()

# Prompt for video summarization
prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video, providing an important summary within 250 words. Please provide the summary of the text given here:"""

# Function to extract transcript details based on available languages
def extract_transcript_details(video_id, languages=["en"]):
    try:
        transcript_text = None
        for lang in languages:
            try:
                transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                break  # Stop loop if transcript is found for a language
            except Exception:
                continue  # Try next language if transcript not found for current language

        if transcript_text is None:
            raise Exception("No transcript found in available languages.")

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

# Function to detect language and translate if necessary
def detect_language_and_translate(text, target_language):
    try:
        # Detect language
        result = translate_client.detect_language(text)
        detected_language = result["language"]

        if detected_language != target_language:
            # Translate if not in target language
            translated_text = translate_client.translate(text, target_language=target_language)["translatedText"]
            return translated_text
        else:
            return text

    except Exception as e:
        raise e

# Function to generate summary using LSA algorithm from sumy
def generate_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 1)  # Generate a 1-sentence summary
    return " ".join(str(sentence) for sentence in summary)

# Streamlit app
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.error("Please enter a YouTube video link.")
    else:
        try:
            transcript_text = extract_transcript_details(video_id)

            if transcript_text:
                if "te" in transcript_text.lower():
                    transcript_text = detect_language_and_translate(transcript_text, target_language="en")

                summary = generate_summary(transcript_text)
                st.markdown("## Detailed Notes (English Summary):")
                st.write(summary)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
