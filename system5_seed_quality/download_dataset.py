import argparse
import subprocess
import sys
import zipfile
from pathlib import Path


DATASET = "warcoder/soyabean-seeds"
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "seed_quality"


def download_dataset(force: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DATA_DIR / "soyabean-seeds.zip"

    if any(DATA_DIR.iterdir()) and not force:
        print(f"Dataset folder already has files: {DATA_DIR}")
        print("Use --force to download again.")
        return

    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET,
        "-p",
        str(DATA_DIR),
        "--force",
    ]

    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Kaggle download failed: kaggle command was not found. "
            "Install the Kaggle CLI and configure kaggle.json first."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Kaggle download failed with exit code {exc.returncode}.") from exc

    zip_files = sorted(DATA_DIR.glob("*.zip"))
    if not zip_files:
        raise RuntimeError(f"Kaggle download failed: no zip file found in {DATA_DIR}.")

    zip_path = zip_files[0]
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(DATA_DIR)

    print(f"Dataset extracted to: {DATA_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download soybean seed quality dataset from Kaggle.")
    parser.add_argument("--force", action="store_true", help="Download again even if files exist.")
    args = parser.parse_args()

    try:
        download_dataset(force=args.force)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
