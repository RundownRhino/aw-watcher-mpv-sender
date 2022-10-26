import argparse
from pathlib import Path

from .sender import Sender
from aw_client.client import ActivityWatchClient


def main():
    parser = argparse.ArgumentParser(description="Starts the sender")
    parser.add_argument("log_folder", type=Path, help="the folder aw-watcher-mpv-logger writes logs to")
    args = parser.parse_args()
    log_folder: Path = args.log_folder
    if not log_folder.exists():
        try:
            log_folder = log_folder.resolve()  # for better error message, try to resolve if possible
        except:
            raise ValueError("Path couldn't be resolved:", log_folder)
        raise ValueError("Path doesn't exist:", log_folder)

    run_with(log_folder)


def run_with(log_folder: Path):
    Sender(log_folder=log_folder, client=ActivityWatchClient(client_name="aw-watcher-mpv")).run()
