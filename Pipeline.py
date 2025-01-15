import os
import json
import sys
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv
import time
from datetime import datetime
from tqdm import tqdm  # Import tqdm

load_dotenv()

## Global scope variable
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

Audio_playlist_path = "Audio/"

## GEMINI model config and System insturction 

generation_config = {
  "temperature": 0,
  "top_p": 0.2,
  "top_k": 20,
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

SYSTEM_INST = """You're an expert at transcribing bangla audio into bangla text. Now follow the below steps:
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


##### All the necessary functions #######

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

def load_names(path):
  """
  Load the JSON file which contains the tree structure of the videos in the "Audio/" directory.

  Parameters:
  path (str): The path to the JSON file.

  Returns:
  dict: A dictionary where the keys are the playlist names, and the values are lists of video names.
  """
  # opening the json file
  with open(path, 'r') as json_file:
      playlist_vid_tree = json.load(json_file)

  return playlist_vid_tree


def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def get_gemini_response_json(path):
  """
  Uploads an audio file to Gemini and initiates a chat session to transcribe the audio into Bangla text.

  Parameters:
  path (str): The path to the audio file that needs to be transcribed.

  Returns:
  dict: A JSON response containing the transcribed Bangla text.
  """
  # first upload the file
  files = [
      upload_to_gemini(path)
  ]

  # create a chat_session and include the file (chat session will be created in each iteration)
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

  # now getting the response back
  response = chat_session.send_message("Please transcribe the audio into bangla text.")
  gemini_json_response = json.loads(response.text)
  return gemini_json_response

def log_transcription(transcription_log, transcription_list):
  with open(transcription_log, "w") as Tlog_file:
    json.dump(transcription_list,Tlog_file,ensure_ascii=False,)


def log_error(log_file, error_file_path):
  with open(log_file, "a") as log_file:
    log_file.write(error_file_path)
    log_file.write("\n")
  return


def main(audio_root_dir,
        playlist_json_path,
        transcription_log,
        log_file_path,):
  # first read the data.json file
  playlist_vid_tree = load_names(playlist_json_path)

  total_video_len = len([item for sublist in playlist_vid_tree.values() for item in sublist])

  # a list for all the transcription
  transcription_list_dict_list = []

  api_calls_count = 0

  with tqdm(total=total_video_len, desc="Transcribing Audio") as pbar:
    # now looping over each playlist
    for playlist in playlist_vid_tree:
      videos = playlist_vid_tree[playlist]

      ## configure the path for playlist
      playlist_path = os.path.join(audio_root_dir,playlist)

      # now looping over each video in the playlist
      for video in videos:
        api_calls_count += 1

        # checking if the api call is exceeding 10 calls per min
        if api_calls_count >= 10:
          elapsed_time = (datetime.now() - start_time).total_seconds()

          # If we have not yet waited a full minute, sleep for the remaining time
          if elapsed_time < 60:
            print("Exceeded 10 calls per min. Going to sleep for 1 min")
            time.sleep(60)
            print("Sleep complete back to action")

          # Reset the counter and start time for the next minute
          api_calls = 0
          start_time = datetime.now()
        

        # now get the audio path
        audio_path = os.path.join(playlist_path,video)

        # checking if the file size > 0 (then it is a valid file)
        if os.path.getsize(audio_path) > 0:
          # now get the json response
          try:
            gemini_json_response = get_gemini_response_json(audio_path)

            # now get the text
            transcription = gemini_json_response["Bangla_transcription_from_audio"]

            ## creating a dict object
            dict_obj = {
              "Playlist_name": playlist,
              "Video_name": video,
              "Transcription": transcription
            }

            # appending to the list
            transcription_list_dict_list.append(dict_obj)

            # logging the transcription
            print(f"Successfully Transcribed {audio_path}. Logging it.")
            log_transcription(transcription_log,transcription_list_dict_list)
          except:
            print(f"Error in file: {audio_path}. Logging it.")
            log_error(log_file_path,audio_path)
            continue
        # not valid files
        else:
          print(f"Error in file: {audio_path}. Logging it.")
          log_error(log_file_path,audio_path)
          

  return


if __name__ == "__main__":
  # setting up all the variables for the main

  audio_root_dir = "Audio/"
  playlist_json_path = "data.json"
  transcription_log = "transcription_log.json"
  log_file_path = "error_log.txt"

  create_vid_json(False) ## already created

  # calling the main
  main(audio_root_dir,playlist_json_path,transcription_log,log_file_path)






