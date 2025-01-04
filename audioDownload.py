import json 
from pytube import YouTube
import os
from typing import List, Dict
from pytubefix import YouTube
from pytubefix.cli import on_progress


# done till 0-7 index playlist (19-10-24)

# pytubefix example
 
# url = "https://www.youtube.com/embed/aqz-KE-bpKQ"
 
# yt = YouTube(url, on_progress_callback = on_progress, use_po_token=True,allow_oauth_cache=False)
# print(yt.title)
 
# ys = yt.streams.get_audio_only()
# ys.download(mp3=True,output_path=".")


# create the main file for audio
os.makedirs("./Audio",exist_ok=True)

# load the json file containing all the urls
with open("AllVideoUrl.json", "r") as file:
    data = json.load(file)


def downloadPlaylist(json:Dict) -> None:
    playlist_name = json["Play_list_name"]
    playlist_url_list = json['Play_list_video_links']

    # creating a dir inside the Audio folder
    path = os.path.join("./Audio",playlist_name)

    # create the directory
    os.makedirs(path,exist_ok=True)

    print(f"Start Downloading Playlist: {playlist_name}")
    # now loop over and download the audio from the urls
    for url in playlist_url_list:
        try:
            # print(url)
            # Create YouTube object
            # yt = YouTube(url)
            yt = YouTube(url, on_progress_callback = on_progress, use_po_token=True,)
            # the playlist path
            output_path = path

            # Get the audio stream (mp3 format with the highest bitrate)
            # audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream = yt.streams.get_audio_only()

            # Download the audio file
            print(f"Downloading: {yt.title}")
            # audio_stream.download(output_path=output_path, filename=f"{yt.title}.mp3")
            audio_stream.download(mp3=True,output_path=output_path)
            print("Download completed successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    print(f"Finish Downloading Playlist: {playlist_name}")


def DownloadAll(data:List) -> None:

    # loop over the values 
    for item in data:
        # call the download function
        downloadPlaylist(item)


if __name__ == "__main__":
    # calling the function
    DownloadAll(data=data[8:]) # looping from 8th index the prev one are downloaded