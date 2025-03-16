import streamlit as st
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from txtai.pipeline import Summary
from PyPDF2 import PdfReader

st.set_page_config(layout="wide")

# Load transformers summarizer pipeline
summarizer = pipeline('summarization')

@st.cache_resource
def text_summary(text, maxlength=None):
    # Create summary instance using txtai Summary
    summary = Summary()
    result = summary(text)
    return result

def extract_text_from_pdf(file_path):
    # Open the PDF file using PyPDF2 and extract text
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_youtube_transcript(video_id):
    # Fetch the transcript for the YouTube video using YouTubeTranscriptApi
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    result = ""
    for i in transcript:
        result += ' ' + i['text']
    return result

choice = st.sidebar.selectbox("Select your choice", ["Summarize YouTube Video", "Summarize Text", "Summarize Document"])

if choice == "Summarize YouTube Video":
    st.subheader("Summarize YouTube Video")
    youtube_video_url = st.text_input("Enter YouTube video URL")
    
    if youtube_video_url:
        video_id = youtube_video_url.split("=")[1]
        try:
            # Fetch transcript and summarize
            transcript = get_youtube_transcript(video_id)
            num_iters = int(len(transcript)/1000)
            summarized_text = []
            for i in range(0, num_iters + 1):
                start = i * 1000
                end = (i + 1) * 1000
                out = summarizer(transcript[start:end])
                out = out[0]['summary_text']
                summarized_text.append(out)

            st.markdown("**Video Transcript Summary:**")
            st.success(" ".join(summarized_text))
        except Exception as e:
            st.error(f"Error fetching transcript: {e}")

elif choice == "Summarize Text":
    st.subheader("Summarize Text")
    input_text = st.text_area("Enter your text here")
    
    if input_text and st.button("Summarize Text"):
        st.markdown("**Your Input Text:**")
        st.info(input_text)
        result = text_summary(input_text)
        st.markdown("**Summary Result:**")
        st.success(result)

elif choice == "Summarize Document":
    st.subheader("Summarize Document")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    
    if input_file:
        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            extracted_text = extract_text_from_pdf("doc_file.pdf")
            
            st.markdown("**Extracted Text from Document:**")
            st.info(extracted_text)
            
            doc_summary = text_summary(extracted_text)
            st.markdown("**Document Summary Result:**")
            st.success(doc_summary)
