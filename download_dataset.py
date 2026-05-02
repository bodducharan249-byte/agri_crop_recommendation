# Import Kaggle API
from kaggle.api.kaggle_api_extended import KaggleApi

# Import os to create folders
import os

# Create data folder
os.makedirs("data", exist_ok=True)

# Create Kaggle API object
api = KaggleApi()

# Login using kaggle.json
api.authenticate()

# Download crop recommendation dataset
api.dataset_download_files(
    "atharvaingle/crop-recommendation-dataset",
    path="data",
    unzip=True
)

# Print success message
print("Dataset downloaded successfully.")