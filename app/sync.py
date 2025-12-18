import re
import json
from pathlib import Path
from collections import defaultdict
import boto3

from app.config import load_config, get_appdata_dir
from app.logger import logger


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

    logger.info("Refresh scan (local): found %d folders, %d common weeks", len(weeks_per_folder), len(set.intersection(*weeks_per_folder.values())))

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

    logger.info("Refresh scan (bucket): found %d prefixes, %d common weeks", len(weeks_per_prefix), len(set.intersection(*weeks_per_prefix.values())))

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


def download_weeks(weeks: set):
    """Download files for the given set of (year, week) tuples from the configured
    R2 bucket into the local folder structure. Returns updated week_status dict.

    The function attempts to download any objects whose filename matches the week
    and places them into <local_path>/<prefix>/<filename> where prefix is the
    top-level prefix (folder) from the bucket key (prefix/filename).
    """
    config = load_config()
    if config is None:
        raise RuntimeError("Configuration not found")

    if not weeks:
        # nothing to do, return current status
        return build_week_status(get_local_complete_weeks(), get_bucket_complete_weeks())

    s3 = boto3.client(
        "s3",
        endpoint_url=config["endpoint"],
        aws_access_key_id=config["access_key"],
        aws_secret_access_key=config["secret_key"],
    )

    bucket = config["bucket"]
    dest_path = Path(config["local_path"])

    failures = []
    downloaded = []

    logger.info("Download requested for %d weeks", len(weeks))
    # Iterate through objects and download matching ones
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
            if (year, week) not in weeks:
                continue

            # ensure local folder exists; filename may contain subpaths
            local_dir = dest_path / prefix
            local_file = local_dir / filename
            # ensure parent folders exist
            try:
                local_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                failures.append((key, f"Failed to create directory {local_file.parent}: {e}"))
                logger.error("Failed to create directory %s: %s", str(local_file.parent), e)
                continue

            # check that we can write to this directory
            try:
                test_path = local_file.parent / (".__writetest__" + local_file.name)
                with open(test_path, "w", encoding="utf-8") as fh:
                    fh.write("")
                test_path.unlink()
            except Exception as e:
                failures.append((key, f"Permission denied to write to directory {local_file.parent}: {e}"))
                logger.error("Permission denied writing to %s: %s", str(local_file.parent), e)
                continue
            # skip download if file already exists locally
            if local_file.exists():
                # record as skipped (not a failure)
                # but do not treat as downloaded
                continue

            try:
                # download object to local file path
                s3.download_file(bucket, key, str(local_file))
                downloaded.append(str(local_file))
                logger.info("Downloaded file: %s", str(local_file))
            except Exception as e:
                # cleanup partial file if created
                try:
                    if local_file.exists():
                        local_file.unlink()
                except Exception as cleanup_exc:
                    logger.warning("Failed to cleanup partial file %s: %s", str(local_file), cleanup_exc)

                failures.append((key, str(e)))
                logger.error("Failed to download %s: %s", key, e)

    # After attempting downloads, recompute status
    local_weeks = get_local_complete_weeks()
    bucket_weeks = get_bucket_complete_weeks()
    status = build_week_status(local_weeks, bucket_weeks)

    # return status, failures list and downloaded files list
    logger.info("Download complete: %d downloaded, %d failures", len(downloaded), len(failures))
    return status, failures, downloaded
