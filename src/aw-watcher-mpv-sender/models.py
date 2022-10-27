from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import datetime as DT
from aw_core.models import Event
from .utils import parse_timestamp


@dataclass(frozen=True)
class CurplayingHeartbeat:
    time: DT.datetime
    filename: str
    title: str
    kind: Literal["playing"]

    @classmethod
    def from_dict(cls, dct: dict[str, str]):
        assert dct["kind"] == "playing"
        return cls(time=parse_timestamp(dct["time"]), filename=dct["filename"], title=dct["title"], kind=dct["kind"])

    def to_event(self) -> Event:
        return Event(timestamp=self.time, data=dict(filename=self.filename, title=self.title))
