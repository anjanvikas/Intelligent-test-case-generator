'''
=======frd_parser======
1. read the .txt/ .pdf / .docx file
2. according to enterprise frd template will parse the document
'''
def read_frd_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()