# Multimedia Transcription and Summarization

This project is a web application that transcribes audio/video content and provides summaries in multiple languages. It can process local files, YouTube videos, and direct text input.

## Features

- **Transcription**:
  - Transcribe audio and video files (MP3, WAV, MP4, MOV, etc.).
  - Extract and transcribe audio from YouTube URLs.
  - Powered by the AssemblyAI API for accurate speech-to-text conversion.

- **Summarization**:
  - Generate summaries of the transcribed text in three different formats:
    - **English**: A standard summary in English.
    - **Kannada**: A summary translated into the Kannada language.
    - **Kanglish**: A summary in Kanglish (Kannada written with English letters), ideal for casual reading.
  - Supports direct text input for summarization.

- **Transliteration**:
  - Convert English text to Kanglish.

## How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chinmayc0707/major_project.git
   cd major_project
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API Keys:**
   - **AssemblyAI**: Open `assemblyai.py` and replace the placeholder with your own API key.
   - **OpenRouter**: Update the API keys in `app.py` for the summarization and transliteration features.

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://127.0.0.1:5000`.

## Project Structure

- `app.py`: The main Flask application file containing the web server logic and routes.
- `assemblyai.py`: Handles all interactions with the AssemblyAI API for transcription.
- `transliteration.py`: Contains the logic for English to Kanglish transliteration.
- `templates/`: Houses the HTML templates for the web interface.
- `static/`: Stores static assets like CSS and JavaScript files.
- `uploads/`: The default directory for storing uploaded audio/video files.
- `downloads/`: The default directory for storing audio downloaded from YouTube.