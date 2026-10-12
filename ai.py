from openai import OpenAI
import json


client = OpenAI(
        api_key="...................",
        base_url="https://api.mistral.ai/v1"

)


def analyze_resume(resume_text, user_goal):

    prompt = f"""
You are a senior software engineer and hiring manager.

I will provide you with a resume text and a user goal.

Evaluate the resume based on the user's goal.

User goal: {user_goal}

Strict rules:
- Extract only relevant skills for this goal.
- Remove irrelevant tools [example: Excel for backend developer].
- Identify real skill gaps.
- Generate roadmap only for missing fields.
- Make output different based on goal.

Return only JSON:

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

Resume text:
{resume_text}

"""


    try:

        response = client.chat.completions.create(

            model="mistral-small-latest",

            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

        )


        content = response.choices[0].message.content


        start = content.find("{")
        end = content.rfind("}") + 1


        return json.loads(content[start:end])


    except Exception as e:

        return {

            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)

        }
    




conversation = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def speak(text):
    global conversation

    conversation.append({
        "role": "user",
        "content": text
    })

    try:
        response = client.chat.completions.create(
            model="mistral-small-latest",
            messages=conversation
        )

        reply = response.choices[0].message.content

        conversation.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except Exception as e:
        print(e)
        return "Sorry, AI is not working."
