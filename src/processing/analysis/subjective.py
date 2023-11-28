import json
import os

import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.config.constants import IMPROVEMENT_ANALYSIS_PROMPT, POSITIVE_ANALYSIS_PROMPT
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON


def generate_positive_analysis(
    history: ChatMessageHistoryWithJSON,
):
    chat = ChatOpenAI(temperature=0.3, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(SystemMessage(content=POSITIVE_ANALYSIS_PROMPT))
    messages.append(HumanMessage(content=history.to_json()))
    out = chat(messages)

    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": """""",
    #         },
    #         {"role": "user", "content": history.to_json()},
    #     ],
    #     # response_format={type: "json_object"},
    # )
    r = json.loads(out.content)
    return r


def generate_improvement_analysis(
    history: ChatMessageHistoryWithJSON,
):
    chat = ChatOpenAI(temperature=0.3, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(SystemMessage(content=IMPROVEMENT_ANALYSIS_PROMPT))
    messages.append(HumanMessage(content=history.to_json()))

    out = chat(messages)

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    # messages = []
    # for message in history.messages:
    #     if message.type == "ai":
    #         messages.append({"role": "assistant", "content": message.content})
    #     elif message.type == "human":
    #         messages.append({"role": "user", "content": message.content})

    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": """given a transcript of an interview i want you to tell me 5 things the candidate can improve upon. please respond in JSON with format {"points":[{"point":<point_name>,"reason":<reason>}]}""",
    #         },
    #         {"role": "user", "content": history.to_json()},
    #     ],
    #     # response_format={type: "json_object"},
    # )
    r = json.loads(out.content)
    return r

    # # audio_data = base64.b64decode(user_response_file)
    # # human_audio_obj = Audio(audio_data, rate=SAMPLE_RATE)
    # with open(f"tmp_human.wav", "wb") as f:
    #     f.write(audio_data)
    # human_reply = stt_model.transcribe(f"tmp_human.wav")
    # human_reply_text = human_reply["text"]
    # history.add_user_message(human_reply_text)
    # ai_reply: str = conversation(human_reply_text, history.messages)
    # history.add_ai_message(ai_reply)

    # return ai_reply
