# 🎥 AskVideo — Video Knowledge Graph & Summary Generator

VidInsights.ai is an intelligent backend system that:
- Extracts transcripts from YouTube videos
- Generates knowledge graphs (Neo4j) based on semantic relationships
- Summarizes videos in multiple languages using Groq's LLMs
- Allows users to ask context-aware questions about the video
- Supports text-to-speech and speech-to-text features

This project is powered by **FastAPI**, **Streamlit**, **Neo4j**, and **Groq’s LLM APIs**.

---

## 🌐 Live App

🖥️ Streamlit UI: [https://askvideo-5tta2adheqpwaujmp4fia7.streamlit.app](https://askvideo-5tta2adheqpwaujmp4fia7.streamlit.app)  
🚀 FastAPI Backend (Render): [https://askvideo.onrender.com](https://askvideo.onrender.com)

---

## 📦 Tech Stack

| Layer         | Technology                     |
|--------------|---------------------------------|
| Backend API  | FastAPI                         |
| Frontend     | Streamlit                       |
| LLM API      | [Groq](https://console.groq.com/) (LLaMA3) |
| Graph DB     | [Neo4j Aura Cloud](https://neo4j.com/cloud/aura/) |
| TTS / STT    | gTTS (Google) / Groq Whisper    |

---

## 🧠 Features

✅ Extract YouTube transcripts (or input manually)  
✅ Auto-create semantic **knowledge graphs** in Neo4j  
✅ Summarize videos in multiple **languages** and **styles**  
✅ Ask questions about video content using graph context  
✅ Speech-to-text & text-to-speech support

---

## 🛠️ Local Setup Instructions

### 1. Clone the Repository


pip install -r requirements.txt

# .env
GROQ_API_KEY=your_groq_api_key

NEO4J_URI=neo4j+s://your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
