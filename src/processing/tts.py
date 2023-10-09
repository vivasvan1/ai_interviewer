import numpy as np
import nltk  # we'll use this to split into sentences
nltk.download('punkt')

from bark import SAMPLE_RATE, generate_audio

from IPython.display import Audio
import base64
from src.agent.simple import stt_model,conversation

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI
from IPython.display import Audio


system_personality_prompt="""You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Sam and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
# system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
system_response_prompt="""Ask only one question per response"""

# def reset_llms():
#   global chat,chat_messages
#   #RESET
#   chat = ChatOpenAI()
  

#   chat_messages = [SystemMessage(content=system_personality_prompt+system_response_prompt)]


def do_text_to_speech(script):
  sentences = nltk.sent_tokenize(script)

  SPEAKER = "v2/en_speaker_6"
  silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

  pieces = []
  for sentence in sentences:
      audio_array = generate_audio(sentence, history_prompt=SPEAKER)
      pieces += [audio_array, silence.copy()]

  ai_audio_obj = Audio(np.concatenate(pieces), rate=SAMPLE_RATE)
  return ai_audio_obj

