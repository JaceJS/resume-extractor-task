from flask import Flask, request, jsonify
import requests, os

app = Flask(__name__)

# Get the OPENAI_API_KEY from .env file
openai_api_key = os.getenv(
    "OPENAI_API_KEY",
)


def fetch_openai_response(request_data):
    api_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    try:
        response = requests.post(api_endpoint, headers=headers, json=request_data)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to get response from OpenAI API: {str(e)}"}, 500


@app.route("/", methods=["POST"])
def index():
    try:
        request_data = request.get_json()
        resume_text = request_data.get("resume_text")

        # Validate the presence and type of resume_text
        if not resume_text or not isinstance(resume_text, str):
            return (
                jsonify(
                    {"error": "Field 'resume_text' is required and must be a string"}
                ),
                400,
            )

        openai_request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a recruiter looking at a resume. You want to extract the Skills and Work Experience from the resume.",
                },
                {
                    "role": "user",
                    "content": f"Give me a list of Skills and Work Experience from this resume: \n{resume_text}",
                },
            ],
            "max_tokens": 512,  # Adjust max_tokens as needed
            "temperature": 0,
        }

        response_data = fetch_openai_response(openai_request_data)
        # Extract the response content from the response data
        response_content = (
            response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        )

        return response_content

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
