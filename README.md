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
4. Restart ActivityWatch, and on right-clicking the tray icon you should see `aw-watcher-mpv` appear in modules, where you can start it. On the first launch, it should fail immediately due to a lack of config.
5. In the [AW Config directory](https://docs.activitywatch.net/en/latest/directories.html#config), find the automatically created file `aw-watcher-mpv\aw-watcher-mpv.toml`. In it, you need to specify the folder `mpv-logger` is configured to log into; by default `<mpv root>/mpv_history`. For example:
```toml
log_folder = "C:/Program Files/mpv/mpv-history"
```
After this change, `aw-watcher-mpv` should launch and run correctly.

###Autolaunch
If you want `aw-watcher-mpv` to launch automatically, add it to `autostart_modules` list of `aw-qt.toml` in the [AW Config directory](https://docs.activitywatch.net/en/latest/directories.html#config). Example config:
```toml
[aw-qt]
autostart_modules = ["aw-server", "aw-watcher-afk", "aw-watcher-window", "aw-watcher-mpv"]
```

Alternatively to letting AW launch the watcher, you may install `aw-watcher-mpv-sender` as a python module and launch it via the command line (see `python -m aw_watcher_mpv_sender --help`).

###Custom visualization
If you want the custom visualization (very WIP) to work, first of all you need to either be using the Python server, or aw-server-rust of a version above v0.12.1 (you need [this commit](https://github.com/ActivityWatch/aw-server-rust/commit/8bf4cb3666bad30cfb607c606d0fbd711ac02649)). You then need to add:
```toml
[server.custom_static]
# make sure this fits your actual path to aw-watcher-mpv!
# the path HAS to use /, not \!
aw-watcher-mpv = "C:/Program Files/ActivityWatch/aw-watcher-mpv/visualization/dist"
```
into your `aw-server.toml` or your `aw-server-rust`'s `config.toml` (depending on which you're using).

After that, restart the server and do to your dashboard. Open the Activity tab. Create a new view (say, `mpv` for both id and title), click "Edit view", then "Add visualization", then click the cogwheel and select "Custom visualization". This will open a popup asking for which visualization, enter "aw-watcher-mpv" and something like "Most Watched Videos" for the title.

## Build
If you need to build from source:
1. Clone the repository
2. (Optional) Create a venv with e.g. `python -m virtualenv venv` and activate it (with e.g. `./venv/Scripts/activate`).
3. `poetry install` to get all the Python dependencies. You may need to do `pip install poetry` first.
4. (For this step, you need node - v.18 is what I use, maybe other versions work too.) You now need to build the custom visualization. For that, `cd visualization`, then do `npm install` to install all the node modules needed for building it, and `npm run build` to build it. This produces an output in `visualization/dist`.
5. `pyinstaller --clean pyinstaller.spec` to build the module.
After this, the folder `dist/aw-watcher-mpv` will be the built module.

## TODOs and known issues
- [X] ~~Currently, the log file for today is fully scanned every five seconds. This isn't *too* bad as the log file can't be more than a few megabytes for a full day, but a better way should be implemented later.~~ - fixed, now the sender seeks to the last file end position.
- [ ] Because the sender only checks the current day's logs, the last event or two from the last day (so, ~10 seconds of viewing time) may be lost. More generally, it doesn't scan old logs to discover events there.
- [ ] Visualizations? Would be nice to have something like "video titles by playing time".
- [ ] Counting video playing time as non-afk. That actually seems easy-ish to implement dashboard-side; it'd require adding another union [here](https://github.com/ActivityWatch/aw-webui/blob/74778e06d2ad702ff3e60582f28b3fda043f0488/src/queries.ts#L124-L130). Doing this in a generic fashion would of course need a PR.
- [ ] Automatically delete old `-logger` logfiles?

## Acknowledgements
Initial draft of the logger code was based on [mpv-history.lua](https://github.com/SqrtMinusOne/dotfiles/blob/d093e755fd97a88157d10f4df7353a1729071ee5/.config/mpv/scripts/mpv-history.lua) - SqrtMinusOne graciously posted it when I asked on the AW discord if anyone knew of an existing AW watcher for mpv.