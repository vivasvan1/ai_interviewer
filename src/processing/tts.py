import collections
import sys
import numpy as np
import nltk  # we'll use this to split into sentences

nltk.download("punkt")
import os

from IPython.display import Audio
import base64
from src.agent.simple import stt_model, conversation
import torch
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

from transformers import BarkModel

# model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float16)
# device = "cuda:0" if torch.cuda.is_available() else "cpu"
# model = model.to(device)

# Enable CPU offload
# model.enable_cpu_offload()

import torch
import webrtcvad


# from transformers import AutoProcessor

# voice_preset = "v2/en_speaker_6"

# processor = AutoProcessor.from_pretrained("suno/bark-small")

# from optimum.bettertransformer import BetterTransformer

# # Use bettertransform for flash attention
# model = BetterTransformer.transform(model, keep_original_model=False)

system_personality_prompt = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Vaato and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
# system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
system_response_prompt = """Ask only one question per response"""

# def reset_llms():
#   global chat,chat_messages
#   #RESET
#   chat = ChatOpenAI()


#   chat_messages = [SystemMessage(content=system_personality_prompt+system_response_prompt)]
device = "cuda:0" if torch.cuda.is_available() else "cpu"

from pathlib import Path
import openai

import requests

url = "https://api.openai.com/v1/audio/speech"
headers = {
    "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
    "Content-Type": "application/json",
}


def do_text_to_speech(script):
    data = {
        "model": "tts-1",
        "input": script,
        "voice": "alloy",
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.content
        # with open("speech.mp3", "wb") as output_file:
        #     output_file.write(response.content)
    else:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
        return None

    # sentences = nltk.sent_tokenize(script)

    # SPEAKER = "v2/en_speaker_6"
    # SAMPLE_RATE = model.generation_config.sample_rate

    # silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    # pieces = []

    # with torch.inference_mode():
    #     text_prompt = sentences
    #     voice_preset = "v2/en_speaker_6"

    #     inputs = processor(text_prompt, voice_preset=voice_preset).to(device)
    #     output = model.generate(**inputs, do_sample=True)

    # for sentence in output:
    #     # audio_array = generate_audio(sentence, history_prompt=SPEAKER)
    #     pieces += [sentence.cpu().numpy(), silence.copy()]

    # ai_audio_obj = Audio(data=np.concatenate(pieces), rate=SAMPLE_RATE)
    # with open("/tmp/test.wav", "wb") as f:
    #     f.write(ai_audio_obj.data)

    # audio, sample_rate = read_wave("/tmp/test.wav")
    # vad = webrtcvad.Vad()
    # frames = frame_generator(30, audio, sample_rate)
    # frames = list(frames)
    # segments = vad_collector(sample_rate, 30, 300, vad, frames)

    # # Segmenting the Voice audio and save it in list as bytes
    # concataudio = [segment for segment in segments]

    # joinedaudio = b"".join(concataudio)
    # audio_array = np.frombuffer(joinedaudio, dtype=np.int16)
    # audio_obj = Audio(data=audio_array, rate=16000)
    # # vad = webrtcvad.Vad()

    # # # Define frame duration and padding duration
    # # frame_duration_ms = 30
    # # padding_duration_ms = 300

    # # # Apply VAD collector directly to ai_audio_obj
    # # frames = frame_generator(frame_duration_ms, ai_audio_obj.data, SAMPLE_RATE)
    # # frames = list(frames)
    # # segments = vad_collector(
    # #     SAMPLE_RATE, frame_duration_ms, padding_duration_ms, vad, frames
    # # )

    # # # Segmenting the voice audio and save it in a list as bytes
    # # concataudio = [segment for segment in segments]

    # # joinedaudio = b"".join([frame.data.tobytes() for frame in concataudio])
    # # audio_array = np.frombuffer(joinedaudio, dtype=np.int16)
    # # audio_obj = Audio(data=audio_array, rate=SAMPLE_RATE)

    # return audio_obj


import collections
import contextlib
import sys
import wave
import webrtcvad
from pydub import AudioSegment


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    sound = AudioSegment.from_mp3(path)
    sound = sound.set_frame_rate(16000)  # Convert to 16000 Hz
    sound.export(path, format="wav")

    with contextlib.closing(wave.open(path, "rb")) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()

        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, "wb")) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset : offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)

        sys.stdout.write("1" if is_speech else "0")
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                sys.stdout.write("+(%s)" % (ring_buffer[0][0].timestamp,))
                # We want to yield all the audio we see from now until
                # we are NOTTRIGGERED, but we have to start with the
                # audio that's already in the ring buffer.
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
                triggered = False
                yield b"".join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
    sys.stdout.write("\n")
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b"".join([f.bytes for f in voiced_frames])
