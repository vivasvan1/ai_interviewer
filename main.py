
from os.path import join, dirname
from dotenv import load_dotenv
import os
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

import base64
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.schema import SystemMessage
from src.agent.simple import process_user_response
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.resume import process_resume_and_jd
from src.processing.tts import do_text_to_speech
from bark import preload_models
import whisper


import logging

logging.basicConfig(level=logging.INFO)


from src.utils.audio import convert_audio_to_base64

# Preload AI models
preload_models(True, True, True, True, True, True, True, False)
stt_model = whisper.load_model("small")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://ai-interviewer-two.vercel.app",
    "https://vaato.vercel.app",
    "https://vaato.ultimateworld.io"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel


class AIResponse(BaseModel):
    response: str
    history: str


@app.post(
    "/interview/start",
    response_model=AIResponse,
    tags=["Interview"],
    description="Process the uploaded resume (optionally a job description) and produce AI response",
)
async def process_resume(
    resume: UploadFile = Form(...), jd: UploadFile = None, questions: str = ""
):
    try:
        ai_reply, question_text, system_message = process_resume_and_jd(
            resume.file, jd.file if jd else None, questions
        )
        history = ChatMessageHistoryWithJSON(timestamps=[])
        history.add_message(SystemMessage(content=system_message))
        # history.messages.append(SystemMessage(content=system_message))
        history.add_ai_message(ai_reply)

        ai_response_base64 = convert_audio_to_base64(do_text_to_speech(ai_reply))
        return {"response": ai_response_base64, "history": history.to_json()}

    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)


@app.post(
    "/interview/next",
    response_model=AIResponse,
    tags=["Interview"],
    description="Process user's audio response and compute AI response",
)
async def user_response(
    response_audio: UploadFile = File(...), chat_messages: str = Form(...)
):
    try:
        logging.info("Received request for /interview/next")

        audio_bytes = await response_audio.read()

        # Check if audio_bytes is not empty
        if not audio_bytes:
            raise ValueError("No audio data found in the uploaded file")

        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON(timestamps=[])
        history.from_json(chat_messages)

        ai_reply = process_user_response(audio_bytes, history)
        if not ai_reply:
            raise ValueError("AI reply is empty or null")

        ai_response_base64 = convert_audio_to_base64(do_text_to_speech(ai_reply))
        if not ai_response_base64:
            raise ValueError("Failed to convert AI reply to base64 encoded audio")

        return {"response": ai_response_base64, "history": history.to_json()}

    except Exception as e:
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)
