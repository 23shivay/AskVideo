# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from groq import Groq
import os
from typing import Optional
from neo4j import GraphDatabase

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://askvideo-5tta2adheqpwaujmp4fia7.streamlit.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello from VidInsights.ai API!", "status": "online"}

# Clients and DB config
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

class VideoRequest(BaseModel):
    video_url: str
    language: str
    word_count: int
    style: str
    transcript_text: Optional[str] = None  # <-- ADDED

class VideoResponse(BaseModel):
    success: bool
    summary: str
    message: Optional[str] = None

def create_knowledge_graph(video_id: str, transcript_text: str):
    with neo4j_driver.session() as session:
        session.run("""
            MERGE (v:Video {video_id: $video_id, transcript: $transcript})
        """, video_id=video_id, transcript=transcript_text)

        prompt = f"""
        Analyze this transcript and list triples like entity1|relationship|entity2:

        {transcript_text}
        """
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",  # <-- UPDATED MODEL
            temperature=0.5,
        )

        triples = response.choices[0].message.content.strip().split('\n')
        for triple in triples:
            if '|' in triple:
                e1, rel, e2 = map(str.strip, triple.split('|'))
                session.run("""
                    MATCH (v:Video {video_id: $video_id})
                    MERGE (a:Entity {name: $e1})
                    MERGE (b:Entity {name: $e2})
                    MERGE (a)-[:RELATES_TO {type: $rel}]->(b)
                    MERGE (v)-[:HAS_ENTITY]->(a)
                    MERGE (v)-[:HAS_ENTITY]->(b)
                """, video_id=video_id, e1=e1, e2=e2, rel=rel)

def generate_summary(video_id: str, style: str, word_count: int, language: str):
    with neo4j_driver.session() as session:
        data = session.run("""
            MATCH (v:Video {video_id: $video_id})
            OPTIONAL MATCH (v)-[:HAS_ENTITY]->(e1)-[r:RELATES_TO]->(e2)
            RETURN v.transcript as transcript, collect(e1.name + ' ' + r.type + ' ' + e2.name) as rels
        """, video_id=video_id).single()

    transcript = data['transcript']
    rels = "\n".join(data['rels'])

    prompt = f"""
    Write a {style} summary (~{word_count} words) of this transcript in {language}:
    Relationships:
    {rels}

    Transcript:
    {transcript}
    """

    summary = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    ).choices[0].message.content.strip()

    return summary

@app.post("/process-video", response_model=VideoResponse)
def process_video(request: VideoRequest):
    try:
        video_id = request.video_url.split("v=")[-1]
        transcript_text = request.transcript_text

        if not transcript_text:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([x['text'] for x in transcript])

        create_knowledge_graph(video_id, transcript_text)
        summary = generate_summary(video_id, request.style, request.word_count, request.language)

        return VideoResponse(success=True, summary=summary, message="Video processed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
