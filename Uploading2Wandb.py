from dotenv import load_dotenv
import shutil
import wandb
import pathlib
import os
load_dotenv()

# wandb loging
wandb.login(key=os.environ['WANDB_API_KEY'])

# converting to zip file
root = pathlib.Path(__file__).parent
audio_path = os.path.join(root,"Audio")
destinationPath = os.path.join(root,"BanglaAudioZipFile")
shutil.make_archive(destinationPath, 'zip', audio_path)

zipFileName = destinationPath+".zip"


# uploading to wandb
run = wandb.init(project="YoutubeBanglaAudioTranscribe",name='Raw_Audio_dataset_Rakibul_AI',job_type="DatasetUpload")

# Create a new artifact
artifact = wandb.Artifact('Raw_Audio_dataset_Rakibul_AI', type='dataset')

# Add the zip file to the artifact
artifact.add_file(zipFileName)

# Log the artifact to wandb
run.log_artifact(artifact)

# End the run
run.finish()