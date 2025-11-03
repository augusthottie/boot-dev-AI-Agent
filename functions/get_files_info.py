import os
from google.genai import types


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description=(
        "Lists files in the specified directory along with their sizes, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The directory to list files from, relative to the "
                    "working directory. If not provided, lists files in "
                    "the working directory itself."
                ),
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    # Create the full path by joining working_directory and directory
    full_path = os.path.join(working_directory, directory)

    # Normalize both paths to resolve any "..", ".", or symbolic links
    normalized_full_path = os.path.realpath(full_path)
    normalized_working_dir = os.path.realpath(working_directory)

    # Validate that the full path is within the working directory
    # Check if paths are equal OR if full_path starts with working_dir
    is_same_dir = normalized_full_path == normalized_working_dir
    is_subdir = normalized_full_path.startswith(
        normalized_working_dir + os.sep
    )
    if not (is_same_dir or is_subdir):
        error_msg = (
            f'Error: Cannot list "{directory}" as it is outside '
            f'the permitted working directory'
        )
        return error_msg

    # Check if the path is a directory
    try:
        if not os.path.isdir(normalized_full_path):
            return f'Error: "{directory}" is not a directory'

        # List the directory contents
        entries = os.listdir(normalized_full_path)

        # Build the output string
        result_lines = []
        for entry in entries:
            entry_path = os.path.join(normalized_full_path, entry)
            file_size = os.path.getsize(entry_path)
            is_dir = os.path.isdir(entry_path)
            result_lines.append(
                f"- {entry}: file_size={file_size} bytes, is_dir={is_dir}"
            )

        return "\n".join(result_lines)

    except Exception as e:
        return f"Error: {str(e)}"
