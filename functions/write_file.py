import os
from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=(
        "Writes or overwrites a file with the given content, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the file to write, relative to the "
                    "working directory."
                ),
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)


def write_file(working_directory, file_path, content):
    try:
        # Create the full path by joining working_directory and file_path
        full_path = os.path.join(working_directory, file_path)

        # Resolve the absolute paths to handle .. and symlinks
        resolved_full_path = os.path.realpath(full_path)
        resolved_working_dir = os.path.realpath(working_directory)

        # Check if the file_path is outside the working_directory
        is_outside = (
            not resolved_full_path.startswith(
                resolved_working_dir + os.sep
            )
            and resolved_full_path != resolved_working_dir
        )
        if is_outside:
            return (
                f'Error: Cannot write to "{file_path}" as it is outside '
                f'the permitted working directory'
            )

        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(resolved_full_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        # Write the content to the file
        with open(resolved_full_path, 'w') as file:
            file.write(content)

        # Return success message
        return (
            f'Successfully wrote to "{file_path}" '
            f'({len(content)} characters written)'
        )
    except Exception as e:
        return f'Error: {str(e)}'
