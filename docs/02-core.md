# Stage 2: The core

**Goal:** Plex, Radarr, Sonarr, Prowlarr and qBittorrent running and wired together. You
add a movie in Radarr and it ends up playable in Plex on its own. About 1–2 hours.

All commands run in the repo folder:

```bash
cd ~/media-server
```

## 1. Create your settings file

```bash
cp .env.example .env
id -u; id -g; timedatectl show -p Timezone --value
nano .env
```

In `nano`, set:

| Setting | Value |
|---|---|
| `PUID` / `PGID` | the two numbers `id -u` and `id -g` printed (usually 1000 / 1000) |
| `TZ` | the time zone `timedatectl` printed, e.g. `America/Chicago` |
| `SERVER_IP` | the reserved address from stage 1 |
| `SERVER_NAME` | any name, e.g. `Smith Media` |
| `DATA_DIR` | `/mnt/data` (leave as is if you followed stage 1) |

Leave the rest for now. Save with **Ctrl+O**, **Enter**, and exit with **Ctrl+X**.

## 2. Make the folders

```bash
./scripts/setup-folders.sh
```

## 3. (Optional) Hardware transcoding

Only matters if you have Plex Pass. Check for Intel graphics with `ls /dev/dri`. If it
lists `renderD128`, set `COMPOSE_FILE=compose.yaml:extras/gpu-intel.yaml` in `.env`.
NVIDIA needs extra setup first (docs/07); skip it for now.

## 4. Start everything

Get a Plex claim code at <https://plex.tv/claim> (sign in first). It expires in
4 minutes, so paste it into `.env` as `PLEX_CLAIM=claim-xxxx` and run straight away:

```bash
docker compose up -d
```

The first time, this downloads every app (a few minutes). Then check:

```bash
docker compose ps
```

All six should say `running` / `Up`. Afterwards, clear `PLEX_CLAIM=` in `.env` (it's
single-use anyway).

## 5. Plex

Open `http://SERVER_IP:32400/web` in a browser on any computer at home.

1. Sign in. Give the server a name. You can leave "Allow me to access my media outside my
   home" on.
2. **Add Library → Movies** → Add folder → `/data/drive1/media/movies`.
3. **Add Library → TV Shows** → Add folder → `/data/drive1/media/tv`.
4. **Settings (wrench) → Library**: turn **off** "Scan my library automatically" and
   "Run a partial scan when changes are detected". Radarr and Sonarr tell Plex about new
   files instead (steps 9 and 10), so it doesn't scan twice.
5. **Settings → Remote Access**: if it shows red, your router needs port **32400** forwarded
   to `SERVER_IP` (or turn on UPnP in the router). The AI can help find the setting.
6. If you have Intel graphics and Plex Pass: **Settings → Transcoder** → tick "Use hardware
   acceleration when available".

## 6. qBittorrent

1. Find the temporary password:
   ```bash
   docker logs qbittorrent 2>&1 | grep -i password
   ```
2. Open `http://SERVER_IP:8080`, log in as `admin` with that password.
3. **Tools → Options → Web UI**: set your own username and password. Put the same values in
   `.env` as `QBIT_USER` and `QBIT_PASS` (with `nano .env`).
4. **Options → Downloads**:
   - Default Torrent Management Mode: **Automatic**
   - When Torrent Category changed / Default Save Path changed / Category Save Path changed:
     **Relocate torrent**
   - Default Save Path: `/data/drive1/torrents`
   - "Keep incomplete torrents in": **unticked**
5. **Options → Connection**: Listening port = your `TORRENT_PORT` (6881 by default).
   UPnP on. For best speeds, forward that port (TCP+UDP) to `SERVER_IP` on the router.
6. **Options → BitTorrent**: Seeding limits **off** (all unticked). Queueing: max active
   downloads 5, max active uploads and max active torrents **1000** (so seeding never stops).
7. **Save.** Then in the left panel, right-click **Categories → Add category**:
   - `radarr` → save path `/data/drive1/torrents/movies`
   - `tv-sonarr` → save path `/data/drive1/torrents/tv`

## 7. Prowlarr (the torrent-site list)

Open `http://SERVER_IP:9696`. The first time, it asks you to set up a login: choose
**Forms**, set a username and password (use the same login for Radarr and Sonarr to keep
things simple).

1. **Settings → Indexers → +** → **FlareSolverr**. Tags: `flaresolverr`.
   Host: `http://flaresolverr:8191`. Save.
2. **Indexers → Add Indexer**: add the sites you'll use. Private trackers need your
   account's API key or cookie from that site. If a site fails its test with a Cloudflare
   error, edit it and add the `flaresolverr` tag.
3. **Settings → Apps** comes after Radarr and Sonarr exist (step 11).

## 8. Find the API keys

```bash
./scripts/collect-keys.py
```

This copies Radarr's, Sonarr's and Prowlarr's API keys into `.env`. It prints what it
found, never the keys themselves.

## 9. Radarr (movies)

Open `http://SERVER_IP:7878`, set up the login (Forms) like Prowlarr.

**Settings → Media Management** (click **Show Advanced** at the top):
- Rename Movies: **on**
  - Standard Movie Format: `{Movie Title} ({Release Year}) {Quality Full}`
  - Movie Folder Format: `{Movie Title} ({Release Year})`
- Unmonitor Deleted Movies: **on**
- Use Hardlinks instead of Copy: **on**
- Import Extra Files: off
- Recycling Bin: `/data/drive1/recycle/` · Recycling Bin Cleanup: **7** days
- Root Folders → Add → `/data/drive1/media/movies/`
- Save

**Settings → Download Clients → + → qBittorrent**:
- Host `qbittorrent`, Port `8080`, your qBittorrent username and password
- Category: `radarr`
- **Remove Completed: OFF** (important: torrents keep seeding)
- Test → Save

**Settings → Connect → + → Plex Media Server**:
- Host: your `SERVER_IP`, Port `32400`
- Click **Authenticate with Plex.tv**
- Notification triggers: On Import, On Upgrade, On Rename, On Movie Delete, On Movie File Delete
- Update Library: **on** → Test → Save

## 10. Sonarr (TV)

Open `http://SERVER_IP:8989`. Same as Radarr, with these differences:

- Episode format: `{Series Title} - S{season:00}E{episode:00} - {Episode Title} {Quality Full}`
- Series Folder Format: `{Series Title}` · Season Folder Format: `Season {season}`
- Unmonitor Deleted Episodes: **on**
- Recycling Bin `/data/drive1/recycle/`, cleanup 7 days, hardlinks on
- Root folder: `/data/drive1/media/tv/`
- qBittorrent category: `tv-sonarr`, **Remove Completed: OFF**
- Connect → Plex Media Server, same as Radarr

## 11. Connect Prowlarr to Radarr and Sonarr

In Prowlarr: **Settings → Apps → + → Radarr**:
- Prowlarr Server `http://prowlarr:9696`, Radarr Server `http://radarr:7878`
- API Key: Radarr's (Radarr → Settings → General → API Key)
- Sync Level: Full Sync → Test → Save

Do the same for **Sonarr** (`http://sonarr:8989`, Sonarr's API key). In a minute,
Radarr's and Sonarr's **Settings → Indexers** fill with your sites.

## 12. The real test

Pick a movie and test the whole chain. *Night of the Living Dead (1968)* is public domain,
so it makes a good test.

1. Radarr → **Add New** → search it → Root folder `/data/drive1/media/movies`,
   Quality profile **HD-1080p**, tick **Start search for missing movie** → Add.
2. Watch it appear in qBittorrent under category `radarr`.
3. When it finishes, Radarr imports it within a minute or two (**Activity** tab).
4. It appears in Plex.
5. Prove it's a hardlink, not a copy:
   ```bash
   find /mnt/data/media/movies -type f -size +100M -exec stat -c '%h links  %n' {} \;
   ```
   It should say **2 links**. If it says 1, the hardlink setting or paths are wrong;
   see troubleshooting.

## 13. Health check

```bash
./scripts/doctor.sh
```

Fix anything marked ✘ before moving on.

## Before you download a lot: VPN?

Some people route downloads through a VPN for privacy. Will runs NordVPN on the whole
server. If you want one, see "VPN" in [docs/07](07-maintenance.md#vpn) before you start
downloading heavily. It's optional and up to you.

## Done when

- [ ] `docker compose ps` shows all six core apps up
- [ ] A movie added in Radarr downloads, imports, and plays in Plex
- [ ] The imported file shows **2 links**
- [ ] A TV show added in Sonarr does the same
- [ ] `./scripts/doctor.sh` shows no ✘
- [ ] `my-setup.md` updated: stage 2 done

**Use it for a few days.** Then pick an upgrade:
[requests & stats](03-requests-and-stats.md) ·
[quality & polish](04-quality-and-polish.md) ·
[dashboard & names](05-dashboard-and-names.md) ·
[private trackers](06-private-trackers.md)
