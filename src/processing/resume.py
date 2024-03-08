from logging import debug, info
import logging
import shutil
import openai
from pypdf import PdfReader
import tempfile
import fitz

# from src.processing.tts import reset_llms


def get_questions_from_file(text: str, document_name: str):
    debug("Text of document", document_name, " = ", text)
    # Get the questions from GPT-3
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are an interviewer and given this document and i want you to provide me a list of questions. ",
            },
            {
                "role": "user",
                "content": f"Below is the content of the document: \n{text}.",
            },
        ],
    )
    questions_text = ""
    questions_json = ""

    # Parse the 'choices' field from the API response
    if "choices" in api_response and len(api_response["choices"]) > 0:
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        debug(f"GPT-3 Response: {questions_text}")
        # questions_json = json.loads(questions_text)
    else:
        debug("Failed to get a valid response.")

    return questions_text


def read_pdf(upload_file: str) -> str:
    text = ""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Save uploaded file to a temporary file
        shutil.copyfileobj(upload_file, temp_file)
        temp_file_path = temp_file.name
    # Read PDF from the temporary file
    doc = fitz.open(temp_file_path)
    for page in doc:  # iterate the document pages
        text += page.get_text()  # get plain text encoded as UTF-8
    return text


def get_questions_from_resume_and_jd(resume_text: str, jd_text: str):
    # # Read Resume
    # resume_text = read_pdf(path_to_resume)
    # # Read JD
    # jd_text = read_pdf(path_to_jd)

    # Get the questions from GPT-3
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an interviewer and given these documents and i want you to provide me a list of questions from it. ",
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
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        debug(f"GPT-3 Response: {questions_text}")
        # questions_json = json.loads(questions_text)
    else:
        debug("Failed to get a valid response.")

    return questions_text


basic_questions = """Can you tell me about yourself?
What are your strengths and weaknesses?
Why do you want to work for this company?
Can you describe a challenging situation you've faced at work and how you handled it?
Where do you see yourself in five years?
How do you handle stress and pressure?
What is your greatest professional achievement?
What is your preferred work style or work environment?
Why should we hire you for this position?
Do you have any questions for us?"""


def process_resume_and_jd(
    resume_file=None, jd_file=None, resume_text=None, jd_text=None, questions=None
):
    final_questions = ""

    # No info was provided set question to default
    if (
        resume_file == None
        and resume_text == None
        and jd_file == None
        and jd_text == None
        and questions == None
    ):
        # Load Default Questions
        final_questions = basic_questions

    # Case: Some context was provided
    else:
        # Combine resume_text and resume_file if any one or both available
        full_resume_text = ""
        if resume_file:
            extracted_text = read_pdf(resume_file)
            full_resume_text += extracted_text + "\n\n"
        if resume_text:
            full_resume_text += resume_text + "\n\n"

        # Combine jd_text and jd_file if any one or both available
        full_jd_text = ""
        if jd_file:
            extracted_text = read_pdf(jd_file)
            full_jd_text += extracted_text + "\n\n"
        if jd_text:
            full_jd_text += jd_text + "\n\n"

        gen_question_text = ""
        if (not full_resume_text) and (not full_jd_text):
            # Direct Questions Provided.
            pass
        elif full_resume_text and (not full_jd_text):
            # Generate Question from Resume.
            gen_question_text = get_questions_from_file(full_resume_text, "resume")
        elif full_jd_text and (not full_resume_text):
            # Generate Question from JD.
            gen_question_text = get_questions_from_file(full_jd_text, "interview context")
        else:
            # Generate Question from Resume + JD.
            gen_question_text = get_questions_from_resume_and_jd(
                full_resume_text, full_jd_text
            )

        # Combine ProvidedQuestions with GeneratedQuestions
        final_questions = (
            (questions + " and " + gen_question_text)
            if questions and gen_question_text
            else (questions if not gen_question_text else gen_question_text)
        )
    debug("final_questions : "+ str(final_questions))
    system_personality_prompt = """You are smart friendly and formal interviewer and i want you to have a human voice call type conversation via chat with me ask me following questions {interview_questions} or something you think would be interesting to ask based on the response of user\n\n"""
    # system_response_prompt="""Please respond only in JSON of format { type:"interviewer",message:"message1"} and only one message\n\n"""
    system_response_prompt = """Ask only one question per response"""
    system_message = system_personality_prompt + system_response_prompt

    system_message = system_message.replace("{interview_questions}", final_questions)

    # out = chat(chat_messages)
    # ai_reply = json.loads(out.content)["message"]
    ai_reply: str= "" # just kept for historical purpose
    # ai_reply: str = f"Hi there this is {voice}. Your AI Interviewer for today. Hope you are doing well. Shall we get started?"
    # chat_messages.append(AIMessage(content=ai_reply))
    return ai_reply, final_questions, system_message
