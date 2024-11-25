
from src.agent.simple import continueConversation, process_user_response, translateToAnother
from src.ai_names import AiNameAndVoice, VoiceType
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.tts import do_text_to_speech
from src.utils.audio import convert_audio_to_base64

class Conversation:
    def __init__(self):
        self.ai_voice: VoiceType = VoiceType.alloy
        self.history = ChatMessageHistoryWithJSON()
        self.language = "english"
        self.interview_type = 'campaign'
    
    def inititateConversation(self,voice:VoiceType,history: str,language: str,interview_type: str ):
        self.ai_voice = voice
        self.history.from_json(history)
        self.language = language
        msg = self.history.messages
        self.interview_type = interview_type
        
        if any(obj.type == "human" for obj in msg):
            ai_reply = continueConversation(self.history)
            ai_response_base64 = convert_audio_to_base64(
                do_text_to_speech(ai_reply, self.ai_voice)
            )
            if not ai_response_base64:
                raise ValueError("Failed to convert AI reply to base64 encoded audio")
            return {"response": ai_response_base64,"response_text": ai_reply, "history": self.history.to_json()}
        else:
            return self.getWelcomeMessage()
        
    def getWelcomeMessage(self,addToHisotry = True):
        voice_name = AiNameAndVoice().getName(self.ai_voice)
        ai_reply: str = (
            f"Hi there, this is {voice_name} . Your AI interviewer for today. Hope you are doing well. Shall we get started?"
        )
        if self.language != "english":
            ai_reply = translateToAnother(ai_reply,self.language)
        
        self.history.add_ai_message(ai_reply) 
    
        ai_response_base64 = convert_audio_to_base64(
            do_text_to_speech(ai_reply, self.ai_voice)
        )
        if not ai_response_base64:
            raise ValueError("Failed to convert AI reply to base64 encoded audio")
        return {"response": ai_response_base64, "response_text": ai_reply ,"history": self.history.to_json()}
    
    def process_reply(self,audio_data):
        ai_reply,feedback = process_user_response(audio_data, self.history, self.interview_type == 'practice')
        if not ai_reply:
            raise ValueError("AI reply is empty or null")

        ai_response_base64 = convert_audio_to_base64(
            do_text_to_speech(ai_reply, self.ai_voice)
        )
        
        if feedback is not None: 
            self.history.feedbacks.append(feedback)
        
        if not ai_response_base64:
            raise ValueError("Failed to convert AI reply to base64 encoded audio")
        return {"response": ai_response_base64,"response_text": ai_reply, "history": self.history.to_json(),"feedback": feedback}
        
        
        
        
        
    