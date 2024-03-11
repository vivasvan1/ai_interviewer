import json
from logging import debug
import openai



def generate_metric(jdText=None):
    prompt = f"""Below are the details of the interview campaign.

{jdText}

We look forward to hearing your insights and experiences.

return 5 good metric in json format without any explaination or reason. keep the metric name at max made of 2 words.

format: {{ metrics:[metricname1,metricname2] }}
Example Response:
{{
"metrics": [
"Engagement",
"Alignment",
"Innovation",
"Leadership",
"Conflict Resolution"
]
}}"""

    api_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a HR manager and have to generate measurement metric for an interview campaign.",
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
    