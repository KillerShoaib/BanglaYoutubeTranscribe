import os
import json
import sys
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

Audio_playlist_path = "Audio/"



## model config
# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8092,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "Bangla_transcription_from_audio": content.Schema(
        type = content.Type.STRING,
      ),
    },
  ),
  "response_mime_type": "application/json",
}

SYSTEM_INST = """You're expert at transcribing bangla audio into bangla text. Now follow the below steps:
1. You'll be given a bangla audio. Your task is to only transcribe that bangla audio in bangla text. 
2. Do not add anything else. Only transcribe the audio into bangla.
3. Sometimes in the audio there maybe english words. You don't have to translate the english words into bangla. Rather while transcribing keep the english words as it is.
4. Finally return your final bangla transcription (with some english text if there is any).
"""


model = genai.GenerativeModel(
  model_name="gemini-2.0-flash-exp",
  generation_config=generation_config,
  system_instruction=SYSTEM_INST,
)



def create_vid_json(condition):
    """
    Create a JSON file which contains the tree structure of the videos in the "Audio/" directory.
    
    Parameters:
    condition (bool): If True, the function will create the JSON file. If False, the function won't do anything.
    """
    if(condition):
        dirs = os.listdir(Audio_playlist_path)
        playlist_vid_tree = {key:[value for value in os.listdir(os.path.join(Audio_playlist_path,key))] for key in os.listdir(Audio_playlist_path)}

        # Save dictionary to a JSON file
        with open('data.json', 'w') as json_file:
            json.dump(playlist_vid_tree,json_file,ensure_ascii=False, indent=4)
        return

create_vid_json(False) ## already created


# opening the json file
with open('data.json', 'r') as json_file:
    playlist_vid_tree = json.load(json_file)


for playlist in playlist_vid_tree:
    playlist_name = playlist


