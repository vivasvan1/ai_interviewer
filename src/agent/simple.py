import base64
import whisper

from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage
from IPython.display import Audio
from bark import SAMPLE_RATE
from langchain.chat_models import ChatOpenAI

from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

chat = ChatOpenAI(temperature=0.3)

system_personality_prompt = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Sam and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
# system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
system_response_prompt = """Ask only one question per response"""

chat_messages: list[BaseMessage] = [
    SystemMessage(content=system_personality_prompt + system_response_prompt)
]


stt_model = whisper.load_model("small")


def conversation(message: str, chat_messages: list[BaseMessage]) -> str:
    chat_messages.append(HumanMessage(content=message))
    out = chat(chat_messages)
    chat_messages.append(AIMessage(content=out.content))
    return out.content


def process_user_response(user_response_file, history: ChatMessageHistoryWithJSON):
    audio_data = base64.b64decode(user_response_file)
    human_audio_obj = Audio(audio_data, rate=SAMPLE_RATE)
    with open(f"tmp_human.wav", "wb") as f:
        f.write(human_audio_obj.data)
    human_reply = stt_model.transcribe(f"tmp_human.wav")
    human_reply_text = human_reply["text"]
    history.add_user_message(human_reply_text)
    ai_reply: str = conversation(human_reply_text, history.messages)
    history.add_ai_message(ai_reply)

    return ai_reply
