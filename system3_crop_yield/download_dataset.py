import subprocess
from pathlib import Path


DATASET = "gurudathg/crop-yield-prediction-using-soil-and-weather"
BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "crop_yield"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(OUTPUT_DIR),
        "--unzip",
    ]

    print(f"Downloading Kaggle dataset: {DATASET}")
    print(f"Destination: {OUTPUT_DIR}")

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Kaggle CLI is not installed. Install it with `pip install kaggle` "
            "and configure your Kaggle API credentials."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Kaggle download failed. Check network access and Kaggle API "
            "credentials, then run this script again."
        ) from exc

    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files were extracted in {OUTPUT_DIR}")

    print("Dataset downloaded successfully.")
    for csv_file in csv_files:
        print(f"Found CSV: {csv_file.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
