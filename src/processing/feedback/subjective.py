import json
import logging
import os
import openai
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage


generate_feedback_system_message = """\
Given two messages from a candidate and an interviewer, \
i want you to tell me an example of an ideal answer to the \
question and where the candidate can improve upon. Give as \
much detail as possible and in following format \
### Ideal Answer:\n<ideal_answer>\n\n### Areas of Improvement:\
\n<areas_of_improvement>\n\n### Suggestions:\n<suggestion>\
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
    logging.info(r)
    return r
