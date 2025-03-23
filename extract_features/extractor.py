# understanding_layer/extractor.py
from openai import OpenAI
import os
import json
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def validate_feature_structure(feature):
    """Validates the extracted feature structure"""
    required_fields = [
        'feature_title',
        'description',
        'expected_behaviors',
        'inputs',
        'outputs',
        'validations',
        'edge_cases'
    ]
    
    missing_fields = [field for field in required_fields if field not in feature]
    if missing_fields:
        print(f"⚠️ Warning: Feature missing required fields: {missing_fields}")
        return False
    return True

def extract_understanding_blocks(frd_features, user_stories=None, api_contracts=None):
    """
    Given parsed input from FRD, User Stories, and API Contracts,
    extracts structured testable units with comprehensive feature analysis.
    """
    combined_input = f"""
You are an expert Business Analyst and QA Architect. Analyze the following requirements and extract detailed, testable features. For each feature, provide a comprehensive structured analysis that will be used for test case generation.

Guidelines for feature extraction:
1. Break down complex requirements into atomic, testable features
2. Identify all explicit and implicit requirements
3. Capture business rules and validation logic
4. Document dependencies between features
5. Identify potential risk areas and edge cases
6. Consider security and performance aspects
7. Note any assumptions or constraints

For each feature, provide the following structure:
{{
    "feature_title": "Short, descriptive name",
    "feature_id": "FT_XXX format",
    "description": "Detailed feature description",
    "priority": "high/medium/low",
    "dependencies": ["List of dependent features or systems"],
    "expected_behaviors": [
        "List of specific behaviors the feature should exhibit"
    ],
    "inputs": [
        {{
            "field": "Input field name",
            "type": "Data type",
            "valid_values": ["List of valid values or ranges"],
            "invalid_values": ["List of invalid values or conditions"],
            "constraints": ["Any constraints or validation rules"]
        }}
    ],
    "outputs": [
        {{
            "condition": "Specific condition",
            "expected_result": "Expected output or behavior",
            "error_handling": "How errors should be handled"
        }}
    ],
    "validations": [
        "List of business rules and validation requirements"
    ],
    "edge_cases": [
        "List of boundary conditions and special scenarios"
    ],
    "performance_requirements": [
        "Any performance-related requirements"
    ],
    "security_considerations": [
        "Security-related aspects to consider"
    ],
    "assumptions": [
        "List of assumptions made"
    ]
}}

IMPORTANT: Return ONLY the JSON array without any markdown formatting or explanation text.

Requirements to analyze:
FRD Features:
{'\n'.join(frd_features)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in requirements analysis and feature extraction. Always return pure JSON without any markdown formatting or explanation text."},
                {"role": "user", "content": combined_input}
            ],
            temperature=0.2,
            max_tokens=4000
        )

        output = response.choices[0].message.content.strip()
        
        # Remove any markdown formatting or explanation text
        if "```json" in output:
            output = output[output.find("["):output.rfind("]")+1]
        elif "```" in output:
            output = output[output.find("["):output.rfind("]")+1]
        
        try:
            features = json.loads(output)
            
            # Validate each feature's structure
            if isinstance(features, list):
                for feature in features:
                    validate_feature_structure(feature)
            elif isinstance(features, dict):
                validate_feature_structure(features)
            
            return features
            
        except json.JSONDecodeError as e:
            print(f"⚠️ Error: Unable to parse LLM output as JSON: {str(e)}")
            print(f"Raw output: {output}")
            return {"error": "Invalid JSON format", "raw_response": output}
            
    except Exception as e:
        print(f"⚠️ Error extracting features: {str(e)}")
        return {"error": str(e)}