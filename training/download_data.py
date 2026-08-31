"""Download official datasets needed for training and evaluation."""

from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

ISOT_URL = (
    "https://onlineacademiccommunity.uvic.ca/isot/wp-content/uploads/"
    "sites/7295/2023/03/News-_dataset.zip"
)
XSUM_URL = (
    "https://huggingface.co/datasets/EdinburghNLP/xsum/resolve/"
    "30802a38d3f89b2fa8f19276008459e8c2b8b8e6/data/test-00000-of-00001.parquet"
)


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"Using existing file: {destination}")
        return
    request = urllib.request.Request(url, headers={"User-Agent": "NewsLensAI/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    print(f"Downloaded: {destination}")


def download_isot() -> None:
    archive = RAW_DIR / "News-_dataset.zip"
    _download(ISOT_URL, archive)
    with zipfile.ZipFile(archive) as bundle:
        expected = {"True.csv", "Fake.csv"}
        members = {Path(name).name for name in bundle.namelist()}
        if not expected.issubset(members):
            raise RuntimeError("The ISOT archive does not contain True.csv and Fake.csv.")
        for name in bundle.namelist():
            basename = Path(name).name
            if basename in expected:
                with bundle.open(name) as source, (RAW_DIR / basename).open("wb") as destination:
                    shutil.copyfileobj(source, destination)
    print(f"ISOT CSV files are ready in {RAW_DIR}")


def download_xsum() -> None:
    _download(XSUM_URL, RAW_DIR / "xsum-test.parquet")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["isot", "xsum", "all"], default="all")
    args = parser.parse_args()
    if args.dataset in {"isot", "all"}:
        download_isot()
    if args.dataset in {"xsum", "all"}:
        download_xsum()


if __name__ == "__main__":
    main()
