'''
======user_stories_parser.py=======
1. fetchs the application specific user stories from jira
'''
def read_user_stories_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()