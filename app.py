import streamlit as st
import yt_dlp
import whisper
import speech_recognition as sr
from txtai.pipeline import Summary
from PyPDF2 import PdfReader

st.set_page_config(layout="wide")

@st.cache_resource
def text_summary(text, maxlength=None):
    summary = Summary()
    result = summary(text)
    return result

def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        text = page.extract_text()
    return text

def get_youtube_transcript(video_url):
    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "skip_download": True,
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        subtitles = info.get("subtitles") or info.get("automatic_captions")
        if subtitles and "en" in subtitles:
            return subtitles["en"][0]["url"]
        else:
            return "No subtitles available."

def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎤 Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError:
        return "Could not request results from Google Speech API."

choice = st.sidebar.selectbox("Select your choice", [
    "Summarize Text", "Summarize Document", "Summarize YouTube Video", "Summarize Voice Input"
])

if choice == "Summarize Text":
    st.subheader("Summarize Text")
    input_text = st.text_area("Enter your text here")
    if st.button("Summarize Text"):
        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("**Your Input Text**")
            st.info(input_text)
        with col2:
            st.markdown("**Summary Result**")
            result = text_summary(input_text)
            st.success(result)

elif choice == "Summarize Document":
    st.subheader("Summarize Document")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    if input_file is not None:
        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                st.info("File uploaded successfully")
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                st.markdown("**Summary Result**")
                doc_summary = text_summary(extracted_text)
                st.success(doc_summary)

elif choice == "Summarize YouTube Video":
    st.subheader("Summarize YouTube Video")
    video_url = st.text_input("Enter YouTube Video URL")
    if st.button("Summarize Video"):
        transcript_url = get_youtube_transcript(video_url)
        if transcript_url.startswith("http"):
            st.info("Fetching subtitles...")
            import requests
            transcript_text = requests.get(transcript_url).text
            col1, col2 = st.columns([1,1])
            with col1:
                st.markdown("**Extracted Transcript:**")
                st.info(transcript_text[:1000])  # Displaying first 1000 characters
            with col2:
                st.markdown("**Summary Result**")
                video_summary = text_summary(transcript_text)
                st.success(video_summary)
        else:
            st.error("No subtitles found for this video.")

elif choice == "Summarize Voice Input":
    st.subheader("Summarize Voice Input")
    if st.button("Start Recording"):
        voice_text = voice_to_text()
        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("**Recognized Speech:**")
            st.info(voice_text)
        with col2:
            st.markdown("**Summary Result**")
            speech_summary = text_summary(voice_text)
            st.success(speech_summary)
