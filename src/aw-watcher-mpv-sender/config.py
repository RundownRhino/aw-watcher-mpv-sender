from typing import TypedDict

from aw_core.config import load_config_toml

default_log_folder = "full/path/to/log/folder"
default_config = f"""
log_folder = "{default_log_folder}"
"""


class Config(TypedDict):
    log_folder: str


CONFIG: Config = load_config_toml("aw-watcher-mpv", default_config=default_config)  # type:ignore
if not isinstance(CONFIG, dict):
    raise ValueError("the configuration TOML wasn't a dictionary - perhaps you used a group?", CONFIG)
