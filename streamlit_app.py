# streamlit_app.py
import streamlit as st
import requests
import base64
from youtube_transcript_api import YouTubeTranscriptApi

API_BASE_URL = "https://askvideo.onrender.com"  # Production backend URL

st.set_page_config(page_title="VidInsights.ai", layout="wide")
st.title("🎥 VidInsights.ai - Smart Video Analysis")

menu = st.sidebar.radio("Choose action", [
    "📹 Process Video",
    "❓ Ask Question",
    "🎤 Speech to Text",
    "🗣️ Text to Speech"
])

if menu == "📹 Process Video":
    st.subheader("📹 Video Summarization")
    video_url = st.text_input("YouTube Video URL")
    language = st.selectbox("Choose output language", ["english", "hindi", "marathi", "gujarati", "bengali", "kannada"])
    word_count = st.slider("Approximate Word Count", 50, 500, 150)
    style = st.selectbox("Summary Style", ["formal", "casual", "technical", "conversational"])

    if st.button("Generate Summary"):
        try:
            video_id = video_url.split("v=")[-1]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([x["text"] for x in transcript])
        except Exception as e:
            st.error(f"Could not fetch transcript: {e}")
            st.stop()

        with st.spinner("Sending transcript to backend for analysis..."):
            res = requests.post(f"{API_BASE_URL}/process-video", json={
                "video_url": video_url,
                "language": language,
                "word_count": word_count,
                "style": style,
                "transcript_text": transcript_text
            })
            if res.ok:
                st.success("Summary Generated ✅")
                st.text_area("Summary:", res.json()['summary'], height=300)
            else:
                st.error(res.json().get("detail", "Something went wrong"))

elif menu == "❓ Ask Question":
    st.subheader("❓ Ask a Question About the Video")
    video_url = st.text_input("YouTube Video URL")
    question = st.text_area("Your Question")
    language = st.selectbox("Language for Answer", ["english", "hindi", "marathi", "gujarati", "bengali", "kannada"])
    if st.button("Get Answer"):
        with st.spinner("Thinking..."):
            res = requests.post(f"{API_BASE_URL}/ask-question", json={
                "video_url": video_url,
                "question": question,
                "language": language,
                "question_type": "text"
            })
            if res.ok:
                st.success("Answer Found ✅")
                st.markdown(f"**Answer:** {res.json()['answer']}")
            else:
                st.error(res.json().get("detail", "Something went wrong"))

elif menu == "🎤 Speech to Text":
    st.subheader("🎤 Convert Speech to Text")
    language = st.selectbox("Language", ["english", "hindi", "marathi", "gujarati", "bengali", "kannada"])
    audio_file = st.file_uploader("Upload .m4a Audio File", type=["m4a"])
    if st.button("Transcribe") and audio_file:
        audio_bytes = audio_file.read()
        base64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        audio_data = f"data:audio/m4a;base64,{base64_audio}"
        res = requests.post(f"{API_BASE_URL}/speech-to-text", json={"audio_data": audio_data, "language": language})
        if res.ok:
            st.success("Transcription Complete ✅")
            st.text_area("Text:", res.json()['text'], height=300)
        else:
            st.error(res.json().get("detail", "Something went wrong"))

elif menu == "🗣️ Text to Speech":
    st.subheader("🗣️ Text to Speech")
    text = st.text_area("Text to convert")
    lang = st.selectbox("Select Language Code", ["en", "hi", "mr", "gu", "bn", "kn"])
    if st.button("Generate Audio"):
        res = requests.post(f"{API_BASE_URL}/text-to-speech", json={"text": text, "lang": lang})
        if res.ok:
            st.success("Audio Generated ✅")
            audio_data = base64.b64decode(res.json()["audioContent"])
            st.audio(audio_data, format="audio/mp3")
        else:
            st.error(res.json().get("detail", "Something went wrong"))
