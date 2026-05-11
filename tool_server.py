from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Tool server is running!"

@app.route("/read_github_file", methods=["POST"])
def read_github_file():
    data      = request.json
    file_path = data.get("file_path", "app.py")
    token     = os.getenv("GITHUB_TOKEN")
    base_url  = os.getenv("GITHUB_RAW_URL")

    base    = base_url.rsplit("/", 1)[0]
    raw_url = f"{base}/{file_path}"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw"
    }

    response = requests.get(raw_url, headers=headers)

    if response.status_code == 200:
        return jsonify({"content": response.text})
    else:
        return jsonify({"error": f"Could not read file. Status {response.status_code}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
