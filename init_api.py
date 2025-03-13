import google.generativeai as genai
import os


genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
genai.configure(api_key="AIzaSyBaiW7QGrdf2yE6sckWpHhAHdn4Fs0be_Y")

for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
