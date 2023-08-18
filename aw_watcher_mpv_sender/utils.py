from __future__ import annotations

import datetime as DT
import logging
from collections import deque
from functools import cache
from typing import Collection, Generic, Hashable, Iterator, TypeVar

HashableT = TypeVar("HashableT", bound=Hashable)

logger = logging.getLogger(__name__)


def utcnow() -> DT.datetime:
    """
    Gives the current UTC time. Not the same as datetime.utcnow().
    """
    return DT.datetime.now(tz=DT.timezone.utc)


def today_filename() -> str:
    """
    Returns the filename that today's log file of mpv-aw-watcher-logger should have.
    """
    return utcnow().strftime("%Y-%m-%d") + ".log"


def log_error(msg: str, e: BaseException):
    logger.error(msg, exc_info=e)


def parse_timestamp(ts: str) -> DT.datetime:
    res = DT.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    return res.replace(tzinfo=DT.timezone.utc)


class LRUSet(Generic[HashableT], Collection):
    """
    An ordered set that stores only maxlen last elements.
    """

    def __init__(self, maxlen: int):
        assert maxlen > 0
        self._maxlen = maxlen
        self._queue: deque[HashableT] = deque(maxlen=maxlen)
        self._set: set[HashableT] = set()

    def __len__(self) -> int:
        return len(self._queue)

    def remove(self, el: HashableT):
        self._queue.remove(el)
        self._set.remove(el)

    def push(self, el: HashableT):
        if el in self._set:
            self.remove(el)  # we want to move it to the end of the queue if so.
        if len(self) == self._maxlen:
            self.pop()
        self._queue.append(el)
        self._set.add(el)

    def pop(self) -> HashableT:
        oldest = self._queue.popleft()
        self._set.remove(oldest)
        return oldest

    def __iter__(self) -> Iterator[HashableT]:
        return iter(self._queue)

    def __contains__(self, el: HashableT) -> bool:
        return el in self._set


@cache
def __version__() -> str:
    try:
        import pkg_resources

        return pkg_resources.get_distribution("aw-watcher-mpv-sender").version
    except (ImportError, TypeError):
        return "<unknown>"
