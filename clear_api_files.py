import google.generativeai as genai
from conf import GEMINI_API_KEY

# Configure with your API key
genai.configure(api_key=GEMINI_API_KEY)

# List files
files = genai.list_files()
for file in files:
    genai.delete_file(file.name)
    print(f"File ID: {file.name} deleted")
