import re
import json
from pathlib import Path
from collections import defaultdict
import boto3

from app.config import load_config, get_appdata_dir


def test_connection(config: dict):
    s3 = boto3.client(
        "s3",
        endpoint_url=config["endpoint"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )

    s3.list_objects_v2(Bucket=config["bucket"], MaxKeys=1)


_PATTERN = re.compile(r"(?P<year>\d{4})W(?P<week>\d{2})_.*\.parquet$")


def get_local_complete_weeks() -> set:
    """Scan local destination folder configured in app and return set of (year, week)
    that exist in ALL subfolders (same logic as helper.ipynb).
    """
    config = load_config()
    if config is None:
        return set()

    dest_path = Path(config["local_path"])
    weeks_per_folder = defaultdict(set)

    for folder in dest_path.iterdir():
        if not folder.is_dir():
            continue

        for f in folder.iterdir():
            if not f.is_file():
                continue

            m = _PATTERN.match(f.name)
            if m:
                year = int(m.group("year"))
                week = int(m.group("week"))
                weeks_per_folder[folder.name].add((year, week))

    if not weeks_per_folder:
        return set()

    return set.intersection(*weeks_per_folder.values())


def get_bucket_complete_weeks() -> set:
    """Scan the configured Cloudflare R2 bucket and return set of (year, week)
    that exist in ALL prefixes (folders) in the bucket.
    """
    config = load_config()
    if config is None:
        return set()

    s3 = boto3.client(
        "s3",
        endpoint_url=config["endpoint"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )

    bucket = config["bucket"]
    weeks_per_prefix = defaultdict(set)

    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if "/" not in key:
                continue

            prefix, filename = key.split("/", 1)
            m = _PATTERN.match(filename)
            if not m:
                continue

            year = int(m.group("year"))
            week = int(m.group("week"))
            weeks_per_prefix[prefix].add((year, week))

    if not weeks_per_prefix:
        return set()

    return set.intersection(*weeks_per_prefix.values())


def build_week_status(local_weeks: set, bucket_weeks: set) -> dict:
    """Return dict mapping (year,week) -> {'local':bool,'bucket':bool}.
    """
    keys = set(local_weeks) | set(bucket_weeks)
    status = {}
    for k in keys:
        status[k] = {
            "local": k in local_weeks,
            "bucket": k in bucket_weeks,
        }
    return status


def _week_key_to_str(tpl: tuple) -> str:
    return f"{tpl[0]:04d}-{tpl[1]:02d}"


def _str_to_week_key(s: str) -> tuple:
    y, w = s.split("-")
    return (int(y), int(w))


def get_week_status_path() -> Path:
    return get_appdata_dir() / "week_status.json"


def save_week_status(week_status: dict):
    # Accept dict with tuple keys -> convert to string keys
    data = { _week_key_to_str(k): v for k, v in week_status.items() }
    path = get_week_status_path()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_week_status() -> dict:
    path = get_week_status_path()
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return { _str_to_week_key(k): v for k, v in raw.items() }
