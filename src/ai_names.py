from enum import Enum

class VoiceType(Enum):
    alloy = "alloy"
    echo = "echo"
    fable = "fable"
    onyx = "onyx"
    nova = "nova"
    shimmer = "shimmer"

class AiNameAndVoice:
    def __init__(self):
        self.voice_to_name = {
            VoiceType.alloy:"Sam",
            VoiceType.echo: "Joy",
            VoiceType.fable: "Mo",
            VoiceType.onyx: "Peter",
            VoiceType.nova: "Ria",
            VoiceType.shimmer: "Niya"
        }

    def getName(self, voice: VoiceType) -> str:
        voice_type = VoiceType(voice)
        return self.voice_to_name.get(voice_type)  