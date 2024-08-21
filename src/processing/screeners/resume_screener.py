import openai
import json
from typing import List


def chatgpt_prompt(model, prompts):
    """Function to interact with ChatGPT for generating responses."""
    response = openai.ChatCompletion.create(
        model=model, messages=prompts
    )
    return (
        response.choices[0].message["content"]
        if response.choices
        else "No response available."
    )


def get_embeddings(texts):
    """Fetch embeddings for a list of texts."""
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    return response["data"]


def calculate_similarity(embeddings1, embeddings2):
    """Calculate cosine similarity between two sets of embeddings."""
    from numpy import dot
    from numpy.linalg import norm

    # Cosine similarity
    cos_sim = dot(embeddings1, embeddings2) / (norm(embeddings1) * norm(embeddings2))
    return cos_sim


def resume_screener(resumesText:List[str], jdText: str) -> str:
    # Summarize the job description using ChatGPT
    jd_summary = chatgpt_prompt(
        "gpt-3.5-turbo",
        [
            {
                "role": "system",
                "content": "You are an assistant tasked with summarizing job descriptions.",
            },
            {"role": "user", "content": jdText},
        ],
    )

    # Convert job description summary and resumes into embeddings
    jd_embedding = get_embeddings([jd_summary])[0]["embedding"]
    resume_embeddings = get_embeddings(resumesText)
    results = []

    for index, resume in enumerate(resumesText):
        # Generate summary using ChatGPT
        summary = chatgpt_prompt(
            "gpt-3.5-turbo",
            [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant tasked with summarizing resumes. "
                        "Extract the candidate's name, email ID, and phone number (if available). "
                        "Return JSON of format "
                        '{"summary": "<summary>", "candidate_name": "<candidate_name>", "email": "<email>", "phone_number": "<phone_number>"}'
                    ),
                },
                {"role": "user", "content": resume},
            ],
        )


        embedding = resume_embeddings[index]
        if embedding:
            resume_embedding = embedding["embedding"]
            # Calculate semantic similarity
            similarity = calculate_similarity(jd_embedding, resume_embedding)

            # Generate concerns using ChatGPT based on the job description summary and resume
            concerns = chatgpt_prompt(
                "gpt-3.5-turbo",
                [
                    {
                        "role": "system",
                        "content": "You are an HR assistant. Generate concerns based on the resume and job description.",
                    },
                    {
                        "role": "user",
                        "content": f"Job Description Summary: {jd_summary}\nResume Summary: {summary}",
                    },
                ],
            )

            # Assuming mismatch if similarity is below a certain threshold
            mismatch = (
                "Low relevance to job description."
                if similarity < 0.5
                else "Relevant to job description."
            )

            # Structure the result for each resume
            result = {
                "summary": summary,
                "similarity_score": similarity,
                "concerns": concerns,
                "mismatches": mismatch,
            }

            results.append(result)

    # Sort results by similarity score
    results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return json.dumps(results, indent=4)


# # Example usage
# resumes = [
#     "Experienced project manager with skills in leadership, conflict resolution, and innovation.",
#     "Software developer proficient in Java, Python, and C++ with extensive experience in AI and machine learning.",
# ]
# jd = "Looking for a project manager with experience in leadership, innovation, and team management."

# # Call the function
# result = resume_screener(resumes, jd)
# print(result)
