import os
import time
import requests
from urllib.parse import urlparse
import yt_dlp

def is_youtube_url(url):
    try:
        parsed_url = urlparse(url)
        return 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc
    except Exception as e:
        print("Error parsing URL:", e)
        return False

def download_youtube_audio(url):
    print("Downloading audio from YouTube...")
    output_template = "downloads/%(title)s.%(ext)s"
    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise Exception("Could not extract audio information")
            audio_file = ydl.prepare_filename(info).rsplit(".", 1)[0] + ".mp3"
            if not os.path.exists(audio_file):
                raise Exception("Audio file was not downloaded successfully")
            print("YouTube audio saved as:", audio_file)
            return audio_file
    except Exception as e:
        print("Error downloading audio:", str(e))
        raise

def get_time_elapsed(start_time):
    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    return f"{minutes} minutes and {seconds} seconds"

# AssemblyAI API settings
total_start_time = time.time()
base_url = "https://api.assemblyai.com"
headers = {
    "authorization": "YOUR_ASSEMBLYAI_API_KEY"  # Replace with your AssemblyAI API key
}

def transcribe_youtube_audio(media_source):
    if not is_youtube_url(media_source):
        raise ValueError("Please provide a valid YouTube URL")
    try:
        print("Processing YouTube video...")
        local_audio_file = download_youtube_audio(media_source)
        return transcribe_local_file(local_audio_file)
    finally:
        try:
            if local_audio_file and os.path.exists(local_audio_file):
                os.remove(local_audio_file)
                print("Cleaned up temporary YouTube audio file")
        except Exception as e:
            print("Error cleaning up file:", e)

def transcribe_local_file(file_path):
    print(f"Uploading local file to AssemblyAI: {file_path}")
    upload_start_time = time.time()
    with open(file_path, "rb") as f:
        upload_response = requests.post(
            base_url + "/v2/upload",
            headers={**headers, "Content-Type": "application/octet-stream"},
            data=f
        )
    if upload_response.status_code != 200:
        raise RuntimeError(f"Failed to upload file. Status code: {upload_response.status_code}")
    upload_url = upload_response.json().get("upload_url")
    print(f"Upload completed in {get_time_elapsed(upload_start_time)}")
    
    print("Starting transcription...")
    transcription_start_time = time.time()
    data = {
        "audio_url": upload_url,
        "speech_model": "universal"
    }
    transcript_response = requests.post(base_url + "/v2/transcript", json=data, headers=headers)
    if transcript_response.status_code != 200:
        raise RuntimeError(f"Failed to start transcription. Status code: {transcript_response.status_code}")
    
    transcript_id = transcript_response.json().get('id')
    polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"
    print("Transcription started, polling for results...")
    
    while True:
        result_response = requests.get(polling_endpoint, headers=headers)
        result = result_response.json()
        status = result.get('status')
        if status == 'completed':
            print("Transcription completed in", get_time_elapsed(transcription_start_time))
            print("Transcript Text:", result.get('text'))
            return result.get('text')
        elif status == 'error':
            raise RuntimeError(f"Transcription failed: {result.get('error')}")
        else:
            print("Waiting for transcription to complete...")
            time.sleep(3)