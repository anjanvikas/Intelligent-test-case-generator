# understanding_layer/extractor.py
from openai import OpenAI


import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_understanding_blocks(frd_features, user_stories=None, api_contracts=None):
    """
    Given parsed input from FRD, User Stories, and API Contracts,
    call LLM to extract structured testable units.
    """
    combined_input = """
You are an intelligent QA assistant. Analyze the following functional requirements and and list down all the features you may think of based on the functional requirements and extract the following structured JSON for all the features:

- feature_title: short name
- description: brief explanation
- expected_behaviors: list
- inputs: list of fields with valid/invalid values
- outputs: list of condition-result mappings
- validations: list of business rules
- edge_cases: list of tricky/unusual scenarios

FRD Features:
{}
""".format(
        '\n'.join(frd_features)
    )
# User Stories:
# {}

# API Contracts:
# {}


    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "user", "content": combined_input}
    ],
    temperature=0.3)

    return response.choices[0].message.content