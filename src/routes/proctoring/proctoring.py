import logging
import os
from fastapi import APIRouter, Body, Form, HTTPException
from pydantic import BaseModel
import requests

from src.processing.proctoring.proctoring import processFrame

from supabase import create_client, Client

router = APIRouter()

class AnalysisResponse(BaseModel):
    response: str

@router.post(
    "/proctoring/analyse_frames",
    response_model=AnalysisResponse,
    tags=["Proctoring"],
    description="Analyse frames from the interview",
)
async def analyse_frames(data: dict = Body(...)):
    try:
        logging.info("Received request for /proctoring/analyse_frames")
        supabaseUrl = os.environ.get("SUPABASE_URL")
        supabase: Client = create_client(supabaseUrl, os.environ.get("SUPABASE_ANON_KEY"))
        uuid = data.get("uuid")
        flagged = False
        reasons = []
        
        # Correctly execute the query and get the data
        response = supabase.from_("interviews").select("conversation_tab_switches").eq("uuid", uuid).single().execute()
        tabSwitchCount = response.data['conversation_tab_switches']

        if int(tabSwitchCount) > 3:
            flagged = True
            reasons.append({"tag": "multiple_tab_switch", "frames": None})
        
        framesList = supabase.storage.from_("interviews").list(f"interviews/{uuid}/video_frames/")
        frame_urls = [
            f"{supabaseUrl}/storage/v1/object/public/interviews/interviews/{uuid}/video_frames/{f['name']}?"
            for f in framesList
        ]
        
        susbehavior = processFrame(frame_urls)
        
        if len(susbehavior) > 0:
            flagged = True
            reasons.extend(susbehavior)
                
        # Finally updating DB
        supabase.from_("interviews").update({
            "suspicion": {"flagged": flagged, "reasons": reasons}
        }).eq("uuid", uuid).execute()

        return {"response": "success"}
    except Exception as e:
        logging.error(f"Error in analyse_frames: {str(e)}")
        raise HTTPException(detail=str(e), status_code=400)
