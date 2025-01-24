from datasets import Dataset, DatasetDict, load_dataset
from huggingface_hub import HfApi, create_repo
import os
from dotenv import load_dotenv
load_dotenv()


def load_json_dataset(file_path:str):
    # load from json file
    data = load_dataset('json', data_files=file_path)['train']

    return data


def create_hf_repo(dataset_name:str, token:str)->str:
    api = HfApi()
    repo_id = f"{dataset_name}"
    try:
        repo_url = api.create_repo(repo_id=repo_id, token=token, repo_type="dataset")
        print(f"Created repo at {repo_url}")
    except Exception as e:
        print(f"Repo creation failed: {e}")
        print(f"Make sure that the repository doesn't exist under your user or organization or you have the right permissions and API tokens")

    return repo_id


def push_to_hf_hub(dataset:Dataset, repo_id:str, token:str)->None:
 # Check if dataset is dictionary
    if isinstance(dataset, dict):
        dataset = DatasetDict(dataset)

    if not isinstance(dataset, Dataset):
        print("The dataset is not in a Dataset format. Please transform it first into a Dataset object.")
        return

    dataset.push_to_hub(repo_id=repo_id, token=token)
    print(f"Dataset has been pushed to https://huggingface.co/datasets/{repo_id}")
 

if __name__ == "__main__":

   
    json_file_path = "transcribtionLogs/transcription_log.json" 
    dataset_name = "RakibulAI-Utub-Bangla-Transcription"  
    hf_token = os.environ['hf_token'] # replace with your token

    # Create Dataset
    dataset = load_json_dataset(json_file_path)

    # Create Repo
    repo_id = create_hf_repo(dataset_name, hf_token)

    # Push to the Hub
    push_to_hf_hub(dataset, repo_id, hf_token)
