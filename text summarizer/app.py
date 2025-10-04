from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

def gemini(prompt):
    import google.generativeai as genai

    # Replace with your Gemini API key from Google Cloud Console
    API_KEY = "YOUR_API_KEY"

    # Configure the API Key
    genai.configure(api_key=API_KEY)

    # Initialize Gemini Model (text-only model)
    model = genai.GenerativeModel('gemini-pro')


    response = model.generate_content(prompt)

    # Print the response
    print(response.text)


# Replace with your actual Gemini API endpoint and key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
GEMINI_API_KEY = "AIzaSyC3BBFPV22Ph7uT3lqggQIdP9uyIEFQNkg"

# Map summary length to prompt instructions
LENGTH_MAP = {
    "short": "Summarize the following text in 1-2 sentences.",
    "medium": "Summarize the following text in 3-5 sentences.",
    "long": "Summarize the following text in a detailed paragraph.",
    "longer": "Summarize the following text in multiple detailed paragraphs."
}

@app.route('/')
def index():
    return send_from_directory('.', 'text-summarizer.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text', '')
    length = data.get('length', 'medium')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    prompt = LENGTH_MAP.get(length, LENGTH_MAP['medium']) + "\n\n" + text

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload, timeout=30)
        print("Gemini API status:", response.status_code)
        print("Gemini API response:", response.text)
        response.raise_for_status()
        result = response.json()
        # Defensive extraction
        summary = None
        if (
            "candidates" in result and
            result["candidates"] and
            "content" in result["candidates"][0] and
            "parts" in result["candidates"][0]["content"] and
            result["candidates"][0]["content"]["parts"] and
            "text" in result["candidates"][0]["content"]["parts"][0]
        ):
            summary = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return jsonify({'error': 'Unexpected Gemini API response', 'details': result}), 500

        return jsonify({'summary': summary})
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Failed to summarize text', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
