# import base64
import os

# import whisper

from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage

# from IPython.display import Audio
from langchain.chat_models import ChatOpenAI
import requests

from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

chat = ChatOpenAI(temperature=0.3, openai_api_key=os.environ.get("OPENAI_API_KEY"))

system_personality_prompt_case = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Vaato and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user. Dont divert from asking questions\n\n"""
# system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
system_response_prompt = """Ask only one question per response"""

chat_messages: list[BaseMessage] = [
    SystemMessage(content=system_personality_prompt_case + system_response_prompt)
]


# stt_model = whisper.load_model("small")


def conversation(message: str, chat_messages: list[BaseMessage]) -> str:
    # chat_messages.append(HumanMessage(content=message))
    out = chat(chat_messages)
    # chat_messages.append(AIMessage(content=out.content))
    return out.content


def process_user_response(audio_data, history: ChatMessageHistoryWithJSON):
    # audio_data = base64.b64decode(user_response_file)
    # human_audio_obj = Audio(audio_data, rate=SAMPLE_RATE)
    # with open(f"tmp_human.wav", "wb") as f:
    #     f.write(audio_data)

    try:
        human_reply_text = speech_to_text(audio_data)

        # human_reply = stt_model.transcribe(f"tmp_human.wav")

        # human_reply_text = human_reply
        history.add_user_message(human_reply_text)
        ai_reply: str = conversation(human_reply_text, history.messages)
        history.add_ai_message(ai_reply)

        return ai_reply
    except Exception as e:
        raise e


def speech_to_text(audio_data):
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY"),
    }
    files = {
        "file": ("openai.mp3", audio_data),
    }
    data = {
        "model": "whisper-1",
    }

    response = requests.post(url, headers=headers, files=files, data=data)

    if response.status_code == 200:
        transcription_data = response.json()
        return transcription_data["text"]
    else:
        print(f"Request failed with status code {response.status_code}")
        response.raise_for_status()
