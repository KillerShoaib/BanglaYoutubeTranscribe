import wandb
from dotenv import load_dotenv
import os
from typing import Union
load_dotenv()

def download(condition:bool)-> Union[str,None]:
  """
  Downloads the artifact from wandb if condition is True.
  The artifact is downloaded in the current working directory.
  The function returns the path of the downloaded artifact if condition is True, otherwise it returns None.
  """
  if(condition):
    # wandb loging
    wandb.login(key=os.environ['WANDB_API_KEY'])
    run = wandb.init(project="YoutubeBanglaAudioTranscribe",name='Raw_Audio_dataset_Rakibul_AI',job_type="DatasetDownload")
    artifact = run.use_artifact('killershoaib/YoutubeBanglaAudioTranscribe/Raw_Audio_dataset_Rakibul_AI:v0', type='dataset')
    artifact_dir = artifact.download()
    return artifact_dir
  else:
    return


if __name__ == "__main__":
  # calling the function
  download(True)