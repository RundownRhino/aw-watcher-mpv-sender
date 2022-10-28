# aw-watcher-mpv
An [ActivityWatch](https://github.com/ActivityWatch/activitywatch) watcher to report on when there's a video playing in mpv, and what it is.
Currently, only provides heartbeat events with the video's title and filename. This is enough to see what you watched and for how long.
The bucket used is `aw-watcher-mpv-curplaying_CLIENTHOSTNAME`.

Notably, **it works by scanning logs provided by another utility**. This repo is for the `-sender` part that scans the logs. The other part is [aw-watcher-mpv-logger](https://github.com/RundownRhino/aw-watcher-mpv-logger) - an `mpv` plugin that records the events as text files that the sender then scans.

## Installation
Since version 0.2, `aw-watcher-mpv` gets built as a pyinstaller executable, making it a valid AW module. Get the latest release from [Releases](https://github.com/RundownRhino/aw-watcher-mpv-sender/releases/latest), or see [Build](#build) about building from source.

## Usage
1. Install [aw-watcher-mpv-logger](https://github.com/RundownRhino/aw-watcher-mpv-logger) by following the installation instructions there.
2. Download `aw-watcher-mpv-sender` by following [the instructions above](#installation).
3. Put the watcher into your ActivityWatch installation alongside the other watchers. If the path to aw-qt is `C:\Program Files\ActivityWatch\aw-qt.exe`, the path to the watcher's executable should be `I:\Program Files\ActivityWatch\aw-watcher-mpv\aw-watcher-mpv.exe`.
4. Restart ActivityWatch, and on right-clicking the tray icon you should see `aw-watcher-mpv` appear in modules, where you can start it.
5. If you want `aw-watcher-mpv` to launch automatically, add it to `autostart_modules` list of `aw-qt.toml` in the [AW Config directory](https://docs.activitywatch.net/en/latest/directories.html#config). Example config:
```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window", "aw-watcher-mpv"]
```

Alternatively to letting AW launch the watcher, you may install `aw-watcher-mpv-sender` as a python module and launch it via the command line (see `python -m aw_watcher_mpv_sender --help`).

## Build
If you need to build from source:
1. Clone the repository
2. (Optional) Create a venv with e.g. `python -m virtualenv venv` and activate it (with e.g. `./venv/Scripts/activate`).
3. `poetry install` to get all the dependencies. You may need to do `pip install poetry` first.
4. `pyinstaller --clean pyinstaller.spec` to build the module.
After this, the folder `dist/aw-watcher-mpv` will be the built module.

## TODOs and known issues
- [X] ~~Currently, the log file for today is fully scanned every five seconds. This isn't *too* bad as the log file can't be more than a few megabytes for a full day, but a better way should be implemented later.~~ - fixed, now the sender seeks to the last file end position.
- [ ] Because the sender only checks the current day's logs, the last event or two from the last day (so, ~10 seconds of viewing time) may be lost. More generally, it doesn't scan old logs to discover events there.
- [ ] Visualizations? Would be nice to have something like "video titles by playing time".
- [ ] Counting video playing time as non-afk. That actually seems easy-ish to implement dashboard-side; it'd require adding another union [here](https://github.com/ActivityWatch/aw-webui/blob/74778e06d2ad702ff3e60582f28b3fda043f0488/src/queries.ts#L124-L130). Doing this in a generic fashion would of course need a PR.
- [ ] Automatically delete old `-logger` logfiles?

## Acknowledgements
Initial draft of the logger code was based on [mpv-history.lua](https://github.com/SqrtMinusOne/dotfiles/blob/d093e755fd97a88157d10f4df7353a1729071ee5/.config/mpv/scripts/mpv-history.lua) - SqrtMinusOne graciously posted it when I asked on the AW discord if anyone knew of an existing AW watcher for mpv.