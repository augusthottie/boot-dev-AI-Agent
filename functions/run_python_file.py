import os
import subprocess
from google.genai import types


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description=(
        "Executes a Python file with optional command-line arguments, "
        "constrained to the working directory."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description=(
                    "The path to the Python file to execute, relative to "
                    "the working directory."
                ),
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description=(
                    "Optional list of command-line arguments to pass to "
                    "the Python script."
                ),
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(working_directory, file_path, args=[]):
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
                f'Error: Cannot execute "{file_path}" as it is outside '
                f'the permitted working directory'
            )

        # Check if the file exists
        if not os.path.exists(resolved_full_path):
            return f'Error: File "{file_path}" not found.'

        # Check if the file is a Python file
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'

        # Execute the Python file using subprocess.run
        completed_process = subprocess.run(
            ['python3', resolved_full_path] + args,
            cwd=resolved_working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Format the output
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        exit_code = completed_process.returncode

        output_parts = []

        if stdout:
            output_parts.append(f'STDOUT:\n{stdout}')
        if stderr:
            output_parts.append(f'STDERR:\n{stderr}')

        if exit_code != 0:
            output_parts.append(f'Process exited with code {exit_code}')

        if not output_parts:
            return 'No output produced.'

        return '\n'.join(output_parts)

    except subprocess.TimeoutExpired:
        return 'Error: executing Python file: Process timed out after 30s'
    except Exception as e:
        return f'Error: executing Python file: {e}'
