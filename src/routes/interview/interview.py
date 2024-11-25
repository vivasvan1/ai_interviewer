import logging
import os
import traceback
from langchain.schema import SystemMessage
from src.ai_names import VoiceType
from src.processing.ai_prompt import interviewer_behavior_prompt, practice_interviewer_behavior_prompt
from src.utils.audio import convert_audio_to_base64
from src.agent.simple import conversation, process_user_response
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.resume import calculate_questions, process_resume_and_jd
from src.processing.tts import do_text_to_speech
from fastapi import APIRouter, Body, FastAPI, UploadFile, Form, File, HTTPException
from pydantic import BaseModel
from typing import List
from src.utils.helper import question_arr_formatter


class AIResponse(BaseModel):
    response: str
    history: str


class QuestionsResponse(BaseModel):
    questions: List[str]


router = APIRouter()


@router.post(
    "/interview/questions",
    response_model=QuestionsResponse,
    tags=["Interview"],
    description="Get questions for the interview",
)
async def get_questions(
    resume: UploadFile = None,
    resumeText: str = Body(default=None),
    jd: UploadFile = None,
    jdText: str = Body(default=None),
    questions: str = Body(default=None),
    language: str = Body(default=None)
    
):
    try:
        question_text = calculate_questions(
            resume.file if resume else None,
            jd.file if jd else None,
            resumeText,
            jdText,
            questions,
            [],
            True,
            language
        )
        return {"questions": question_arr_formatter(question_text) }
    except Exception as e:
        raise HTTPException(detail=str(e.with_traceback()), status_code=400)


@router.post(
    "/interview/start",
    response_model=AIResponse,
    tags=["Interview"],
    description="Process the uploaded resume (optionally a job description) and produce AI response",
)
async def initiate_interview(
    resume: UploadFile = None,
    resumeText: str = Body(default=None),
    jd: UploadFile = None,
    jdText: str = Body(default=None),
    questions: str = Body(default=None),
    questions_list: List[str] = Body(default=[]),
    is_dynamic: bool = Body(default=True),
    voice: VoiceType = Body(default=VoiceType.alloy),
    language: str = Body(default="english"),
    interview_type: str = Body(default='campaign')
):
    try:
        system_message = ""
        if interview_type == 'practice' :
            system_message = practice_interviewer_behavior_prompt(
            resume.file if resume else None,
            jd.file if jd else None,
            resumeText,
            jdText,
            questions,
            questions_list,
            is_dynamic,
            voice,
            language
        )
        else: 
            system_message = interviewer_behavior_prompt(
            resume.file if resume else None,
            jd.file if jd else None,
            resumeText,
            jdText,
            questions,
            questions_list,
            is_dynamic,
            voice,
            language
        )
        
        history = ChatMessageHistoryWithJSON()
        history.add_message(SystemMessage(content=system_message))

        return {"response": "", "history": history.to_json()}

    except Exception as e:
        raise HTTPException(detail=str(e.with_traceback()), status_code=400)


@router.post(
    "/interview/next",
    response_model=AIResponse,
    tags=["Interview"],
    description="Process user's audio response and compute AI response",
)

async def user_response(
    response_audio: UploadFile = File(...),
    chat_messages: str = Form(...),
    voice: VoiceType = Body(default=VoiceType.alloy),
):
    try:
        audio_bytes = await response_audio.read()

        # Check if audio_bytes is not empty
        if not audio_bytes:
            raise ValueError("No audio data found in the uploaded file")

        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)

        ai_reply = process_user_response(audio_bytes, history)
        if not ai_reply:
            raise ValueError("AI reply is empty or null")

        ai_response_base64 = convert_audio_to_base64(
            do_text_to_speech(ai_reply, voice.value)
        )
        if not ai_response_base64:
            raise ValueError("Failed to convert AI reply to base64 encoded audio")
        return {"response": ai_response_base64, "history": history.to_json()}

    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)
