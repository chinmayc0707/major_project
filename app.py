from flask import Flask, render_template, request, send_from_directory
import os
import subprocess
import requests
from urllib.parse import urlparse
import assemblyai

app = Flask(__name__)

import requests
import json

def english_to_kanglish_llm(text, api_key, temperature=0.3):
    """
    Convert English text to Kanglish using Mistral 7B Instruct via OpenRouter API.
    
    Args:
        text (str): English text to convert to Kanglish
        api_key (str): Your OpenRouter API key
        temperature (float): Response creativity (0-1, lower = more consistent)
    
    Returns:
        str: Kanglish text (Kannada in English script)
    """
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Detailed prompt for Kanglish conversion
    system_prompt = """You are an expert in Kannada language and transliteration. Your task is to convert English text to 'Kanglish' - which is Kannada written in English script (Roman script).



Examples:
- "Hello" → "namaskara" or "hello" (commonly used)
- "How are you?" → "hegiddira?" 
- "Thank you" → "dhanyavadagalu"
- "Good morning" → "suprabhaata"

Convert the following English text to Kanglish:"""

    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": [
            
            {"role": "user", "content": f'''
You are an expert in Kannada language and transliteration. Your task is to convert English text to 'Kanglish' - which is Kannada written in English script (Roman script).



Examples:
- "Hello" → "namaskara" or "hello" (commonly used)
- "How are you?" → "hegiddira?" 
- "Thank you" → "dhanyavadagalu"
- "Good morning" → "suprabhaata"

Convert the following English text to Kanglish:
{text}'''}
        ],
        "temperature": temperature,
        "max_tokens": 500,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        kanglish_text = result["choices"][0]["message"]["content"].strip()
        
        # Clean up any extra explanations from the LLM response
        if '\n' in kanglish_text:
            lines = kanglish_text.split('\n')
            # Take the first non-empty line as the main conversion
            for line in lines:
                if line.strip() and not line.startswith('Note:') and not line.startswith('Explanation:'):
                    return line.strip()
        
        return kanglish_text
        
    except Exception as e:
        return f"Error: {str(e)}"

# Enhanced version with conversation context
def kanglish_converter_with_context(api_key):
    """
    Create a Kanglish converter with conversation memory for better context.
    """
    
    def convert_with_examples(text, custom_examples=None):
        """
        Convert text with custom examples for better accuracy.
        
        Args:
            text (str): English text to convert
            custom_examples (list): List of (english, kanglish) example pairs
        """
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build examples section
        examples_text = ""
        if custom_examples:
            examples_text = "\nAdditional examples:\n"
            for eng, kan in custom_examples:
                examples_text += f'- "{eng}" → "{kan}"\n'
        
        system_prompt = f"""You are a Kannada language expert. Convert English text to Kanglish (Kannada written in Roman/English script).

Key principles:
1. Translate meaning to Kannada, then write phonetically in English
2. Maintain natural Kannada sentence structure
3. Use common Kanglish words where they exist
4. Add inherent 'a' vowel after consonants as per Kannada phonetics

Standard examples:
- "Hello" → "namaskara"
- "How are you?" → "hegiddira?"
- "What is your name?" → "nimma hesaru enu?"
- "I am fine" → "naanu chennagi iddene"
- "Thank you" → "dhanyavadagalu"
- "Good" → "chennaagi"
- "Water" → "neeru"
- "Food" → "oota"
{examples_text}

Convert this English text to natural Kanglish: "{text}"

Provide only the Kanglish conversion, nothing else."""

        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [
                {"role": "user", "content": system_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    return convert_with_examples

def allowed_audio(filename):
    return any(filename.lower().endswith(ext) for ext in ['.mp3', '.wav', '.m4a'])

def allowed_video(filename):
    return any(filename.lower().endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm'])

def download_file(url, destination):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(destination, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Downloaded file to:", destination)
    return destination


import requests
import json
from typing import Optional, Dict, Any

class TextSummarizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat-v3.1:free"
    
    def summarize(self, 
                 text: str, 
                 summary_type: str = "general",
                 max_tokens: int = 300,
                 temperature: float = 0.7) -> str:
        """
        Summarize text with different summary types.
        
        Args:
            text: Text to summarize
            summary_type: Type of summary ("general", "bullet_points", "executive", "key_facts")
            max_tokens: Maximum tokens for summary
            temperature: Response creativity (0-1)
        
        Returns:
            Summarized text
        """
        
        system_prompts = {
            "general": "Provide a concise summary highlighting the main points.",
            "bullet_points": "Summarize the text as bullet points covering the key information.",
            "executive": "Create an executive summary focusing on the most important takeaways.",
            "key_facts": "Extract and list the key facts and figures from the text."
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompts.get(summary_type, system_prompts["general"])
                },
                {
                    "role": "user", 
                    "content": f"Text to summarize:\n\n{text}"
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def batch_summarize(self, texts: list, **kwargs) -> list:
        """Summarize multiple texts."""
        return [self.summarize(text, **kwargs) for text in texts]


def call_ai_summarization_api(text, language):
    # This is a placeholder for calling an actual AI summarization API.
    # You should replace this with your actual API call.
    # For example, you could use a library like `transformers` or a service like OpenAI.
    # 
    # Example using a hypothetical API:
    # 
    # import requests
    # 
    # api_url = "https://api.example.com/summarize"
    # headers = {"Authorization": "Bearer YOUR_API_KEY"}
    # data = {"text": text, "language": language}
    # try:
    #     response = requests.post(api_url, headers=headers, json=data)
    #     response.raise_for_status()  # Raise an exception for bad status codes
    #     return response.json()["summary"]
    # except requests.exceptions.RequestException as e:
    #     print(f"Error calling summarization API: {e}")
    #     return ""

    # For now, we will return a dummy summary based on the language.
    if language == "kannada":
        return "ಇದು AI ನಿಂದ ರಚಿತವಾದ ಕನ್ನಡ ಸಾರಾಂಶವಾಗಿದೆ."
    elif language == "kanglish":
        return kanglish_converter_with_context('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')(text, [])
    elif language == "english":
        return TextSummarizer("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").summarize(text, summary_type="key_facts").strip()
    else:
        return ""

def generate_summaries(text):
    if not text:
        return {
            "kannada": "",
            "kanglish": "",
            "english": ""
        }

    # Truncate text to avoid errors with APIs that have a character limit
    max_length = 5000
    if len(text) > max_length:
        text = text[:max_length]

    try:
        kannada_summary = call_ai_summarization_api(text, "kannada")
        kanglish_summary = call_ai_summarization_api(text, "kanglish")
        english_summary = call_ai_summarization_api(text, "english")
    except Exception as e:
        print(f"Error generating summaries: {e}")
        return {
            "kannada": "",
            "kanglish": "",
            "english": ""
        }

    return {
        "kannada": kannada_summary,
        "kanglish": kanglish_summary,
        "english": english_summary
    }

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint for handling file uploads (audio or video).
@app.route('/index-result.html', methods=['GET', 'POST'])
def page2():
    result = ""
    summaries = {"kannada": "", "kanglish": "", "english": ""}
    audio_file = ""
    if request.method == 'POST':
        data = request.files.get('audioFile') or request.files.get('videoFile')
        if data:
            
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            file_path = os.path.join(upload_dir, data.filename)
            data.save(file_path)
            print(f"Received file: {data.filename}")
            # Simply transcribe the file without conversion.
            result=assemblyai.transcribe_local_file(file_path)
            print(f'{result=}')
            if result:
                summaries = generate_summaries(result)
            audio_file = data.filename
        else:
            print("No file received in the form data.")
    return render_template('index-result.html', transcription=result, audio_file=audio_file, kannada_summary=summaries["kannada"], kanglish_summary=summaries["kanglish"], english_summary=summaries["english"])
    

# Endpoint for processing URL input.
@app.route('/process-url', methods=['POST'])
def process_url():
    result = ""
    summaries = {"kannada": "", "kanglish": "", "english": ""}
    filename = ""
    url = request.form.get('urlInput')
    if url:
        print(f"Received URL: {url}")
        if assemblyai.is_youtube_url(url):
            result=assemblyai.transcribe_youtube_audio(url)
        else:
            upload_dir = 'uploads'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = "downloaded_file"
            file_path = os.path.join(upload_dir, filename)

            try:
                result=assemblyai.transcribe_youtube_audio(url)
            except Exception as e:
                print("Error downloading file from URL:", e)
    else:
        print("No URL provided in the form data.")
    if result:
        summaries = generate_summaries(result)
    return render_template('index-result.html',transcription=result, audio_file=filename, kannada_summary=summaries["kannada"], kanglish_summary=summaries["kanglish"], english_summary=summaries["english"])

# Endpoint for processing plain text input.
@app.route('/process-text', methods=['POST'])
def process_text():
    text = ""
    summaries = {"kannada": "", "kanglish": "", "english": ""}
    text = request.form.get('textInput')
    if text:
        print("Received text for processing:", text)
        summaries = generate_summaries(text)
    else:
        print("No text provided in the form data.")
    return render_template('index-result.html', transcription=text, audio_file="", kannada_summary=summaries["kannada"], kanglish_summary=summaries["kanglish"], english_summary=summaries["english"])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)