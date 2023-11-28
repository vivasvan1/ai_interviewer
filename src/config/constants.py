# src/config/constants.py

SYSTEM_PERSONALITY_PROMPT = "You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me start out by introducing yourself as AI Interviewer called Vaato and then ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user. Dont divert from asking questions\n\n"

POSITIVE_ANALYSIS_PROMPT = """given a transcript of an interview i want you to tell me 5 skills the candidate have. please respond in JSON with format {"skills":[{"skill":<skill>,"reason":<reason>}]}"""

IMPROVEMENT_ANALYSIS_PROMPT = """given a transcript of an interview i want you to tell me 5 things the candidate can improve upon. please respond in JSON with format {"points":[{"point":<point_name>,"reason":<reason>}]}"""
