from pytube import Playlist,  YouTube
from PlayListUrl import playLists # importing all the playlist link from there
from typing import List, Optional
import json

def attachVideoUrl(url: str,
                   vidList: List) -> List:

    """ url = takes the playlist url which will be used to retrieved all the video links from that playlist
        vidList =  takes a list object which will append the dictionay object to an existing list item

        The purpose of this function is to take the url get the playlist name and all the video url in that playlist
        and create a dictionary object which will have "play_list_name" and "Play_list_video_links" 
        Finally, append that dict to the list object.
    """

    # first get the playlist object
    p = Playlist(url)

    # get the name of the playlist
    playListName = p.title


    # geth all the videos from the playlist
    playlistVideosUrl = list(p.video_urls)

    # converting them into a dictionary
    dictObj = {
        "Play_list_name": playListName,
        "Play_list_video_links": playlistVideosUrl
    }

    # now appending the dict object to the vidList object
    vidList.append(dictObj)
    return vidList




def gettingPlaylistVid(logging:Optional[bool]=False,
                       saveToJson:Optional[bool]=False):
    """This is the main function which will loop over all the playlist link and run attachVideoUrl to append all
    the dict obj to the videoList list and finaly create a json file and dump the list obj to that file.
    """

    videoList = []
    index= 0
    for playlist in playLists:

        # for printing logging msg
        if logging:
            index+=1
            print(f"Completed Playlist {index}")

    
        # updating the video list by calling the functions
        videoList = attachVideoUrl(
            url=playlist,
            vidList=videoList
        )
    
    if  saveToJson:
        # after getting all the video urls now duming the final list in a pickel  file
        with open("Data/VideoUrl.json", "w") as file:
            json.dump(videoList, file,ensure_ascii=False, indent=4)
    else:
        # if saveToPickle is false then simply return the list
        return videoList




if __name__=="__main__":
    ## caling the function
    gettingPlaylistVid(logging=True,saveToJson=True)

