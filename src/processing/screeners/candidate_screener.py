import json
from logging import debug
import openai

from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from langchain.schema import SystemMessage, AIMessage, HumanMessage


def generate_evaluation(history: ChatMessageHistoryWithJSON, metric: str):
    conversation_transcript = ""
    for message in history.messages:
        if type(message) == SystemMessage:
            continue
        elif type(message) == AIMessage:
            conversation_transcript += "Interviewer: " + message.content + "\n\n"
        elif type(message) == HumanMessage:
            conversation_transcript += "Candidate: " + message.content + "\n\n"

    prompt = f"""Below is a transcript of interview.

Transcript:
{conversation_transcript}
Candidate: End of interview.

Based on this evaluate the candidate on the {metric} with each metric out of 10 points. If there are bad or irrelevent candidate response then consider that and rate the cadidate lower.

return in json format without any explaination or reason. IMPORTANT: keep the metric name as it is.

format: {{ metrics:[{{metricname1: 7}},{{metricname2: 8}}] }}
Example Response:
{{
"metrics": [
{{"Engagement": 9}},
{{"Alignment": 9}},
{{"Innovation": 9}},
{{"Leadership": 3}},
{{"Conflict Resolution": 9}}
]
}}"""
    print(prompt)

    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a HR manager and have to evaluate a candidate on a specified matric based on interview transcript and resume of the candidate.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    print(api_response, "api_response")

    # Parse the 'choices' field from the API response
    if "choices" in api_response and len(api_response["choices"]) > 0:
        # Get the 'text' field from the first choice
        questions_text = api_response["choices"][0]["message"]["content"]
        debug(f"GPT-3 Response: {questions_text}")
        questions_json = json.loads(questions_text)
        return questions_json
    else:
        debug("Failed to get a valid response.")
        raise ValueError("Failed to get a valid response.")
