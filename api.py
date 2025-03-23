from google import genai
import os
import time
from IPython.display import Markdown
import subprocess
import sys
from conf import GEMINI_API_KEY
from google.genai.files import Files

def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

def generate_content(client, video_file_name, lang, task, custom_prompt=''):
    video_file = client.files.get(name=video_file_name)

    prompt = None

    if task == 'SUMMARIZE':
        prompt = "Summarize this video giving the general idea and important details."
    elif task == 'TIMESTAMPS':
        prompt = "Give me a exhaustive list of notable events in the video and their corresponding timestamps."
    elif task == 'AUDIO_SUMMARY':
        prompt = ("Summarize me the dialogue that is audible in the video. You can use "
                  "visual interpretation to understand it more accurately.")
    elif task == 'AUDIO_TRANSCRIPTION':
        prompt = ("Transcribe me in the text form the literal dialogue that is audible in the video, adding to each "
                  "sentence the corresponding timestamp. I want every single word that is being said "
                  "accurately.")
    elif task == 'CUSTOM_PROMPT':
        prompt = custom_prompt
    elif task == 'QUESTIONS_ANSWERS':
        prompt = ('Create me a dozen of question answers about the video if possible. You can include multiple choice '
                  'questions to add more diversity')

    if prompt is None:
        return ("Please provide a valid task. Valid tasks are SUMMARIZE, TIMESTAMPS, AUDIO_SUMMARY, and"
                "AUDIO_TRANSCRIPTION.")

    if lang == 'FR':
        prompt = prompt + "\nWrite your answer in French please."
    elif lang == 'EN':
        prompt = prompt + "\nWrite your answer in English please."

    prompt += "\nYour answer is for display only so don't ask me my opinion about your answer please."


    # Pass the video file reference like any other media part.
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=[
            video_file,
            prompt])

    return response.candidates[0].content.parts[0].text

