# aw-watcher-mpv
An [ActivityWatch](https://github.com/ActivityWatch/activitywatch) watcher to report on when there's a video playing in mpv, and what it is.
Currently, only provides heartbeat events with the video's title and filename. This is enough to see what you watched and for how long.
The bucket used is `aw-watcher-mpv-curplaying_CLIENTHOSTNAME`.

Notably, **it works by scanning logs provided by another utility**. This repo is for the `-sender` part that scans the logs. The other part is [aw-watcher-mpv-logger](https://github.com/RundownRhino/aw-watcher-mpv-logger) - an `mpv` plugin that records the events as text files that the sender then scans.

## Installation
Can be installed with `pip`. For example, to get current master:
```
pip install git+https://github.com/RundownRhino/aw-watcher-mpv-sender
```

## Usage
1. Install [aw-watcher-mpv-logger](https://github.com/RundownRhino/aw-watcher-mpv-logger) by following the installation instructions there.
2. Install `aw-watcher-mpv-sender` by following the instructions above.
3. Launch `aw-watcher-mpv-sender` via the command line, passing it the log folder of the logger. You'll probably want to make a script for this. Example `.bat`:
```bat
title aw-watcher-mpv
python -m aw-watcher-mpv-sender "C:\Program Files\mpv\mpv-history"
pause
```
4. Watch a video in mpv, and a few dozen seconds later you should start seeing the heartbeats. You may need to reopen the web UI.

## TODOs and known issues
- [ ] Currently, the log file for today is fully scanned every five seconds. This isn't *too* bad as the log file can't be more than a few megabytes for a full day, but a better way should be implemented later.
- [ ] Because the sender only checks the current day's logs, the last event or two from the last day (so, ~10 seconds of viewing time) may be lost. More generally, it doesn't scan old logs to discover events there.
- [ ] Visualizations? Would be nice to have something like "video titles by playing time".
- [ ] Counting video playing time as non-afk. That actually seems easy-ish to implement dashboard-side; it'd require adding another union [here](https://github.com/ActivityWatch/aw-webui/blob/74778e06d2ad702ff3e60582f28b3fda043f0488/src/queries.ts#L124-L130). Doing this in a generic fashion would of course need a PR.
