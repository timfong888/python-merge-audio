from google.cloud import storage
from google.oauth2 import service_account

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

import requests
from pydub import AudioSegment
from io import BytesIO
import os

from urllib.parse import urlparse, unquote


# Define Pydantic models for request and response
class AudioRequest(BaseModel):
    audio_urls: List[str]

class AudioResponse(BaseModel):
    merged_audio_url: str

app = FastAPI()

# Initialize Google Cloud Storage client
credentials = service_account.Credentials.from_service_account_file(
    'path/to/your/service-account-file.json')
storage_client = storage.Client(credentials=credentials)
bucket_name = 'your-bucket-name'

def upload_to_gcs(file_path, bucket_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(file_path)

    # Make the blob publicly viewable
    blob.make_public()
    return blob.public_url

def download_and_save_audio(url, filename):
    """Download an audio file from a URL and save it with the given filename."""
    print(f"Downloading and saving audio from {url} as {filename}...")
    # Download the file from the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    audio_segment = AudioSegment.from_file(BytesIO(response.content))

    # Get the directory name and create it if it doesn't exist
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        print(f"Creating directory {directory}...")
        os.makedirs(directory)

    # Exporting the audio segment to a file
    audio_segment.export(filename, format=filename.split('.')[-1])
    return audio_segment

def merge_audios(audio_files):
    """Merge multiple audio files and return the combined audio."""
    print("Merging audio files...")
    combined_audio = None
    for file in audio_files:
        print(f"Processing {file}...")
        audio_segment = AudioSegment.from_file(file)
        if combined_audio is None:
            combined_audio = audio_segment
        else:
            combined_audio += audio_segment
    return combined_audio

def get_filename_from_url(url):
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)  # Decodes percent-encoded characters
    filename = path.split('/')[-1]
    return filename

@app.post("/merge-audios", response_model=AudioResponse)
async def merge_audios_endpoint(request: AudioRequest):

    # Download and save each audio file
    audio_files = []
    merged_filename = ""  # Initialize merged_filename as an empty string

    for url in request.audio_urls:
        try:
            # Extract filename from URL without query parameters
            filename = get_filename_from_url(url)
            audio_segment = download_and_save_audio(url, filename)
            audio_files.append(filename)
            # Concatenate filenames without extension for the merged filename
            merged_filename += os.path.splitext(filename)[0] + "+"  # Concatenate filenames without extension
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    if not audio_files:
        raise HTTPException(status_code=400, detail="No audio files to merge")
    
    # Remove the trailing '+' from the merged filename and add extension
    merged_filename = merged_filename.rstrip('+') + ".mp3"
    print(f"Merging audio files into {merged_filename}...")

    merged_audio = merge_audios(audio_files)
    
    # Save the merged file with the concatenated name
    merged_audio.export(merged_filename, format="mp3")

    # TODO: Upload the merged file to a cloud storage and get the public URL
    # For now, just returning a placeholder URL
    merged_audio_url = "http://example.com/" + merged_filename

    return AudioResponse(merged_audio_url=merged_audio_url)

# List of audio URLs and their desired filenames
# PAYLOAD SAMPLE
"""
{
    "audio_urls": [
        "http://example.com/audio1.mp3",
        "http://example.com/audio2.mp3"
    ]
}
"""

# Run server
# uvicorn merge_audio:app --reload
# afplay 


