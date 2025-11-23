import os
import re
import subprocess
from datetime import datetime, timezone

import yaml
from colorama import Fore, Style


FRONT_MATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def warn(message):
    print(f"{Fore.YELLOW}WARNING: {message}{Style.RESET_ALL}")


def parse_front_matter(content):
    match = FRONT_MATTER_PATTERN.match(content)
    if match:
        metadata = yaml.safe_load(match.group(1)) or {}
        remaining = content.split("---", 2)[2].strip()
        return metadata, remaining
    return {}, content


def get_git_commit_info():
    try:
        output = subprocess.check_output(
            ["git", "log", "-1", "--format=%h %H %ct"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if output:
            parts = output.split()
            if len(parts) == 3:
                short_hash = parts[0]
                long_hash = parts[1]
                commit_ts = int(parts[2])
                commit_dt = datetime.fromtimestamp(commit_ts, tz=timezone.utc)
                return {
                    "hash": {"short": short_hash, "long": long_hash},
                    "dt": {
                        "date": {
                            "long": commit_dt.strftime("%B %d, %Y"),
                            "short": commit_dt.strftime("%Y-%m-%d"),
                        },
                        "time": commit_dt.strftime("%H:%M:%S"),
                        "iso": commit_dt.isoformat(),
                    },
                }
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        pass
    return None


def get_data():
    now = datetime.now(timezone.utc)
    return {
        "last_commit": get_git_commit_info(),
        "now": {
            "date": {
                "long": now.strftime("%B %d, %Y"),
                "short": now.strftime("%Y-%m-%d"),
            },
            "time": now.strftime("%H:%M:%S"),
            "iso": now.isoformat(),
        },
    }


def infer_page_metadata(rel_path, base_path=""):
    if rel_path == "index.html":
        canonical_path = base_path if base_path else "/"
    else:
        path_without_ext = os.path.splitext(rel_path)[0]
        canonical_path = f"{base_path}/{path_without_ext}" if base_path else f"/{path_without_ext}"

    active_page = rel_path.split("/")[0].replace(".html", "").replace(".md", "")

    if active_page == "index":
        active_page = "home"

    return active_page, canonical_path
