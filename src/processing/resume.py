import shutil
from fastapi import UploadFile
import numpy as np
import openai
from pypdf import PdfReader
import tempfile

# from src.processing.tts import reset_llms
from langchain.schema import AIMessage, HumanMessage, SystemMessage


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
                "content": "You are an interviewer and given my resume and i want you to provide me a list of relevant questions from it. ",
            },
            {
                "role": "user",
                "content": f"Below is the resume of the candidate: {text}",
            },
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


def read_pdf(upload_file: UploadFile) -> str:
    text = ""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Save uploaded file to a temporary file
        shutil.copyfileobj(upload_file.file, temp_file)
        temp_file_path = temp_file.name

    # Read PDF from the temporary file
    reader = PdfReader(temp_file_path)
    for page in reader.pages:
        text += page.extract_text() or ""
        if reader.pages.index(page) + 1 != len(reader.pages):
            text += "\n\n"

    return text


def get_questions_from_resume_and_jd(path_to_resume: str, path_to_jd: str):
    # Read Resume
    resume_text = read_pdf(path_to_resume)
    # Read JD
    jd_text = read_pdf(path_to_jd)

    # Get the questions from GPT-3
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an interviewer and given a job description and my resume and i want you to provide me a list of 10 relevant questions starting 3 questions from my resume and then rest from job description. Return JSON output of structure \{ questions:[{question_text:string}] \}",
            },
            {
                "role": "user",
                "content": f"Job Description: {jd_text} and My Resume: {resume_text}",
            },
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


def process_resume_and_jd(resume_file, jd=None, questions=""):
    question_text = ""
    if jd == None or jd.filename == "":
        question_text = get_questions_from_resume(resume_file)
    else:
        question_text = get_questions_from_resume_and_jd(resume_file, jd)

    system_personality_prompt = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
    # system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
    system_response_prompt = """Ask only one question per response"""
    system_message = system_personality_prompt + system_response_prompt

    final_questions = (
        questions + " and " + question_text if questions else question_text
    )
    system_message = system_message.replace("{interview_questions}", final_questions)

    # out = chat(chat_messages)
    # ai_reply = json.loads(out.content)["message"]
    ai_reply: str = "Hi there this is Sam. Your AI Interviewer for today. Hope you are doing well. Shall we get started?"
    # chat_messages.append(AIMessage(content=ai_reply))
    return ai_reply, question_text, system_message
