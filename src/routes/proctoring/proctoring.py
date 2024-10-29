
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.processing.proctoring.proctoring import processFrame


router = APIRouter()

class AnalysisResponse(BaseModel):
    response: list


@router.post(
    "/proctoring/analyse_fames",
    response_model=AnalysisResponse,
    tags=["Proctoring"],
    description="Analyse frames from the interview",
)
async def analyse_frames():
    try:
        susbehavior = processFrame()
        print(susbehavior)
        return {"response": susbehavior}
    except Exception as e:
        raise HTTPException(detail=str(e.with_traceback()), status_code=400)