import requests
import os
from dotenv import load_dotenv

load_dotenv()

def read_github_file(file_path: str = None) -> str:
    """
    Read a Python file from GitHub repository.
    Returns the file content as a string.
    """
    token   = os.getenv("GITHUB_TOKEN")
    raw_url = os.getenv("GITHUB_RAW_URL")

    # If specific file path given, build URL dynamically
    if file_path:
        base = raw_url.rsplit("/", 1)[0]
        raw_url = f"{base}/{file_path}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw"
    }

    response = requests.get(raw_url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return f"Error: Could not read file. Status {response.status_code}"
