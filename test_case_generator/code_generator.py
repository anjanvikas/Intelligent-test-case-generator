def save_test_files(self, generated_content: Dict, output_dir: str = "tests") -> None:
    """Save generated test files"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save main test code
        with open(os.path.join(output_dir, "test_generated.py"), "w") as f:
            f.write(generated_content['test_code'])
        
        # Save pytest configuration
        with open(os.path.join(output_dir, "pytest.ini"), "w") as f:
            f.write("""[pytest]
addopts = -v --html=report.html --self-contained-html
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)
log_cli_date_format = %Y-%m-%d %H:%M:%S""")

        # Create empty requirements file (will be populated by executor)
        open(os.path.join(output_dir, "requirements-test.txt"), 'w').close()

        print("✅ Test files generated successfully")
        
    except Exception as e:
        print(f"⚠️ Error saving test files: {str(e)}")
        raise 