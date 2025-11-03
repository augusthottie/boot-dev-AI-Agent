import os
from google.genai import types
from functions.config import MAX_FILE_CONTENT_LENGTH


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=(
        "Reads and returns the contents of a file, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the file to read, relative to the "
                    "working directory."
                ),
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory, file_path):
    try:
        # Create the full path by joining working_directory and file_path
        full_path = os.path.join(working_directory, file_path)
        # If the file_path is outside the working_directory, return an error:
        if not full_path.startswith(working_directory):
            return (
                f'Error: Cannot read "{file_path}" as it is outside '
                f'the permitted working directory'
            )
        # If the file_path is not a file, return a string with an error:
        if not os.path.isfile(full_path):
            return (
                f'Error: File not found or is not a regular file: '
                f'"{file_path}"'
            )
        # Read the file and return the content
        with open(full_path, 'r') as file:
            content = file.read()
        # Truncate if content exceeds MAX_FILE_CONTENT_LENGTH
        if len(content) > MAX_FILE_CONTENT_LENGTH:
            content = (
                content[:MAX_FILE_CONTENT_LENGTH] +
                f'[...File "{file_path}" truncated at '
                f'{MAX_FILE_CONTENT_LENGTH} characters]'
            )
        return content
    except Exception as e:
        return f'Error: {str(e)}'
