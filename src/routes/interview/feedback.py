import logging
from fastapi import APIRouter
from fastapi import Form, HTTPException
from pydantic import BaseModel
from src.processing.feedback.subjective import generate_feedback
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
import traceback

router = APIRouter()


class AnalysisResponse(BaseModel):
    response: str


@router.post(
    "/interview/feedback/per_message",
    response_model=AnalysisResponse,
    tags=["Interview Analysis"],
    description="",
)
async def feedback_response(
    message_index: str = Form(...), chat_messages: str = Form(...)
):
    try:
        logging.info("Received request for /interview/feedback/per_message")
        logging.info(f"message_index: {int(message_index)}")
        # Convert the JSON string of chat messages into a structured list of chat messages with their history
        history = ChatMessageHistoryWithJSON()
        history.from_json(chat_messages)

        # Check if the history has less than 3 messages, which is insufficient for generating feedback
        if len(history.messages) < int(message_index):
            print("len of history is < 3")
            # Raise an HTTP exception indicating insufficient messages for feedback generation
            raise HTTPException(
                detail="Not enough messages to generate feedback", status_code=400
            )

        # Trim the messages and timestamps history to consider only the last two entries for feedback
        history.messages = history.messages[
            int(message_index) - 1 : int(message_index) + 1
        ]
        history.timestamps = history.timestamps[
            int(message_index) - 1 : int(message_index) + 1
        ]

        # Generate feedback based on the last two entries of the chat messages history
        feedback = generate_feedback(history)
#         feedback = """### Ideal Answer:
# Sure! I have a strong educational background that has prepared me well for this role. I completed my Bachelor's degree in Computer Science from XYZ University. During my time there, I gained a solid foundation in programming languages, data structures, and algorithms. I also had the opportunity to work on several group projects, which helped me develop my teamwork and collaboration skills. After completing my Bachelor's degree, I pursued a Master's degree in Software Engineering from ABC University. This program allowed me to deepen my knowledge of software development methodologies and gain hands-on experience through internships and research projects. Overall, my educational background has provided me with a strong technical foundation and the ability to apply theoretical concepts to real-world scenarios.

# ### Areas of Improvement:
# The candidate did not provide any response to the question about their educational background.

# ### Suggestions:
# The candidate should provide a brief overview of their educational background, including the degrees they have obtained, the universities they attended, and any relevant coursework or projects they worked on. It would also be helpful to mention any honors or awards they received during their studies. Providing specific details about their educational background will give the interviewer a better understanding of the candidate's academic qualifications."""
        # history = ChatMessageHistoryWithJSON()
        # history.from_json(chat_messages)
        # history.add_feedback_to_message(int(message_index), feedback)
        # print(history.to_json())

        # Return the generated feedback as a response
        return AnalysisResponse(response=feedback)

    except HTTPException as e:
        print(traceback.format_exc())
        # Log the HTTPException error detail using logging
        logging.error(f"Error in user_response: {str(e.detail)}")
        # Reraise the caught HTTPException with its detail and status code for the client
        raise HTTPException(detail=str(e.detail), status_code=e.status_code)

    except Exception as e:
        print(traceback.format_exc())
        # Log any other general exceptions encountered during the execution
        logging.error(f"Error in user_response: {str(e)}")
        # In case of general exceptions, raise an HTTPException with the error message and a status code of 400
        raise HTTPException(detail=str(e), status_code=400)
