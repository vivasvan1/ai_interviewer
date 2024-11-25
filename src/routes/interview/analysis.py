import logging
import os
import traceback
from fastapi import APIRouter, Body
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from pydantic import BaseModel
from supabase import Client, create_client
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

from src.processing.analysis.subjective import (
    generate_improvement_analysis,
    generate_overall_analysis,
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
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)
        history.messages = history.messages[1:]
        history.timestamps = history.timestamps[1:]
        positive_response = generate_positive_analysis(history)

        return {"response": str(positive_response)}

    except Exception as e:
        print(traceback.format_exc())
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
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)
        
        history.messages = history.messages[1:]
        history.timestamps = history.timestamps[1:]
        
        improvement_response = generate_improvement_analysis(history)
        
        return {"response": str(improvement_response)}
    

    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)
    
    
@router.post(
    "/interview/analysis/overall",
    response_model=AnalysisResponse,
    tags=["Interview Analysis"],
    description="Process interview history and compute overall AI analysis",
)
async def overall_analysis_response(data: dict = Body(...)):
    
    try:
        logging.info("Received request for /interview/analysis/overall")
        uuid = data.get("uuid")
        
        supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY"))
        historyData = supabase.from_("interviews").select("history").eq("uuid",uuid).single().execute()
        chat_messages = historyData.data['history']
        
        # convert chat_messages_string to list of AI, Human, System Messages
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)
    
        response = generate_overall_analysis(history)
        
        try:
            supabase.from_("interviews").update({"analysis": response}).eq("uuid",uuid).execute()
            
        except:  
            logging.error("Error updating supabase: Interveiw Analysis")
            return "failed"
    
        return {"response": "success"}
    

    except Exception as e:
        logging.error(f"Error in user_response: {e}")
        raise HTTPException(detail=str(e), status_code=400)
    
    
