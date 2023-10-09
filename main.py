import base64
from fastapi import FastAPI, UploadFile, Form, HTTPException
from langchain.schema import SystemMessage

from src.agent.simple import process_user_response
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.resume import process_resume_and_jd
from src.processing.tts import do_text_to_speech

from bark import preload_models
import whisper

# Preload AI models
preload_models(True, True, True, True, True, True, True, False)
stt_model = whisper.load_model("small")

app = FastAPI()

from pydantic import BaseModel


class AIResponse(BaseModel):
    response: str
    history: str


@app.post("/process-resume", response_model=AIResponse)
async def process_resume(resume: UploadFile = Form(...), jd: UploadFile = None):
    try:
        ai_reply, question_text, system_message = process_resume_and_jd(
            resume.file, jd.file if jd else None
        )
        history = ChatMessageHistoryWithJSON()
        history.messages.append(SystemMessage(content=system_message))
        history.add_ai_message(ai_reply)
        ai_audio_obj = do_text_to_speech(ai_reply)
        
        binary_audio_data = ai_audio_obj.data
        ai_response_base64 = base64.b64encode(binary_audio_data).decode("utf-8")
        return {"response": ai_response_base64,"history": history.to_json()}
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)


@app.post("/process-response", response_model=AIResponse)
async def user_response(
    response_audio: UploadFile = Form(...), chat_messages: str = Form(...)
):
    try:
        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)
        
        ai_reply = process_user_response(response_audio, history)
        
        ai_audio_obj = do_text_to_speech(ai_reply)
        binary_audio_data = ai_audio_obj.data
        ai_response_base64 = base64.b64encode(binary_audio_data).decode("utf-8")
        
        return {"response": ai_response_base64, "history": history.to_json()}
    except Exception as e:
        raise HTTPException(detail=str(e), status_code=400)
