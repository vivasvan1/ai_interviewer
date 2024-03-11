import json
import logging
import traceback
from typing import Optional
from fastapi import APIRouter, UploadFile
from fastapi import Form, HTTPException
from pydantic import BaseModel
from src.processing.screeners.candidate_screener import generate_evaluation
from src.processing.resume import read_pdf

from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.screeners.jd_screener import generate_metric
from langchain.schema import BaseMessage, SystemMessage, AIMessage, HumanMessage


router = APIRouter()


class MetricResponse(BaseModel):
    response: dict


@router.post(
    "/hr_campaign/gen_metric",
    response_model=MetricResponse,
    tags=["HR Campaign"],
    description="Generate metric for the hr_campaign",
)
async def gen_metric(jd: UploadFile = None, jdText: Optional[str] = Form(None)):
    try:
        logging.info("Received request for /hr_campaign/gen_metric")

        if jd == None and jdText == None:
            return {
                "response": {
                    "metrics": [
                        "Communication Skills",
                        "Problem Solving Ability",
                        "Teamwork",
                        "Adaptability",
                        "Professionalism",
                    ]
                }
            }
        net_jd = ""
        if jd:
            extracted_text = read_pdf(jd.file)
            net_jd += extracted_text + "\n\n"
        if jdText:
            net_jd += jdText

        metric = generate_metric(net_jd)
        return {"response": metric}

    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error in user_response: {e}")
        return {
            "response": {
                "metrics": [
                    "Communication Skills",
                    "Problem Solving Ability",
                    "Teamwork",
                    "Adaptability",
                    "Professionalism",
                ]
            }
        }
        # raise HTTPException(detail=str(e), status_code=400)


class EvaluationMetricResponse(BaseModel):
    response: dict


@router.post(
    "/hr_campaign/evaluate_candidate",
    response_model=EvaluationMetricResponse,
    tags=["HR Campaign"],
    description="Generate eval metric for the hr_campaign",
)
async def eval_candidate(
    conversation_transcript: str = Form(...),
    metric: str = Form(...),
    #  resume: UploadFile = None, resumeText: Optional[str] = Form(None)
):
    try:
        logging.info("Received request for /hr_campaign/gen_metric")

        history = ChatMessageHistoryWithJSON()
        history.from_json(conversation_transcript)

        

        # if resume == None and resumeText == None:
        response = generate_evaluation(history,metric)

        # net_jd = ""
        # if jd:
        #     extracted_text = read_pdf(jd.file)
        #     net_jd += extracted_text + "\n\n"
        # if jdText:
        #     net_jd += jdText

        # metric = generate_metric(net_jd)
        return {"response": response}

    except Exception as e:
        print(traceback.format_exc())
        logging.error(f"Error in user_response: {e}")
        # return {
        #     "response": {
        #         "metrics": [
        #             "Communication Skills",
        #             "Problem Solving Ability",
        #             "Teamwork",
        #             "Adaptability",
        #             "Professionalism",
        #         ]
        #     }
        # }
        raise HTTPException(detail=str(e), status_code=400)
