# Utub Bangla Transcription

![Image](https://github.com/user-attachments/assets/d20294f8-fdcc-41a7-a0a1-7a701c83056f)

This project aims to automate all the youtube videos of bangla youtubers. For demonstration I've chosen Rakibul Hasan utub chanel who is the most influencial AI content creator in Bangladesh. But this project can be run for any bangla youtuber.

# Motivation Behind This Project

**First, I want to state this project is not intended for commercial use. Transcribing youtube videos and using it for commercial usage is completely prohibited.**

1. My first motivation is to contribute to **Bangla** open source community
2. When I was working with LLM and AI models, one thing that frustrated me that how little resources we've for **Bangla** language. 
3. So, I decided myself either I can be mad about it or do something that'll help the next gen of people who want to build bangla AI models for **Bangla** language.
4. Not only LLMs, but for RAG and better retriever we need more **Bangla** dataset. As a professional Jr. AI engineer I found we have no solid embedding model in bangla which is open source nor have a big knowledge base for any particular domain. I want to change that. Okay let's be honest I myself may not change entirely but I want to start from somewhere and maybe it'll motivate others to follow the path and start contributing to the community.
5. Lastly I want to build something which my sensei (sir) would be proud of. That's why I've chosen **Rakibul Hasan** utub chanel and tried to build a knowledge base from his utub videos. I was inspired by his contribution to the bangla open source community and I owe my career to him. **Without his books I'd not be here right now**. Sensei, if you're reading this, then all I wanna say **"Thank you for everything, I hope this makes you somewhat proud"**

# Huggingface Dataset

Dataset Link: [KillerShoaib/RakibulAI-Utub-Bangla-Transcription](https://huggingface.co/datasets/KillerShoaib/RakibulAI-Utub-Bangla-Transcription)

**Above dataset is the final transcription dataset that I've made from this project.**

# Prerequisites

- **Gemini API KEY**

You'll need a gemini api key to run this project.

## Generating API key
1. Go to google ai studio: https://aistudio.google.com/welcome
2. generate an api key and copy it
3. paste that gemini api key in the .env file as `GEMINI_API_KEY=xxxxxxxx`

That's it! You're all set to go.

# Why use Google's model (the evil one who stole all of our data)

First of all everyone is stealing our data, that's not something new. But there are several reasons I've chosen the google's Gemini model.

1. 1.5k free request per day to their latest model (I'd say that's generous of them)
2. And their STT feature from their `gemini-flash-2.0-exp` is quite good and I was satisfied with the overall result.

Yeah that's it, that was all the reason I chose the google's Gemini model.

# What about Open Source Alternative

Actually my first version of this project was based on an open source model name `seamless-m4t` by meta (meta is also evil btw). I brain strommed the whole pipeline and everything. I was creating the pipeline and then saw gemini released their model. I thought privacy is not a concern here (cause we're using utub video duh..) so why make my life difficult and went with the gemini free api instead of the open source model.

But...but I might recreate this whole pipeline in the open source model if some of you're interested on it. But for now, naah I'm good.

# How to use this project

First I want to acknowledge that the code is bit messy. Sorry for the unstructured code. But I'll try my best to give an overview in this doc so that atleast you've somewhat idea how to run this project.

## Repo Setup
### Clone the repo
```bash
git clone https://github.com/KillerShoaib/BanglaYoutubeTranscribe.git
```

### Switch to project dir
```bash
cd BanglaYoutubeTranscribe
```

### Create a virtual env & activate it (ubuntu)
```bash
python3 -m venv venv
source venv/bin/activate
```

## Install All the dependencies
```bash
pip install -r requirements.txt
```

## Creating .env and pasting the API

Remember, I've told above we need gemini api key. Now we'll create a `.env` file and paste the api key there.

```bash
touch .env
```
(You can manually create the file using GUI. I'm just trying to look cool that's why creating the file from the bash command)

Now paste the API key
```bash
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Project Workflow
before showing how to run the project I think giving you how the overall project works and how I use the project to transcribe the utub videos will give more clear understanding.

### 1.  All the Playlist Url in `PlaylistUrl`

I manually grab all the playlist in the "Rakibul Hasan" utub chanel and paste them in the `PlaylistUrl.py` file. "But, Shoaib why grab all the playlist url link manually?" I was feeling lazy that's all, there weren't much playlist to begin with that's why I didn't automate the process but it can easily be automated.

### 2. Getting all the playlist video url in `VideoLinks.py`

After having all the playlist url now my next task was to get all the video links from each playlist. That's why I wrote `VideoLinks.py` which is basically looping over each playlist and getting all the video links associate with that playlist and saving them into a json file name `VideoUrl.json` (you can find that json file in `Data` directory)

### 3. Getting only the Audio from each video

Let's review what I've done so far.

1. I've all the playlist link in the `PlaylistUrl.py`
2. Then iterate over each playlist and save all the videos in `VideoUrl.json` file for future reference.

Since we've all the video url (utub video link) now all we need is the audio of it. For this I use `pytube-fix` library. I first grab only the audio from that url and then download that audio. The file structure was like below
```
.
└── Audio/
    ├── Playlist1/
    │   ├── video1.mp3
    │   └── video2.mp
    └── Playlist2/
        ├── video1.mp3
        └── video2.mp3
```

**Some Issues while Downloading the Audio:** 
1. I tried to completely automated this entire part but wasn't able to do that thanks to evil corp Google. Google was making it super difficult to download utub videos even using pytube library. I need to provide `po_token` manuallly first to run the script. Please refer to this github [pull request](https://github.com/JuanBindez/pytubefix/pull/209) for more details.
Providing the `po_token` manually makes the script semi automated not fully automated. So we can't run this on virtual machine or schedule a run with this script cause every time we run the script we need to provide the `po_token`. There is a way to automate it but that was way out of the scope of this project.

2. Even after giving the `po_token` there way many instances where the audio wasn't downloaded. It return empty file. I think this is due to utub anti bot policy where they are preventing downloading the audio in many cases. Therefore I wasn't able to download all the utub audio from the "Rakibul Hasan" channel. I've downloaded total **302 videos**

### 4. Saving to & Downloading from Wandb

For my convinience I use wandb to save all the audio data. But you can skip this part. I was using a vm and my local computer to build this project therefore I needed to host all the audio files to cloud.

### 5. `Pipeline` where the automated process of transcription happened

1. First I created a `data.json` file which have `playlist_name` name as key and `video_name` as value. Which helped me to locate the path in the audio folder.
2. Then I create a `SYSTEM_INST` which is basically the instruction to the model to transcribe the audio and return the output in a structure format. Means all the output coming from the model will be in json structure. {"Bangla_transcription_from_audio":"actual transcription"}
3. Then I iterate over each file and send that file to gemini and got the response
4. Remember there were some file which were empty, I log them as error file in the `error_log.txt` (in `traanscribtionLogs` folder). I intended to download those video later on but didn't got time for it.
5. Finally I save all the transcription in the `transcription_log.json`

### 6. Pushing to HF hub

I want to make the dataset public, therefore I push the data to `HuggingFace Hub`, but you can ignore this step.

Dataset Link: [KillerShoaib/RakibulAI-Utub-Bangla-Transcription](https://huggingface.co/datasets/KillerShoaib/RakibulAI-Utub-Bangla-Transcription)

## Replicate but with Different Utub channel

Now that you've read the workflow or how I've used this project to get the transcription then you have much better understanding how to recreate this with different utub channel.

1. First grab all the playlist links for that particular utuber and put them into `PlaylistUrl.py` file.
2. Then download the audio (don't forget to provide `po_token`)
3. And finally do the trascription using the `pipeline` script
4. You can also upload the dataset in the `HuggingFace Hub` using the `upload2hf.py` script (but you'll need a huggingface account and a huggingface token, put that token to the `.env` file similar to `GEMINI_API_KEY`)

# Conclusion

Yeah, nothing to conclude here to be honest. It just a habit of mine that I've learned in childhood to finish an essay with conclusion. Doing the same here. But if I wanted to say something at last then I'd say **"PLEASE CONTRIBUTE TO THE OPEN SOURCE BANGLA AI COMMUNITY, WE NEED MORE BANGLA DATASET"**
