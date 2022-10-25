import datetime as DT
import sys
import traceback


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
    print(msg, traceback.format_exception(e), file=sys.stderr)


def parse_timestamp(ts: str) -> DT.datetime:
    res = DT.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    return res.replace(tzinfo=DT.timezone.utc)
