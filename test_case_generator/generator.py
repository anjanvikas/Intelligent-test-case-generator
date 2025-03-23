# test_case_generator/generator.py
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def save_test_cases(test_cases: list, output_dir: str = "test_outputs") -> str:
    """Save test cases to a JSON file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"test_cases_{timestamp}.json")
    
    # Write test cases to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2)
    
    return output_file

def generate_test_cases_llm(understanding_json: dict) -> list:
    """
    Generates structured test cases using OpenAI GPT based on the understanding output.
    Returns a list of comprehensive test cases covering functional, negative, and edge cases.
    """
    prompt = f"""
You are a Senior QA Engineer with extensive experience in test case design. Based on the following feature information, generate detailed and comprehensive test cases following industry best practices.

Guidelines for test case generation:
1. Cover all functional requirements thoroughly
2. Include positive test cases for happy path scenarios
3. Add negative test cases for error handling
4. Consider edge cases and boundary conditions
5. Include validation test cases
6. Consider data variations and combinations
7. Add performance-related test scenarios where applicable
8. Include security-related test cases if relevant

For each test case, provide:
- id: unique identifier (TC_XXX format)
- title: clear and descriptive title
- description: detailed test case description
- preconditions: list of required setup conditions
- test_data: specific test data to be used
- steps: detailed step-by-step instructions
- expected_result: detailed expected outcome
- type: [functional, negative, edge_case, validation, security, performance]
- priority: [high, medium, low]
- dependencies: any dependent test cases or requirements
- assumptions: any assumptions made

IMPORTANT: Return ONLY the JSON array without any markdown formatting or explanation text.

Feature Information:
{json.dumps(understanding_json, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a QA expert specializing in comprehensive test case design. Always return pure JSON without any markdown formatting or explanation text."},
                {"role": "user", "content": prompt}
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
            test_cases = json.loads(output)
            
            # Validate test case structure
            for test_case in test_cases:
                required_fields = ['id', 'title', 'description', 'steps', 'expected_result', 'type', 'priority']
                missing_fields = [field for field in required_fields if field not in test_case]
                if missing_fields:
                    print(f"⚠️ Warning: Test case missing required fields: {missing_fields}")
            
            # Save test cases to file
            output_file = save_test_cases(test_cases)
            print(f"\n✅ Test cases have been saved to: {output_file}\n")
            
            return test_cases

        except json.JSONDecodeError as e:
            print(f"⚠️ Error: Unable to parse LLM output as JSON: {str(e)}")
            print(f"Raw output: {output}")
            return [{"error": "Invalid JSON format", "raw_response": output}]

    except Exception as e:
        print(f"⚠️ Error generating test cases: {str(e)}")
        return [{"error": str(e)}]
