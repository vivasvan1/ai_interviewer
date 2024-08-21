from logging import debug, info
import logging
import shutil
from typing import List
import openai
from pypdf import PdfReader
import tempfile
import fitz

from abc import ABC, abstractmethod

# from src.processing.tts import reset_llms


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

    # Parse the 'choices' field from the API response
    if "choices" in api_response and len(api_response["choices"]) > 0:
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        debug(f"GPT-3 Response: {questions_text}")
        # questions_json = json.loads(questions_text)
    else:
        debug("Failed to get a valid response.")

    return questions_text


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


def get_questions_from_resume_and_pre_generated_questions(
    resume_text: str, questions_list: List[str]
):
    # # Read Resume
    # resume_text = read_pdf(path_to_resume)
    # # Read JD
    # jd_text = read_pdf(path_to_jd)

    # Get the questions from GPT-3
    pre_generated_questions = "\n".join(questions_list)
    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an interviewer and given some pre generated questions and resume and i want you to provide me a list of modified questions so that they are more relevant to the resume. ",
            },
            {
                "role": "user",
                "content": f"Pre Generated Questions: {pre_generated_questions} and My Resume: {resume_text}",
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


class QuestionGenerationStrategy(ABC):

    @abstractmethod
    def generate(self, resume_text, jd_text, questions_list):
        pass


class DefaultQuestionStrategy(QuestionGenerationStrategy):
    def generate(self, resume_text, jd_text, questions_list):
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
        return basic_questions


class ResumeBasedQuestionStrategy(QuestionGenerationStrategy):
    def generate(self, resume_text, jd_text, questions_list):
        # Logic for generating questions based solely on resume text
        gen_question_text = get_questions_from_file(resume_text, "resume")

        return gen_question_text


class JDBasedQuestionStrategy(QuestionGenerationStrategy):

    def generate(self, resume_text, jd_text, questions_list):
        # Logic for generating questions based solely on job description text
        gen_question_text = get_questions_from_file(jd_text, "interview context")

        return gen_question_text


class CombinedResumeWithJobDescStrategy(QuestionGenerationStrategy):

    def generate(self, resume_text, jd_text, questions_list):
        # Logic for generating questions based on both resume and job description texts
        gen_question_text = get_questions_from_resume_and_jd(resume_text, jd_text)
        return gen_question_text


class CombinedResumeWithQuestionsStrategy(QuestionGenerationStrategy):
    def generate(self, resume_text, jd_text, questions_list):
        # Logic for generating questions based on both resume and job description texts
        gen_question_text = get_questions_from_resume_and_pre_generated_questions(
            resume_text, questions_list
        )
        return gen_question_text


class QuestionListStrategy(QuestionGenerationStrategy):

    def generate(self, resume_text, jd_text, questions_list):
        # Logic for generating questions based on both resume and job description texts
        gen_question_text = "\n".join(questions_list)
        return gen_question_text


def combine_file_content_and_text(file_path, text):
    """Combine the content of a PDF file with a given text

    Args:
        file_path (str): Path to the PDF file
        text (str): Any text to be added to the output

    Returns:
        str: The combined content of the PDF file and the given text
    """
    combined = ""
    if file_path:
        extracted_text = read_pdf(file_path)
        combined += extracted_text + "\n\n"
    if text:
        combined += text + "\n\n"
    return combined


def calculate_questions(
    resume_file=None,
    jd_file=None,
    resume_text=None,
    jd_text=None,
    questions=None,
    questions_list=[],
    is_dynamic=True,
):
    # Combine resume_text and resume_file if any one or both available
    full_resume_text = combine_file_content_and_text(resume_file, resume_text)

    # Combine jd_text and jd_file if any one or both available
    full_jd_text = combine_file_content_and_text(jd_file, jd_text)

    # Determine which strategy to use based on the inputs
    strategy = DefaultQuestionStrategy()
    if is_dynamic:
        if len(questions_list) > 0 and full_resume_text:
            strategy = CombinedResumeWithQuestionsStrategy()
        elif len(questions_list) > 0:
            strategy = QuestionListStrategy()
        elif full_resume_text and full_jd_text:
            strategy = CombinedResumeWithJobDescStrategy()
        elif full_resume_text:
            strategy = ResumeBasedQuestionStrategy()
        elif full_jd_text:
            strategy = JDBasedQuestionStrategy()
    else:
        if len(questions_list) > 0:
            strategy = QuestionListStrategy()


    gen_question_text = strategy.generate(
        full_resume_text, full_jd_text, questions_list
    )

    # Combine ProvidedQuestions with GeneratedQuestions
    final_questions = (
        (gen_question_text + "\n" + questions) if questions else gen_question_text
    )
    return final_questions


def process_resume_and_jd(
    resume_file=None,
    jd_file=None,
    resume_text=None,
    jd_text=None,
    questions=None,
    questions_list=[],
    is_dynamic=True,
    voice="alloy",
):
    print(
        "process_resume_and_jd",
        resume_file,
        jd_file,
        resume_text,
        jd_text,
        questions,
        questions_list,
        is_dynamic,
    )
    final_questions = calculate_questions(
        resume_file,
        jd_file,
        resume_text,
        jd_text,
        questions,
        questions_list,
        is_dynamic,
    )
    debug("final_questions : " + str(final_questions))
    system_personality_prompt = (
        f"""You are smart friendly and formal interviewer and I want you to have a human voice call type conversation via chat with me ask me following questions {final_questions} or something you think would be interesting to ask based on the response of user."""
        + (
            "You may also ask follow up question if needed based on user's response"
            if is_dynamic
            else ""
        )
        + "\n\n"
    )
    print("system_personality_prompt", system_personality_prompt)
    system_response_prompt = """Ask only one question per response"""
    system_message = system_personality_prompt + system_response_prompt

    # out = chat(chat_messages)
    # ai_reply = json.loads(out.content)["message"]
    ai_reply: str = (
        f"Hi there, this is {('Sam' if voice == 'alloy' else voice.capitalize())}. Your AI interviewer for today. Hope you are doing well. Shall we get started?"
    )

    return ai_reply, final_questions, system_message
