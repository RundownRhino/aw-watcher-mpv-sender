from typing import Literal, TypedDict


class PlayingHeartbeat(TypedDict):
    time: str  # datetime
    filename: str
    title: str  # media-title, which falls back to filename if not present
    # length: str  # float
    # path: str
    # pos: str  # float
    kind: Literal["playing"]
