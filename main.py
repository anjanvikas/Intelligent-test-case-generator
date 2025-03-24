from extract_features import extract_understanding_blocks
from input_parser import read_frd_file
from test_case_generator import generate_test_cases_llm
from code_generator import LLMTestCodeGenerator
from code_executor import LLMTestExecutor
import json
import os

def main():
    try:
        # Read and parse FRD
        file_path = "test_data/parabank_frd.txt"
        frd_data = read_frd_file(file_path)
        
        # Extract understanding blocks
        llm_understanding = extract_understanding_blocks(frd_features=frd_data)
        
        # Generate test cases
        test_cases = generate_test_cases_llm(llm_understanding)
        
        # Save test cases
        test_cases_file = "test_outputs/test_cases_latest.json"
        with open(test_cases_file, 'w') as f:
            json.dump(test_cases, f, indent=2)

        # Generate test code using LLM
        try:
            test_generator = LLMTestCodeGenerator()
            generated_content = test_generator.generate_test_code(
                test_cases_file=test_cases_file
            )

            # Save test files
            test_generator.save_test_files(generated_content)
            print("✅ Test code has been generated successfully")

            # Run tests
            executor = LLMTestExecutor()
            results = executor.run_tests("tests")
            
            if results['success']:
                print("✅ Tests completed successfully!")
                print(f"Test report available at: {results['report']}")
            else:
                print(f"❌ Tests failed!")
                if results.get('error'):
                    print(f"Error: {results['error']}")

        except Exception as e:
            print(f"❌ Error generating/running tests: {str(e)}")
            raise

    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()