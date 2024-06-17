from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, HTTPException

from src.processing.resume import read_pdf
from src.processing.screeners.resume_screener import resume_screener


class ResumeScreenerResponse(BaseModel):
    response: str = ""


class QuestionsResponse(BaseModel):
    questions: List[str]


router = APIRouter()


@router.post(
    "/resume_screener",
    response_model=ResumeScreenerResponse,
    tags=["Resume Screener"],
    description="Process the uploaded resume (optionally a job description) and produce screener response",
)
async def process_resume(
    resumes: list[UploadFile] = None,
    jd: UploadFile = None,
):
    try:
        resumeTextList = []
        for resume in resumes:
            resumeTextList.append(read_pdf(resume.file))

        jdText = read_pdf(jd.file)

        response = resume_screener(resumeTextList, jdText)

        return {
            "response": response,
        }

    except Exception as e:
        raise HTTPException(detail=str(e.with_traceback()), status_code=400)
