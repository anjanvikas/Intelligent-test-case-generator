# input_parser/api_parser.py

def parse_api_contracts(openapi_json: dict) -> list:
    """
    Parses OpenAPI JSON and prepares structured data suitable for LLM input.
    Returns a list of endpoint summaries for test case generation.
    """
    api_summaries = []

    paths = openapi_json.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            summary = details.get("summary", "No summary provided")
            parameters = details.get("parameters", [])

            param_list = []
            example_input = {}

            for param in parameters:
                name = param.get("name")
                location = param.get("in", "query")
                required = param.get("required", False)
                ptype = param.get("schema", {}).get("type", "string")

                param_list.append(f"{name} ({ptype}, in {location}, required={required})")
                example_input[name] = f"<{ptype}_value>"

            api_summaries.append({
                "endpoint": path,
                "method": method.upper(),
                "summary": summary,
                "parameters": param_list,
                "example_input": example_input,
                "llm_input": f"""
Endpoint: {path}
Method: {method.upper()}
Summary: {summary}
Parameters: {', '.join(param_list)}
Example Input: {example_input}
"""
            })

    return api_summaries

'''
{
  "endpoint": "/login",
  "method": "POST",
  "summary": "User login",
  "parameters": [
    "username (string, in query, required=True)",
    "password (string, in query, required=True)"
  ],
  "example_input": {
    "username": "<string_value>",
    "password": "<string_value>"
  },
  "llm_input": "\nEndpoint: /login\nMethod: POST\nSummary: User login\nParameters: username (string, in query, required=True), password (string, in query, required=True)\nExample Input: {'username': '<string_value>', 'password': '<string_value>'}\n"
}
'''