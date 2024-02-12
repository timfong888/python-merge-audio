import requests
from pydub import AudioSegment
from io import BytesIO
import os

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

# List of audio URLs and their desired filenames
audio_info = [
    ("https://www.googleapis.com/download/storage/v1/b/compaction_bucket/o/wRT7P-VKM0k.mp3?generation=1707637434810820&alt=media", "wRT7P-VKM0k.mp3"),
    ("https://www.googleapis.com/download/storage/v1/b/compaction_bucket/o/BHhz0jTj5wY.mp3?generation=1707637461047620&alt=media", "BHhz0jTj5wY.mp3")
    # Add more tuples of (audio URL, filename) as needed
]

# Download and save each audio file
audio_files = []
for url, filename in audio_info:
    audio_segment = download_and_save_audio(url, filename)
    audio_files.append(filename)

# Merge the audios
merged_audio = merge_audios(audio_files)

# Export the merged audio to a file
merged_audio.export("merged_audio.mp3", format="mp3")

