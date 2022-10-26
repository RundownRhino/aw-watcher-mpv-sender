from __future__ import annotations
from dataclasses import dataclass, field
import json
from pathlib import Path
import time
import datetime as DT
from typing import Optional


from aw_core.models import Event
from aw_client.client import ActivityWatchClient
from .utils import parse_timestamp, log_error, today_filename
from .models import PlayingHeartbeat


@dataclass
class Sender:
    log_folder: Path
    client: ActivityWatchClient

    # Note: the logs may absolutely have duplicate timestamps, since
    # they only have precision down to a second
    last_heartbeat: Optional[DT.datetime] = None
    buckets_created: set[tuple[str, str]] = field(default_factory=set)

    def __post_init__(self):
        if self.last_heartbeat is None:
            bucket_id = f"{self.client.client_name}-curplaying_{self.client.client_hostname}"
            self.create_bucket_once(bucket_id, "curplaying")
            last_event = self.client.get_events(bucket_id, limit=1)
            if not last_event:
                return
            self.last_heartbeat = last_event[0].timestamp
            print(f"Fetched last timestamp as {self.last_heartbeat.isoformat()}, ignoring events before that.")

    def process_logs(self) -> int:
        """
        Returns the number of possibly-new events seen.
        """
        log = self.log_folder / today_filename()
        if not log.exists():
            return False
        new_seen = 0

        # TODO: is utf-8 a good choice? on mpv's side we use io.open without a specific encoding
        with log.open("rt", encoding="utf-8") as fo:
            with self.client:
                for line in fo:
                    line = line.strip()
                    if not line:
                        continue
                    new_seen += self.process_event(line)
        return new_seen

    def process_event(self, line: str) -> bool:
        """
        Returns whether the event was possibly-new.
        """
        try:
            event = json.loads(line)
        except json.JSONDecodeError as e:
            # TODO: better warning logs?
            # though invalid json might just mean that line wasn't fully written yet.
            log_error("Couldn't decode log line", e)
            return False
        try:
            timestamp = parse_timestamp(event["time"])
            if self.last_heartbeat is not None and timestamp < self.last_heartbeat:
                return False  # event already should have been seen.
            self.send_event(event)
            self.last_heartbeat = timestamp
            return True
        except Exception as e:
            log_error(f"Couldn't process JSON event {event} :", e)
            return False

    def send_event(self, event: dict) -> None:
        # TODO: it would be nice not to resend the last events to the server many times.
        kind = event["kind"]
        if kind != "playing":
            return  # for now we only handle playing heartbeats

        hb_event: PlayingHeartbeat = event  # type:ignore

        event_type = "curplaying"
        bucket_id = f"{self.client.client_name}-{event_type}_{self.client.client_hostname}"
        self.create_bucket_once(bucket_id=bucket_id, event_type=event_type)
        heartbeat_data = {"filename": hb_event["filename"], "title": hb_event["title"]}

        event = Event(timestamp=parse_timestamp(hb_event["time"]), data=heartbeat_data)
        self.client.heartbeat(bucket_id, event, pulsetime=10, commit_interval=10, queued=True)

    def run(self):
        print("Now running.")
        while True:
            try:
                cnt = self.process_logs()
                if cnt:
                    pass
                    # print(f"{cnt} new events sent.")
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
