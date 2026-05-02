from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi


DATASET_SLUG = "vipoooool/new-plant-diseases-dataset"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "plant_disease"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    api = KaggleApi()
    api.authenticate()

    print(f"Downloading Kaggle dataset: {DATASET_SLUG}")
    print(f"Destination: {DATA_DIR}")
    api.dataset_download_files(DATASET_SLUG, path=str(DATA_DIR), unzip=True)
    print("Dataset downloaded and extracted successfully.")


if __name__ == "__main__":
    main()
