# test_case_generator/generator.py
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_test_cases_llm(understanding_json: dict) -> list:
    """
    Generates structured test cases using OpenAI GPT based on the understanding output.
    """
    prompt = f"""
You are a Seasoned QA engineer. Based on the following feature information, generate functional test cases.

Return a JSON array of test cases. Each test case should include:
- title
- steps (as list)
- expected_result
- type (positive, negative, edge case)

Feature:
{json.dumps(understanding_json, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    output = response.choices[0].message.content.strip()

    try:
        test_cases = json.loads(output)
    except json.JSONDecodeError:
        print("⚠️ Unable to parse LLM output as JSON. Returning raw string.")
        test_cases = [{"raw_response": output}]

    return test_cases
