from typing import TypedDict

from aw_core.config import load_config_toml

default_log_folder = "full/path/to/log/folder"
default_connection_sleep: float = 30

default_config = f"""

log_folder = "{default_log_folder}"
# How long to wait before retrying if the watcher can't connect to the server at the start (in seconds). This defaults to a fairly large {default_connection_sleep}s because the server may take a while to start in 0.14, see aw-watcher-mpv-sender#10.
server_connection_sleep = {default_connection_sleep}

"""


class Config(TypedDict):
    log_folder: str
    server_connection_sleep: float


CONFIG: Config = load_config_toml("aw-watcher-mpv", default_config=default_config)  # type: ignore
if not isinstance(CONFIG, dict):
    raise ValueError("the configuration TOML wasn't a dictionary - perhaps you used a group?", CONFIG)
