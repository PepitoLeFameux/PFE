import os
import os
from dotenv import load_dotenv


load_dotenv()

RESIZED_FOLDER = 'videos/resized'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
