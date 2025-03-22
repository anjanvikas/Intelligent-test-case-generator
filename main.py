from extract_features import extract_understanding_blocks
from input_parser import read_frd_file
from test_case_generator import generate_test_cases_llm
def main():
    file_path="test_data/frd.txt"
    frd_data = read_frd_file(file_path)
    llm_understanding = extract_understanding_blocks(frd_features=frd_data)
    print(generate_test_cases_llm(llm_understanding))

if __name__ == "__main__":
    main()