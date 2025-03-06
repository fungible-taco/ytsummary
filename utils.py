import os
import re
import whisper
import requests
import streamlit as st
from pytubefix import YouTube
from dotenv import load_dotenv

##test url
#url = 'https://www.youtube.com/watch?v=TDHW9OrOPTc'

def is_valid_youtube_url(url):
    """Youtube ling regex validation"""

    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)
    return bool(youtube_regex_match)


def get_video_info(url):
    """get video info"""

    try:
        yt = YouTube(url)
        return {
            'title': yt.title,
            'description': yt.description,
            'duration': yt.length,
            'views': yt.views,
            'author': yt.author
        }
    except Exception as e:
        raise Exception(f"Error fetching video info: {str(e)}")


def download_youtube_audio(url, output_filename):
    """extract audio from video"""

    try:
        yt = YouTube(url)
        video_title = yt.title
        ys = yt.streams.get_audio_only()
        ys.download(filename=output_filename)
        print(f"Downloaded audio from: {video_title}")
        return video_title
    except Exception as e:
        print(f"Error downloading YouTube audio: {e}")
        raise


def transcribe_audio(audio_filename, model_size='base'):
    """transcribe audio with whisper"""

    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_filename, fp16=False)
        print('whisper_done')
        return result['text']
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise


def summarize_text(text):
    """summarize transcription with llama"""

    # Get API key from streamlit secrets
    api_key = st.secrets['OPENROUTER_API_KEY']

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={  # Using json parameter instead of data with json.dumps
                "model": "meta-llama/llama-3.2-1b-instruct:free",
                "messages": [
                    {"role": "system", "content": "Summarize the provided text with the following criteria:"
                                                  "1. Provide a detailed, thorough, and concise summary."
                                                  "2. Focus on capturing the main ideas and essential information, especially data points."
                                                  "3. Strictly use the provided text without incorporating any external information."},
                    {"role": "user", "content": text}
                ]
            }
        )
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        raise


def main_func(video_url):
    """main function"""

    audio_file = 'temp_audio.mp3'

    try:
        # Step 1: Download audio from YouTube
        download_youtube_audio(video_url, audio_file)

        # Step 2: Transcribe the audio
        transcript = transcribe_audio(audio_file, model_size='base')

        # Step 3: Summarize the transcript
        summary_response = summarize_text(transcript)

        # Step 4: Print the summary
        if 'choices' in summary_response and summary_response['choices']:
            summary = summary_response['choices'][0]['message']['content']
            print("\nSummary:")
            print(summary)
            return summary
        else:
            print("\nUnable to generate summary. API response:")
            print(summary_response)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up the temporary audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print(f"\nRemoved temporary file: {audio_file}")