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

# bark_model = BarkModel.from_pretrained("suno/bark-small", torch_dtype=torch.float16)
# processing_device = "cuda:0" if torch.cuda.is_available() else "cpu"
# bark_model = bark_model.to(processing_device)

import torch
import webrtcvad


# from transformers import AutoProcessor

# voice_preset_id = "v2/en_speaker_6"

# audio_processor = AutoProcessor.from_pretrained("suno/bark-small")

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

processing_processing_device = "cuda:0" if torch.cuda.is_available() else "cpu"

from pathlib import Path
import openai

import requests

api_url = "https://api.openai.com/v1/audio/speech"
api_headers = {
    "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY"),
    "Content-Type": "application/json",
}


def do_text_to_speech(script):
    request_data = {
        "model": "tts-1",
        "input": text_script,
        "voice": "alloy",
    }

    api_response = requests.post(api_url, headers=api_headers, json=request_data)

    if api_response.status_code == 200:
        return api_response.content
        # with open("speech.mp3", "wb") as output_file_path:
        #     output_file_path.write(api_response.content)
    else:
        print(f"Request failed with status code {api_response.status_code}")
        print(api_response.text)
        return None

    # sentences = nltk.sent_tokenize(text_script)

    # speaker_id = "v2/en_speaker_6"
    # sample_rate = bark_model.generation_config.sample_rate

    # silence_duration = np.zeros(int(0.25 * sample_rate))  # quarter second of silence

    # audio_pieces = []

    # with torch.inference_mode():
    #     text_input = sentences
    #     voice_preset_id = "v2/en_speaker_6"

    #     inputs = audio_processor(text_input, voice_preset=voice_preset_id).to(processing_device)
    #     output = bark_model.generate(**inputs, do_sample=True)

    # for sentence in output:
    #     # audio_data_array = generate_audio(sentence, history_prompt=speaker_id)
    #     audio_pieces += [sentence.cpu().numpy(), silence_duration.copy()]

    # ai_audio_object = Audio(data=np.concatenate(audio_pieces), rate=sample_rate)
    # with open("/tmp/test.wav", "wb") as f:
    #     f.write(ai_audio_object.data)

    # audio_data, audio_sample_rate = read_wave("/tmp/test.wav")
    # voice_activity_detector = webrtcvad.Vad()
    # audio_frames = frame_generator(30, audio_data, audio_sample_rate)
    # audio_frames = list(audio_frames)
    # audio_segments = vad_collector(audio_sample_rate, 30, 300, voice_activity_detector, audio_frames)

    # # Segmenting the Voice audio and save it in list as bytes
    # concatenated_audio = [segment for segment in audio_segments]

    # joined_audio = b"".join(concatenated_audio)
    # audio_data_array = np.frombuffer(joined_audio, dtype=np.int16)
    # audio_object = Audio(data=audio_data_array, rate=16000)
    # # voice_activity_detector = webrtcvad.Vad()

    # # # Define frame duration and padding duration
    # # frame_duration_ms = 30
    # # padding_duration_ms = 300

    # # # Apply VAD collector directly to ai_audio_obj
    # # audio_frames = frame_generator(frame_duration_ms, ai_audio_object.data, sample_rate)
    # # audio_frames = list(audio_frames)
    # # audio_segments = vad_collector(
    # #     sample_rate, frame_duration_ms, padding_duration_ms, voice_activity_detector, audio_frames
    # # )

    # # # Segmenting the voice audio and save it in a list as bytes
    # # concatenated_audio = [segment for segment in audio_segments]

    # # joined_audio = b"".join([frame.data.tobytes() for frame in concatenated_audio])
    # # audio_data_array = np.frombuffer(joined_audio, dtype=np.int16)
    # # audio_object = Audio(data=audio_data_array, rate=sample_rate)

    # return audio_object


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
        audio_sample_rate = wf.getframerate()

        assert audio_sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, audio_sample_rate


def write_wave(path, audio, sample_rate):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, "wb")) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(audio_sample_rate)
        wf.writeframes(audio_data)


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
    n = int(audio_sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / audio_sample_rate) / 2.0
    while offset + n < len(audio_data):
        yield Frame(audio_data[offset : offset + n], timestamp, duration)
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
    audio_sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    voice_activity_detector - An instance of webrtcvad.Vad.
    audio_frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in audio_frames:
        is_speech = voice_activity_detector.is_speech(frame.bytes, audio_sample_rate)

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
                for frame, is_speech in ring_buffer:
                    voiced_frames.append(frame)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([frame for frame, is_speech in ring_buffer if not is_speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
                triggered = False
                yield b"".join([frame.bytes for frame in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write("-(%s)" % (frame.timestamp + frame.duration))
    sys.stdout.write("\n")
    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b"".join([f.bytes for f in voiced_frames])
