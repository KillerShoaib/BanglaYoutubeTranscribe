import os
import json
import sys
import re
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv
import time
from datetime import datetime
from tqdm import tqdm 
import shutil
import zipfile
from typing import Union, Dict, List, Optional

load_dotenv()

############# Global scope variable #############
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
############# Global scope variable #############

##### All the necessary functions #######

def create_vid_json(condition:bool)->None:
    """
    Create a JSON file which contains the tree structure of the videos in the "Audio/" directory.
    
    Parameters:
    condition (bool): If True, the function will create the JSON file. If False, the function won't do anything.
    """
    if(condition):
        dirs = os.listdir(Audio_playlist_path)
        playlist_vid_tree = {key:[value for value in os.listdir(os.path.join(Audio_playlist_path,key))] for key in os.listdir(Audio_playlist_path)}

        # Save dictionary to a JSON file
        with open('Data/data.json', 'w') as json_file:
            json.dump(playlist_vid_tree,json_file,ensure_ascii=False, indent=4)
        return

def extract_audio(zip_file_path: str, extract_to: str)-> None:
    """
    Extracts the audio zip file to the specified directory.

    Parameters:
    - zip_file_path (str): The path to the zip file to be extracted.
    - extract_to (str): The directory where the contents will be extracted.
    """
    # Create the directory if it doesn't exist and if exist and have folder inside it means the zip is already extracted
    if(os.path.exists(extract_to)) and len(os.listdir(extract_to)) > 0:
        print("Zip file is already extracted")
        return

    
    os.makedirs(extract_to, exist_ok=True)


    try:
        # Unzip the file
        print(f"Extracting {zip_file_path}")
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except:
        print(f"Error while extracting {zip_file_path}")


def load_names(path:str)->Dict:
    """
    Load the JSON file which contains the tree structure of the videos in a directory.

    Parameters:
    path (str): The path to the JSON file.

    Returns:
    dict: A dictionary where the keys are the playlist names, and the values are lists of video names.
    """
    # opening the json file
    with open(path, 'r') as json_file:
        playlist_vid_tree = json.load(json_file)

    return playlist_vid_tree


def upload_to_gemini(path:str, mime_type:Optional[str]=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def get_gemini_response_json(path:str)-> Dict:
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



def log_transcription(transcription_log:str, transcription_list:List)->None:
    """
    Writes a list of transcriptions to a JSON file.

    Parameters:
    transcription_log (str): The path to the log file.
    transcription_list (list): A list of transcription dictionaries.
    """
    with open(transcription_log, "w") as Tlog_file:
        json.dump(transcription_list,Tlog_file,ensure_ascii=False,)


def log_error(log_file:str, error_file_path:str):
    """
    Writes the path of an error log file (if any file was unable to transcribe) to the specified log file.

    Parameters:
    log_file (str): The path to the log file.
    error_file_path (str): The path to the error log file that needs to be written to the log file.
    """
    with open(log_file, "a") as log_file:
        log_file.write(error_file_path)
        log_file.write("\n")
    return

def tracker(vid_name: str, playlist_name: str) -> None:
    """
    A function used to keep track of the videos that have been processed.
    It writes the name of the video and the playlist name to a file named `tracker.txt`.

    Parameters:
    vid_name (str): The name of the video.
    playlist_name (str): The name of the playlist.
    """
    with open("transcribtionLogs/tracker.txt", "a") as tracker:
        tracker.write(f"{playlist_name}:{vid_name}")
        tracker.write("\n")

# use this only for lightning studio
def stop_lightningStudio()-> None:
    """
    Stops Lightning Studio if it is currently running.

    This function should be used in conjunction with main() to ensure that
    Lightning Studio is stopped after the script is finished running.

    Parameters:
    None

    Returns:
    None
    """
    from lightning_sdk import Studio
    print("Stopping Lightning Studio")
    s = Studio()
    s.stop()


def main(audio_root_dir:str,
        zip_file_path:str,
        playlist_json_path:str,
        transcription_log:str,
        log_file_path:str,)-> None:

    """
    Orchestrates the audio transcription process using Gemini.

    This function extracts audio files from a zip archive, iterates through each
    audio file, transcribes it to Bangla text using the Gemini API, and logs
    the transcriptions and any errors encountered. It also tracks the processed
    videos in a separate file.

    Args:
        audio_root_dir (str): The directory where the audio files will be extracted.
        zip_file_path (str): The path to the zip file containing audio files.
        playlist_json_path (str): The path to the JSON file containing the playlist and video structure.
        transcription_log (str): The path to the JSON file where transcriptions will be logged.
        log_file_path (str): The path to the text file where errors will be logged.
    
    Returns:
        None
    """


    # first extract the zip file
    extract_audio(zip_file_path,audio_root_dir)

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
                start_time = datetime.now()
                # checking if the api call is exceeding 10 calls per min
                if api_calls_count >= 10:
                    elapsed_time = (datetime.now() - start_time).total_seconds()

                    # If we have not yet waited a full minute, sleep for the remaining time
                    if elapsed_time < 60:
                        print("Exceeded 10 calls per min. Going to sleep for 1 min")
                        time.sleep(60)
                        print("Sleep complete back to action")

                        # Reset the counter and start time for the next minute
                        api_calls_count = 0
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
                        print(f"Error in file after passing to api: {audio_path}. Logging it.")
                        log_error(log_file_path,audio_path)
                        continue
                # not valid files
                else:
                    print(f"Error in file due to empty: {audio_path}. Logging it.")
                    log_error(log_file_path,audio_path)
        
            # tracking all the videos that have completed transcription
            tracker(video,playlist)
          

    return


if __name__ == "__main__":
  # setting up all the variables for the main

  audio_root_dir = "Audio/"
  zip_file_path = "artifacts/Raw_Audio_dataset_Rakibul_AI:v0/BanglaAudioZipFile.zip"
  playlist_json_path = "Data/data.json"
  transcription_log = "transcribtionLogs/transcription_log.json"
  log_file_path = "transcribtionLogs/error_log.txt"

  create_vid_json(False) ## already created

  # calling the main
  main(
    audio_root_dir=audio_root_dir,
    zip_file_path=zip_file_path,
    playlist_json_path=playlist_json_path,
    transcription_log=transcription_log,
    log_file_path=log_file_path
  )

  # stoping the studio (Only use this if you're using lighntning studio)
  stop_lightningStudio()






