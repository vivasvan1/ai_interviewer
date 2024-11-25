import logging
import os
from fastapi import HTTPException
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
import copy


generate_feedback_system_message = """\
Given two messages from a candidate and an interviewer, \
i want you to tell me an example of an ideal answer to the \
question and where the candidate can improve upon. Give as \
much detail as possible and in following format \
The response should strictly include the following:
{   
    "question": "content of question asked",
    "ideal_answer": "ideal answer for the question"
    "areas_of_improvement: "areas of improvement for the candidate"
}
"""

def generate_feedback(
    history: ChatMessageHistoryWithJSON,
):
    chat = ChatOpenAI(temperature=0.7, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(SystemMessage(content=generate_feedback_system_message))
    messages.append(HumanMessage(content=history.to_json()))
    out = chat(messages)
    r = out.content
    return r

def generate_feedback_by_history(
    history: ChatMessageHistoryWithJSON,
):
    if len(history.messages) < 3:
        return None
    # Create a copy of history to avoid modifying the original
    history_copy = copy.deepcopy(history)
    
    question_index = len(history.messages) - 2

    if question_index < 1:
        print("Insufficient messages for slicing. Cannot generate feedback.")
        return None

    # Slice the messages and timestamps to focus on the last two entries
    history_copy.messages = history_copy.messages[question_index : question_index + 2]
    history_copy.timestamps = history_copy.timestamps[question_index : question_index + 2]

    # print(f"Sliced history messages: {history_copy.messages}")

    # Generate feedback based on the trimmed history
    feedback = generate_feedback(history_copy)
    if feedback is not None:
        history.feedbacks.append(feedback)

    return feedback

# ### Ideal Answer:\n<ideal_answer>\n\n### Areas of Improvement:\
# \n<areas_of_improvement>\n\n### Suggestions:\n<suggestion>\