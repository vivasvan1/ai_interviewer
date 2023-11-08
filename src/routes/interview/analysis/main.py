import logging
from fastapi import APIRouter
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from pydantic import BaseModel
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

from src.processing.analysis.subjective import (
    generate_improvement_analysis,
    generate_positive_analysis,
)

router = APIRouter()


class AnalysisResponse(BaseModel):
    response: str


@router.post(
    "/interview/analysis/positive",
    response_model=AnalysisResponse,
    tags=["Interview Analysis"],
    description="Process interview history and compute positive AI analysis",
)
async def positive_analysis_response(chat_messages: str = Form(...)):
    try:
        logging.info("Received request for /interview/analysis/positive")

        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON(timestamps=[])
        history.from_json(chat_messages)
        history.messages = history.messages[1:]
        history.timestamps = history.timestamps[1:]
        positive_response = generate_positive_analysis(history)

        return {"response": str(positive_response)}

    except Exception as e:
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)


@router.post(
    "/interview/analysis/improvement",
    response_model=AnalysisResponse,
    tags=["Interview Analysis"],
    description="Process interview history and compute negative AI analysis",
)
async def improvement_analysis_response(chat_messages: str = Form(...)):
    try:
        logging.info("Received request for /interview/analysis/improvement")

        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON(timestamps=[])
        history.from_json(chat_messages)
        
        history.messages = history.messages[1:]
        history.timestamps = history.timestamps[1:]

        improvement_response = generate_improvement_analysis(history)

        return {"response": str(improvement_response)}

    except Exception as e:
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)
