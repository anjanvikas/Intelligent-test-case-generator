from extract_features import extract_understanding_blocks
from input_parser import read_frd_file
from test_case_generator import generate_test_cases_llm
import json

def main():
    try:
        # Read and parse FRD
        file_path = "test_data/frd.txt"
        frd_data = read_frd_file(file_path)
        
        # Extract understanding blocks
        llm_understanding = extract_understanding_blocks(frd_features=frd_data)
        
        # Convert string to JSON if needed
        if isinstance(llm_understanding, str):
            try:
                llm_understanding = json.loads(llm_understanding)
            except json.JSONDecodeError:
                print("⚠️ Warning: Could not parse understanding blocks as JSON")
        
        # Generate test cases
        test_cases = generate_test_cases_llm(llm_understanding)
        
        # Test cases are automatically saved to file by the generator
        print("✅ Process completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in main process: {str(e)}")

if __name__ == "__main__":
    main()