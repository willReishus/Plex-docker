#!/usr/bin/env python3
"""Safety net that runs before every qbit_manage run (see run.sh and docs/06).

qbit_manage decides "deleted from the library" by hardlinks: a torrent whose
files have no hardlink outside the torrents folder gets tagged noHL and is
deleted after 2 weeks of seeding. When the library holds a separate COPY of the
file instead of a hardlink (a copy-import, a file moved by hand, a second drive),
the torrent looks deleted even though the item is still in the library. This
script tags those torrents "keep" so qbit_manage skips them.

A torrent is protected if any of its large files has no library hardlink but a
file of the exact same size exists somewhere in the library.

Usage: keep_copies.py [--dry-run]. Exits non-zero on any error, so run.sh
(`keep_copies.py && docker start -a qbit_manage`) never runs qbit_manage unprotected.
"""
import http.cookiejar, json, os, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import _env  # noqa: E402

ENV = _env.load()
QBT = "http://localhost:8080/api/v2/"
CATEGORIES = {"radarr", "tv-sonarr", "cross-seed-link"}   # the ones qbit_manage manages
DRIVES = [("/data/drive1", ENV["DATA_DIR"])]               # container path -> host path
if ENV.get("DATA2_DIR"):
    DRIVES.append(("/data/drive2", ENV["DATA2_DIR"]))
LIBRARY = [host + "/media" for _, host in DRIVES]
MIN_SIZE = 50_000_000      # ignore samples, subs, nfo
MIN_LIBRARY_FILES = 20     # fewer than this means a drive is probably not mounted: stop
DRY = "--dry-run" in sys.argv


def log(msg):
    print(time.strftime("%Y-%m-%d %H:%M:%S"), msg, flush=True)


def host_path(p):
    for c, h in DRIVES:
        if p.startswith(c):
            return h + p[len(c):]
    return p


def qbt_session():
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def call(path, data=None):
        body = urllib.parse.urlencode(data).encode() if data is not None else None
        req = urllib.request.Request(QBT + path, data=body, headers={"Referer": "http://localhost:8080"})
        return opener.open(req, timeout=60).read()

    if call("auth/login", {"username": ENV.get("QBIT_USER", ""), "password": ENV.get("QBIT_PASS", "")}) != b"Ok.":
        raise SystemExit("qBittorrent login failed (check QBIT_USER / QBIT_PASS in .env)")
    return call


def library_index():
    inodes, sizes = set(), set()
    for root in LIBRARY:
        if not os.path.isdir(root):
            raise SystemExit(f"library folder missing: {root}")   # a missing mount must not look like "not in library"
        for d, _, files in os.walk(root):
            for f in files:
                try:
                    st = os.lstat(os.path.join(d, f))
                except OSError:
                    continue
                if st.st_size >= MIN_SIZE:
                    inodes.add((st.st_dev, st.st_ino))
                    sizes.add(st.st_size)
    if len(inodes) < MIN_LIBRARY_FILES:
        raise SystemExit(f"library looks too small ({len(inodes)} files); not running qbit_manage")
    return inodes, sizes


def main():
    call = qbt_session()
    lib_inodes, lib_sizes = library_index()
    torrents = json.loads(call("torrents/info"))
    tagged = []
    for t in torrents:
        tags = {x.strip() for x in t["tags"].split(",")}
        if t["category"] not in CATEGORIES or "keep" in tags or t["progress"] < 1:
            continue
        files = json.loads(call("torrents/files?" + urllib.parse.urlencode({"hash": t["hash"]})))
        big = [f for f in files if f["size"] >= MIN_SIZE] or files
        for f in big:
            try:
                st = os.stat(host_path(os.path.join(t["save_path"], f["name"])))
            except OSError:
                continue
            if (st.st_dev, st.st_ino) not in lib_inodes and st.st_size in lib_sizes:
                tagged.append(t)
                break
    for t in tagged:
        log(f"{'would tag' if DRY else 'tagging'} keep: [{t['category']}] {t['name']}")
    if tagged and not DRY:
        call("torrents/addTags", {"hashes": "|".join(t["hash"] for t in tagged), "tags": "keep"})
    log(f"checked {len(torrents)} torrents, {len(lib_inodes)} library files; "
        f"{len(tagged)} {'would be' if DRY else ''} newly tagged keep")


if __name__ == "__main__":
    main()
