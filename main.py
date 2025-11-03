import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import (
    schema_get_file_content,
    get_file_content,
)
from functions.run_python_file import schema_run_python_file, run_python_file
from functions.write_file import schema_write_file, write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)

    if verbose:
        print(
            f"Calling function: {function_name}"
            f"({function_call_part.args})"
        )
    else:
        print(f" - Calling function: {function_name}")

    # Add the working directory to the arguments
    function_args["working_directory"] = "./calculator"

    # Call the appropriate function based on the name
    if function_name == "get_files_info":
        function_result = get_files_info(**function_args)
    elif function_name == "get_file_content":
        function_result = get_file_content(**function_args)
    elif function_name == "run_python_file":
        function_result = run_python_file(**function_args)
    elif function_name == "write_file":
        function_result = write_file(**function_args)
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # Return the result as a types.Content
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


system_prompt = """

You are a helpful AI coding agent.
When a user asks a question or makes a request, make a function call plan.
You can perform the following operations:
- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory.
You do not need to specify the working directory in your function calls
as it is automatically injected for security reasons.

When executing Python files, if no arguments are specified by the user,
proceed with an empty arguments list. Do not ask for clarification.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

client = genai.Client(api_key=api_key)
user_prompt = sys.argv[1] if len(sys.argv) > 1 else exit("Provide a prompt!")
verbose = "--verbose" in sys.argv

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

# Loop to handle multiple turns of tool use
max_iterations = 20
for iteration in range(max_iterations):
    try:
        if verbose:
            print(f"\n=== Iteration {iteration + 1} ===")
        
        # Call generate_content with the entire messages list
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        if verbose:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        # Add all candidates' content to the messages list
        for candidate in response.candidates:
            messages.append(candidate.content)

        # Check if we have a final text response
        if response.text:
            print(response.text)
            break

        # Check for function calls and handle them
        function_responses = []
        has_function_calls = False
        
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.function_call:
                    has_function_calls = True
                    function_call_result = call_function(part.function_call, verbose)
                    
                    # Validate the response structure
                    if not function_call_result.parts[0].function_response.response:
                        raise RuntimeError(
                            "Function call result does not contain "
                            "expected response structure"
                        )
                    
                    # Print the result if verbose
                    if verbose:
                        response_data = (
                            function_call_result.parts[0].function_response.response
                        )
                        print(f"-> {response_data}")
                    
                    function_responses.append(function_call_result)
        
        # If there were function calls, add their responses to messages
        if has_function_calls and function_responses:
            # Combine all function responses into a single user message
            all_parts = []
            for func_response in function_responses:
                all_parts.extend(func_response.parts)
            
            messages.append(types.Content(role="user", parts=all_parts))
        elif not has_function_calls:
            # No function calls and no text response - end the loop
            if verbose:
                print("No function calls or text response. Ending loop.")
            break
            
    except Exception as e:
        print(f"Error during iteration {iteration + 1}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        break

if iteration == max_iterations - 1:
    print("Maximum iterations reached without a final response.")
