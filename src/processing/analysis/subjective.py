import json
import logging
import os
import openai
from supabase import Client, create_client
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage, BaseMessage


def generate_positive_analysis(
    history: ChatMessageHistoryWithJSON,
):
    chat = ChatOpenAI(temperature=0.7, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(
        SystemMessage(
            content="""given a transcript of an interview i want you to tell me 5 skills the candidate have. please respond in JSON with format {"skills":[{"skill":"valid_parsable_string","reason":"valid_parsable_string"}]}. If not enough data or improper candidate response return {"skills":[]}"""
        )
    )
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
    chat = ChatOpenAI(temperature=0.7, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(
        SystemMessage(
            content="""given a transcript of an interview i want you to tell me 5 things the candidate can improve upon. please respond in JSON with format {"points":[{"point":\"\"\"string\"\"\","reason":\"\"\"string\"\"\"}]}"""
        )
    )
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

def generate_overall_analysis(
    history: ChatMessageHistoryWithJSON
):
    chat = ChatOpenAI(temperature=0.7, openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY", ""))
    messages: list[BaseMessage] = []
    messages.append(
        SystemMessage(
            content="""
            given a transcript of an interview i want you to tell me the about the key points asked in the given json format.
            please respond in JSON with format and fill the vaues of the key.
            {
                "performance_summary": "Explain the candidates performance and analysis in 360 words.",
                "positives":["List of 5 skills of the candidate"]
                "improvements": ["List of 5 points on places where candidate could improve upon as pe the job description"]
                "communication_skills": {
                    "summary": "Textual summary on candidate communication skill",
                    "rating": "Rating of the candidate on this skill out of 10"
                },
                "technical_knowledge": {
                    "summary": "Textual summary of candidate's technical proficiency and understanding",
                    "rating": "Rating out of 10"
                },
                "problem_solving_skills": {
                    "summary": "Textual summary of candidate's approach to problem-solving, logic, and creativity",
                    "rating": "Rating out of 10"
                },
                "adaptability": {
                    "summary": "Textual summary of how well the candidate adapts to new questions or challenges",
                    "rating": "Rating out of 10"
                },
                "clarity_of_thought": {
                    "summary": "Textual summary of the candidate's clarity and coherence in their responses",
                    "rating": "Rating out of 10"
                },
                "engagement_and_interest": {
                    "summary": "Textual summary of how engaged and interested the candidate appeared",
                    "rating": "Rating out of 10"
                },
                "relevance_to_job_description": {
                    "summary": "How well the candidate's skills and experiences align with the job requirements",
                    "rating": "Rating out of 10"
                },
                "notable_quotes": [
                    "Significant or impactful quotes from the candidate"
                ],
                "follow_up_recommendations": "Suggestions for next steps, such as further technical evaluation or specific questions for follow-up interviews",
                "overall_rating": "Give an overall rating of the candidate's performance out of 10"
                }
                if unable to calculate a rating, just give a 0 rating.
                Dont use candidate name in the analysis.
            """
        )   
    )
    messages.append(HumanMessage(content=history.to_json()))
    out = chat(messages)
    
    return out.content


# Use the following key points to analyse: 
            
#             - If resume is provided then how much does the candidate experience match with the Job description.
#             - Summarize the candidate interview on the following point:
#                 -- clarity on the topics or questions asked. Give text and rating out of 10
#                 -- How proper answers were given i.e the communication skills. Give text and rating out of 10
#                 -- Problem solving ability of the candidate. Give text and rating out of 10
#                 -- How much professinalism the candidate have. Give text and rating out of 10
#                 -- Team work and adaptibilty of the candidate. Give text and rating out of 10
            
#             please respond in JSON with format 
#             {"jb_resemblence":"valid_parsable_string",
#                 "summary":"valid_parsable_string",
#                 "skills":[{"skill":"valid_parsable_string","reason":"valid_parsable_string"}]}
            
#             If not enough data to make analysis , then respond with empty object {}.