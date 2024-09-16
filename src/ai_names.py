from enum import Enum

class VoiceType(Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

class AiNameAndVoice:
    def __init__(self):
        self.voice_to_name = {
            VoiceType.ALLOY:"Sam",
            VoiceType.ECHO: "Joy",
            VoiceType.FABLE: "Mo",
            VoiceType.ONYX: "Peter",
            VoiceType.NOVA: "Ria",
            VoiceType.SHIMMER: "Niya"
        }

    def getName(self, voice: VoiceType) -> str:
        return self.voice_to_name.get(voice)  