import numpy as np
import openai
from pypdf import PdfReader

# from src.processing.tts import reset_llms
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)


def get_questions_from_resume(path_to_resume: str):
    # Read PDF
    reader = PdfReader(path_to_resume)
    page = reader.pages[0]
    text = page.extract_text()

    # Get the questions from GPT-3
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",

        messages=[
            {
                "role": "system",
                "content": "You are an interviewer and given my resume and i want you to provide me a list of relevant questions from it. Return on JSON output of structure \{ questions:[{question_text:string}] \}",
            },
            {"role": "user", "content": f"Below is the resume of the candidate: {text}"},
        ],
    )
    questions_text = ""
    questions_json = ""

    # Parse the 'choices' field from the API response
    if "choices" in api_response and len(api_response["choices"]) > 0:
        print(api_response["choices"])
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        print(f"GPT-3 Response: {questions_text}")
        # questions_json = json.loads(questions_text)
    else:
        print("Failed to get a valid response.")

    return questions_text


def get_questions_from_resume_and_jd(path_to_resume:str,path_to_jd:str):
    # Read PDF
    reader = PdfReader(path_to_resume)
    resume_text = ""
    for page in reader.pages:
      resume_text += page.extract_text()
      if(reader.pages.index(page)+1!=len(reader.pages)):
        resume_text+="\n\n"

    reader = PdfReader(path_to_jd)
    jd_text = ""
    for page in reader.pages:
      jd_text += page.extract_text()
      if(reader.pages.index(page)+1!=len(reader.pages)):
        jd_text+="\n\n"

    # Get the questions from GPT-3
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",

        messages=[
            {
                "role": "system",
                "content": "You are an interviewer and given a job description and my resume and i want you to provide me a list of 10 relevant questions starting 3 questions from my resume and then rest from job description. Return JSON output of structure \{ questions:[{question_text:string}] \}",
            },
            {"role": "user", "content": f"Job Description: {jd_text} and My Resume: {resume_text}"},
        ],
    )
    questions_text = ""
    questions_json = ""

    # Parse the 'choices' field from the API response
    if "choices" in api_response and len(api_response["choices"]) > 0:
        print(api_response["choices"])
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        print(f"GPT-3 Response: {questions_text}")
        # questions_json = json.loads(questions_text)
    else:
        print("Failed to get a valid response.")

    return questions_text

def process_resume_and_jd(resume_file, jd=None):
    
    question_text = ""
    if(jd==None or jd.filename==""):
      question_text = get_questions_from_resume(resume_file)
    else:
      question_text = get_questions_from_resume_and_jd(resume_file,jd)
    # chat_messages[0].content = chat_messages[0].content.replace("{interview_questions}", question_text)
    # out = chat(chat_messages)
    # ai_reply = json.loads(out.content)["message"]
    ai_reply:str = "Hi there this is Sam.your AI Interviewer for today Hope you are doing well. Shall we get started?"
    # chat_messages.append(AIMessage(content=ai_reply))
    return ai_reply
