from typing import Dict, List, Optional
import json
import os
from openai import OpenAI
from pathlib import Path

class LLMTestCodeGenerator:
    def __init__(self):
        self.client = OpenAI()

    def _analyze_tech_stack(self, requirements: str, test_cases: List[Dict]) -> Dict[str, str]:
        """Analyze requirements and test cases to determine technology stack"""
        prompt = f"""
Analyze the following requirements and test cases to determine:
1. Type of application (web, mobile, desktop, API, etc.)
2. Technology stack and frameworks
3. Appropriate testing frameworks and tools
4. Required test dependencies

Requirements:
{requirements}

Test Cases:
{json.dumps(test_cases, indent=2)}

Return a JSON object with:
- app_type: type of application
- tech_stack: main technologies used
- test_framework: recommended testing framework
- dependencies: list of required testing dependencies
- test_structure: recommended test structure
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in test automation architecture."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)

    def _create_test_code_prompt(self, test_cases: List[Dict], requirements: str, tech_analysis: Dict) -> str:
        """Create dynamic prompt based on technology stack analysis"""
        return f"""
Generate test code for the following test cases based on the analyzed technology stack.
The code must be valid syntax and follow best practices for the identified framework.

Application Type: {tech_analysis['app_type']}
Technology Stack: {tech_analysis['tech_stack']}
Testing Framework: {tech_analysis['test_framework']}

Requirements:
{requirements}

Test Cases:
{json.dumps(test_cases, indent=2)}

Generate complete test code that:
1. Uses the appropriate testing framework ({tech_analysis['test_framework']})
2. Implements all test cases
3. Includes proper setup and teardown
4. Has appropriate assertions and verifications
5. Handles errors and edge cases
6. Follows best practices for the identified technology stack
7. Includes necessary mocks and stubs if required
8. Implements proper test isolation

The code should be production-ready and follow the identified framework's conventions.
Return only the code without any explanation or markdown formatting.
"""

    def generate_test_code(self, test_cases_file: str, requirements_file: str) -> Dict[str, str]:
        """Generate appropriate test code based on application type and test cases"""
        try:
            # Read inputs
            with open(test_cases_file, 'r') as f:
                test_cases = json.load(f)
            
            with open(requirements_file, 'r') as f:
                requirements = f.read()

            # Analyze technology stack
            tech_analysis = self._analyze_tech_stack(requirements, test_cases)
            
            # Generate framework-specific code
            test_code = self._generate_framework_specific_code(test_cases, requirements, tech_analysis)
            
            # Generate necessary configuration files
            config_files = self._generate_config_files(tech_analysis)
            
            return {
                'test_code': test_code,
                'config_files': config_files,
                'tech_analysis': tech_analysis
            }

        except Exception as e:
            print(f"⚠️ Error generating test code: {str(e)}")
            raise

    def _generate_framework_specific_code(self, test_cases: List[Dict], requirements: str, 
                                        tech_analysis: Dict) -> str:
        """Generate code specific to the identified testing framework"""
        prompt = self._create_test_code_prompt(test_cases, requirements, tech_analysis)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""You are an expert in {tech_analysis['test_framework']} testing.
                Generate only valid test code following the framework's best practices."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        return self._clean_generated_code(response.choices[0].message.content)

    def _generate_config_files(self, tech_analysis: Dict) -> Dict[str, str]:
        """Generate necessary configuration files for the testing framework"""
        prompt = f"""
Generate configuration files needed for {tech_analysis['test_framework']} testing.
Include:
1. Framework configuration
2. Test runner configuration
3. Coverage tool configuration
4. Environment configuration
5. Any other necessary setup files

Return a JSON object where keys are file names and values are file contents.
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in test configuration and setup."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        return json.loads(response.choices[0].message.content)

    def _clean_generated_code(self, code: str) -> str:
        """Clean up generated code and ensure proper formatting"""
        # Remove markdown if present
        if "```" in code:
            code = code[code.find("```") + 3:]
            code = code[:code.rfind("```")]
        
        return code.strip()

    def save_test_files(self, generated_content: Dict[str, str], output_dir: str = "tests") -> None:
        """Save generated test code and configuration files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main test code
        with open(os.path.join(output_dir, "test_generated.py"), "w") as f:
            f.write(generated_content['test_code'])
        
        # Save configuration files
        for filename, content in generated_content['config_files'].items():
            with open(os.path.join(output_dir, filename), "w") as f:
                f.write(content) 