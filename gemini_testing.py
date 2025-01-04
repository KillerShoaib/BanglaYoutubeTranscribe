# import os
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()

# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# # Create the model
# generation_config = {
#   "temperature": 1,
#   "top_p": 0.95,
#   "top_k": 40,
#   "max_output_tokens": 8192,
#   "response_mime_type": "text/plain",
# }

# model = genai.GenerativeModel(
#   model_name="gemini-2.0-flash-exp",
#   generation_config=generation_config,
#   system_instruction="You're a python expert",
# )
# # chat_session = model.start_chat(
# #   history=[
# #   ]
# # )

# # response = chat_session.send_message("INSERT_INPUT_HERE")

# response = model.generate_content("What is async function in python")

# print(response.text)



################

import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv
import json

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

SYSTEM_INST = """You're expert at transcribing bangla audio into bangla text. Now follow the below steps:
1. You'll be given a bangla audio. Your task is to only transcribe that bangla audio in bangla text. 
2. Do not add anything else. Only transcribe the audio into bangla.
3. Sometimes in the audio there maybe english words. You don't have to translate the english words into bangla. Rather while transcribing keep the english words as it is.
4. Finally return your final bangla transcription (with some english text if there is any).
"""


# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8092,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "Bangla_Transcription_Audio": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  system_instruction=SYSTEM_INST,
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
  upload_to_gemini("Audio/Prompt Engineering Guide/'এআই'কে বশ করার উপায় ২ Writing Effective Prompts  Prompt Engineering Guide (2nd).mp3", mime_type="audio/mpeg"),
]

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
      ],
    },
  ]
)

# chat_session = model.start_chat(
#   history=[]
# )

response = chat_session.send_message("Please transcribe the audio into bangla text.")

json_response = json.loads(response.text)

print(json_response["Bangla_Transcription_Audio"])

with open("Testin.txt",'a') as file:
    file.write(response.text)
    file.write("\n")
    file.write(json_response["Bangla_Transcription_Audio"])
    file.write("\n")
# print(response.text)
# print(response)
# print(type(response.text))