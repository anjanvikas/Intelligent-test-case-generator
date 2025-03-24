from typing import Dict, List
import json
from openai import OpenAI
import docker
import os
import subprocess

class LLMTestExecutor:
    def __init__(self):
        self.client = OpenAI()
        self.docker_client = docker.from_env()

    def generate_test_environment(self, requirements_file: str, tech_analysis: Dict) -> Dict[str, str]:
        """Generate appropriate test environment based on technology stack"""
        with open(requirements_file, 'r') as f:
            requirements = f.read()

        prompt = f"""
Generate test environment configuration for:
Application Type: {tech_analysis['app_type']}
Technology Stack: {tech_analysis['tech_stack']}
Testing Framework: {tech_analysis['test_framework']}

Requirements:
{requirements}

Generate:
1. Dockerfile appropriate for this tech stack
2. Docker Compose configuration
3. Environment variables
4. Any necessary setup scripts

The configuration should:
- Use appropriate base images for the tech stack
- Install all dependencies
- Set up test environment
- Configure test runners and coverage tools
- Handle framework-specific requirements

Return configurations as JSON with:
- dockerfile: Dockerfile content
- docker_compose: docker-compose.yml content
- env_vars: environment variables
- setup_scripts: any additional setup scripts
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a DevOps expert specializing in test environments."},
                {"role": "user", "content": prompt}
            ]
        )

        return json.loads(response.choices[0].message.content)

    def _analyze_test_requirements(self, test_cases: list) -> dict:
        """Analyze test cases to determine testing environment needs"""
        prompt = f"""
Analyze these test cases and determine the testing environment requirements.
Return a JSON object with the complete environment setup needed to run these tests.

Test Cases:
{json.dumps(test_cases, indent=2)}

Determine:
1. What type of testing is needed (API, Web UI, Database, etc.)?
2. What testing framework would be most appropriate?
3. What dependencies and configurations are required?

Return a JSON object with:
1. required_files: Map of filename to content for all necessary configuration files
2. setup_commands: List of commands needed to set up the environment
3. test_commands: List of commands to run the tests
4. report_path: Expected path where test reports will be generated

Example Response:
{{
    "required_files": {{
        "requirements-test.txt": "required dependencies",
        "pytest.ini": "pytest configuration",
        "conftest.py": "test fixtures and setup"
    }},
    "setup_commands": ["installation commands"],
    "test_commands": ["test execution commands"],
    "report_path": "path/to/report"
}}
"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in test automation setup. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            raise

    def _setup_environment(self, test_dir: str, env_config: dict) -> None:
        """Set up the test environment based on configuration"""
        # Create required files
        for filename, content in env_config['required_files'].items():
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")

        # Run setup commands
        for cmd in env_config['setup_commands']:
            try:
                subprocess.run(
                    cmd.split(),
                    check=True,
                    cwd=test_dir,
                    capture_output=True,
                    text=True
                )
                print(f"✅ Executed: {cmd}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Command failed: {cmd}")
                print(f"Error: {e.stderr}")
                raise

    def run_tests(self, test_dir: str, test_cases: list) -> Dict:
        """Run tests based on test case requirements"""
        try:
            # Analyze test cases and get environment configuration
            env_config = self._analyze_test_requirements(test_cases)
            
            # Set up the environment
            self._setup_environment(test_dir, env_config)
            
            # Run test commands
            results = []
            for cmd in env_config['test_commands']:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=test_dir
                )
                results.append(result)
            
            # Check if any test command failed
            success = all(r.returncode == 0 for r in results)
            
            # Combine outputs
            output = "\n".join(r.stdout for r in results)
            error = "\n".join(r.stderr for r in results if r.stderr)
            
            report_path = os.path.join(test_dir, env_config['report_path'])
            
            return {
                'success': success,
                'output': output,
                'error': error if not success else None,
                'report': report_path if os.path.exists(report_path) else None
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _create_test_requirements(self, test_dir: str) -> None:
        """Create test-specific requirements file"""
        # Ask LLM what dependencies are needed based on the generated test code
        with open(os.path.join(test_dir, "test_generated.py"), 'r') as f:
            test_code = f.read()

        prompt = f"""
Analyze this test code and list all Python packages required to run it.
Return ONLY a list of requirements in pip format (package>=version).
Example:
pytest>=7.0.0
selenium>=4.0.0

Test code:
{test_code}
"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python dependency expert. Return only a list of required packages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        requirements = response.choices[0].message.content.strip()
        
        # Always include basic test packages
        base_requirements = """
pytest>=7.0.0
pytest-html>=4.1.0
pytest-cov>=4.1.0
"""
        
        # Combine and write requirements
        with open(os.path.join(test_dir, "requirements-test.txt"), 'w') as f:
            f.write(base_requirements + "\n" + requirements)

        print("✅ Created test requirements file")

    def _get_test_command(self, tech_analysis: Dict) -> List[str]:
        """Get appropriate test command based on framework"""
        framework = tech_analysis['test_framework'].lower()
        
        # Framework-specific commands
        commands = {
            'pytest': ['pytest', '--cov', '--cov-report=html'],
            'jest': ['npm', 'test', '--coverage'],
            'junit': ['./gradlew', 'test'],
            'testng': ['mvn', 'test'],
            'mocha': ['mocha', '--coverage'],
            'rspec': ['rspec', '--format', 'documentation'],
            # Add more frameworks as needed
        }

        return commands.get(framework, ['pytest'])  # Default to pytest

    def _parse_test_results(self, output: str, tech_analysis: Dict) -> Dict:
        """Parse test results and coverage reports"""
        return {
            'success': True,
            'coverage_report': 'coverage/index.html',
            'test_report': 'report.html'
        } 