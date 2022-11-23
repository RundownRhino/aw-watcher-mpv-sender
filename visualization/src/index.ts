import { AWClient } from "aw-client";
import { CurplayingHeartbeat } from "./models";
import { enumerate, map, sortDict } from "./utils";

const url = new URL(window.location.href);

let today_start = new Date();
today_start.setHours(0, 0, 0, 0);
let today_end = new Date();
today_end.setHours(23, 59, 59, 999);

const start = map(url.searchParams.get("start"), x => new Date(x)) ?? today_start;
const end = map(url.searchParams.get("end"), x => new Date(x)) ?? today_end;
const hostname = url.searchParams.get("hostname");

const aw = new AWClient("aw-watcher-mpv", { testing: false, baseURL: url.origin })

function load() {
    const statusEl = document.getElementById("status");
    const tableEl = document.getElementById("aw-watcher-mpv-vis-table");
    const bucketName = `aw-watcher-mpv-curplaying_${hostname}`;

    aw.getBuckets()
        .then((bs) => {
            if (bs[bucketName] === undefined) {
                throw `no bucket called ${bucketName}`;
            }
        })
        .then(() => {
            return aw.getEvents(bucketName, { start: start, end: end }) as Promise<CurplayingHeartbeat[]>;
        })
        .then((events) => {
            const groups: { [key: string]: number } = {};
            events.forEach(el => {
                if (el.duration) {
                    groups[el.data.title] = (groups[el.data.title] ?? 0) + el.duration
                }
            });

            for (let [i, [title, duration]] of enumerate(Object.entries(sortDict(groups, (a, b) => -(a - b))))) {
                if (i == 10) { break; }
                const human_duration = `${Math.round(duration)}s`; // TODO
                const tr = document.createElement('tr');
                const td = document.createElement('td');
                td.innerHTML = `<td>${title}: ${human_duration} </td>`;

                tr.appendChild(td)
                // @ts-ignore - the catch will catch it if this is null.
                tableEl.appendChild(td);
            }
        })
        .catch((msg) => statusEl?.append(msg));
}
load();