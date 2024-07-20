from __future__ import annotations

import datetime as DT
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from aw_client.client import ActivityWatchClient

from aw_watcher_mpv_sender.models import CurplayingHeartbeat
from aw_watcher_mpv_sender.utils import LRUSet, __version__, log_error, parse_timestamp, today_filename

logger = logging.getLogger(__name__)


@dataclass
class Sender:
    log_folder: Path
    client: ActivityWatchClient

    # Note: the logs may absolutely have duplicate timestamps, since
    # they only have precision down to a second
    last_heartbeat: Optional[DT.datetime] = None
    buckets_created: set[tuple[str, str]] = field(default_factory=set)
    last_log_path: Optional[Path] = None
    last_position: Optional[int] = None
    last_sent_events: LRUSet[CurplayingHeartbeat] = field(default_factory=lambda: LRUSet(50))

    def __post_init__(self):
        logger.info(f"aw-watcher-mpv-sender initializing. Version is {__version__}, platform is {sys.platform}.")
        if self.last_heartbeat is None:
            bucket_id = f"{self.client.client_name}-curplaying_{self.client.client_hostname}"
            self.create_bucket_once(bucket_id, "curplaying")
            last_event = self.client.get_events(bucket_id, limit=1)
            if not last_event:
                return
            self.last_heartbeat = last_event[0].timestamp
            logger.info(f"Fetched last timestamp as {self.last_heartbeat.isoformat()}, ignoring events before that.")

    def process_logs(self) -> int:
        """
        Returns the number of possibly-new events seen.
        """
        log = self.log_folder / today_filename()
        if not log.exists():
            return False
        new_seen = 0

        # On the mpv side we may occasionally produce non-unicode titles (which are therefore invalid JSON).
        # This is hard to fix, so as a safety measure we discard such lines.
        # Hence, read as binary.
        with log.open("rb") as fo:
            if self.last_log_path == log and self.last_position is not None:
                fo.seek(self.last_position)
            else:
                self.last_log_path = log
                self.last_position = None
            # this prevents tell being disabled from using next:
            for bline in iter(fo.readline, b""):
                bline = bline.strip()
                if not bline:
                    continue
                try:
                    line = bline.decode("utf-8")
                except UnicodeDecodeError as e:
                    logger.warning("Skipping a line due to a UTF-8 decoding error", exc_info=True)
                    continue
                cur_ok = self.process_event(line)
                new_seen += cur_ok
                # If this event was sent successfully, we update the stored position to right after it
                # If not, then possibly event is last in file and only partially written, and so we should reread it next time.
                if cur_ok:
                    self.last_position = fo.tell()
        return new_seen

    def process_event(self, line: str) -> bool:
        """
        Returns whether the event was possibly-new.
        """
        try:
            event = json.loads(line)
        except json.JSONDecodeError as e:
            # invalid json might just mean that line wasn't fully written yet, so it's not very serious - maybe warning?
            log_error("Couldn't decode log line", e)
            return False
        try:
            timestamp = parse_timestamp(event["time"])
            if self.last_heartbeat is not None and timestamp < self.last_heartbeat:
                return False  # event already should have been seen.
            res = self.send_event(event)
            self.last_heartbeat = timestamp
            return res
        except Exception as e:
            log_error(f"Couldn't process JSON event {event} :", e)
            return False

    def send_event(self, raw_event: dict) -> bool:
        kind = raw_event["kind"]
        if kind != "playing":
            return False  # for now we only handle playing heartbeats
        event_type = "curplaying"
        bucket_id = f"{self.client.client_name}-{event_type}_{self.client.client_hostname}"
        self.create_bucket_once(bucket_id=bucket_id, event_type=event_type)
        hb = CurplayingHeartbeat.from_dict(raw_event)
        if hb in self.last_sent_events:
            return False
        self.last_sent_events.push(hb)
        self.client.heartbeat(bucket_id, hb.to_event(), pulsetime=10, commit_interval=10, queued=True)
        return True

    def run(self):
        logger.info("Now running.")
        with self.client:
            while True:
                try:
                    cnt = self.process_logs()
                    if cnt:
                        logger.debug(f"{cnt} new events sent.")
                    time.sleep(5)
                except KeyboardInterrupt:
                    break

    def create_bucket_once(self, bucket_id: str, event_type: str):
        """
        Creates a bucket if it wasn't already created (to avoid an extra request per event).
        """
        key = (bucket_id, event_type)
        if key not in self.buckets_created:
            self.client.create_bucket(bucket_id, event_type)
            self.buckets_created.add(key)
