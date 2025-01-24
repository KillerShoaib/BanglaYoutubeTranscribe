import json 
from pytube import YouTube
import os
from typing import List, Dict
from pytubefix import YouTube
from pytubefix.cli import on_progress


# create the main file for audio
os.makedirs("./Audio",exist_ok=True)

# load the json file containing all the urls
with open("Data/VideoUrl.json", "r") as file:
    data = json.load(file)


def downloadPlaylist(json: Dict) -> None:
    """
    Downloads the audio from a playlist of YouTube videos and saves them in a directory named after the playlist.

    Parameters:
    json (Dict): A dictionary containing the playlist information with keys:
        - "Play_list_name": The name of the playlist.
        - "Play_list_video_links": A list of URLs for the videos in the playlist.
    """
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
            
            # See more details at https://github.com/JuanBindez/pytubefix/pull/209
            yt = YouTube(url, on_progress_callback = on_progress, use_po_token=True,) 
            # the playlist path
            output_path = path

            # Get the audio stream (mp3 format with the highest bitrate)
            audio_stream = yt.streams.get_audio_only()

            # Download the audio file
            print(f"Downloading: {yt.title}")
            audio_stream.download(mp3=True,output_path=output_path)
            print("Download completed successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    print(f"Finish Downloading Playlist: {playlist_name}")


def DownloadAll(data: List) -> None:
    """
    Downloads all the audio from the playlists in the given list.

    Parameters:
    data (List): A list of dictionaries containing the playlist information with keys:
        - "Play_list_name": The name of the playlist.
        - "Play_list_video_links": A list of URLs for the videos in the playlist.
    """

    # loop over the values 
    for item in data:
        # call the download function
        downloadPlaylist(item)


if __name__ == "__main__":
    # calling the function
    DownloadAll(data=data)