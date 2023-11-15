import numpy as np
import nltk  # we'll use this to split into sentences

nltk.download("punkt")

from IPython.display import Audio
import base64
from src.agent.simple import stt_model, conversation
import torch
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.chat_models import ChatOpenAI

from transformers import BarkModel

model = BarkModel.from_pretrained("suno/bark-small")
import torch

device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)

from transformers import AutoProcessor

voice_preset = "v2/en_speaker_6"

processor = AutoProcessor.from_pretrained("suno/bark-small")
from optimum.bettertransformer import BetterTransformer

# Use bettertransform for flash attention
model = BetterTransformer.transform(model, keep_original_model=False)

system_personality_prompt = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Vaato and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
# system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
system_response_prompt = """Ask only one question per response"""

# def reset_llms():
#   global chat,chat_messages
#   #RESET
#   chat = ChatOpenAI()


#   chat_messages = [SystemMessage(content=system_personality_prompt+system_response_prompt)]

device = "cuda:0" if torch.cuda.is_available() else "cpu"


def do_text_to_speech(script):
    sentences = nltk.sent_tokenize(script)

    SPEAKER = "v2/en_speaker_6"
    SAMPLE_RATE = model.generation_config.sample_rate

    silence = np.zeros(int(0.25 * SAMPLE_RATE))  # quarter second of silence

    pieces = []

    with torch.inference_mode():
        text_prompt = sentences
        voice_preset = "v2/en_speaker_6"

        inputs = processor(text_prompt, voice_preset=voice_preset).to(device)
        output = model.generate(**inputs)

    for sentence in output:
        # audio_array = generate_audio(sentence, history_prompt=SPEAKER)
        pieces += [sentence.cpu().numpy(), silence.copy()]

    ai_audio_obj = np.concatenate(pieces)

    vad = webrtcvad.Vad()

    # Define frame duration and padding duration
    frame_duration_ms = 30
    padding_duration_ms = 300

    # Apply VAD collector directly to ai_audio_obj
    frames = frame_generator(frame_duration_ms, ai_audio_obj, SAMPLE_RATE)
    frames = list(frames)
    segments = vad_collector(
        SAMPLE_RATE, frame_duration_ms, padding_duration_ms, vad, frames
    )

    # Segmenting the voice audio and save it in a list as bytes
    concataudio = [segment for segment in segments]

    joinedaudio = b"".join([frame.data.tobytes() for frame in concataudio])
    audio_array = np.frombuffer(joinedaudio, dtype=np.int16)
    audio_obj = Audio(data=audio_array, rate=SAMPLE_RATE)

    return audio_obj


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, data, timestamp, duration):
        self.data = data
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the audio data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
    num_frames = len(audio) // frame_size
    for i in range(num_frames):
        start = i * frame_size
        end = start + frame_size
        timestamp = float(start) / sample_rate
        duration = float(frame_size) / sample_rate
        yield Frame(audio[start:end], timestamp, duration)


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
        is_speech = vad.is_speech(frame.data.tobytes(), sample_rate)

        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
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
                triggered = False
                yield b"".join([f.data.tobytes() for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []

    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        yield b"".join([f.data.tobytes() for f in voiced_frames])
