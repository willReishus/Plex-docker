# Troubleshooting

**Always start with:**

```bash
cd ~/media-server
./scripts/doctor.sh
docker logs <app-name> --tail 100     # e.g. docker logs radarr --tail 100
```

---

### A page won't open from my phone/laptop

- Is the server on and did its IP change? On the server: `hostname -I`. It must match
  `SERVER_IP` in `.env`. If not, the router reservation (stage 1, step 5) isn't working.
- Is the app running? `docker compose ps`. If it's not up: `docker compose up -d`, then
  check its log.
- Did you include the port? `http://192.168.1.50:7878`, not `http://192.168.1.50`.
- Ubuntu's firewall is off by default. If someone turned it on (`sudo ufw status`), the
  ports need allowing.

### "Permission denied" in a log, or files owned by root

`PUID`/`PGID` in `.env` must match your user (`id -u`, `id -g`). Then fix existing files:

```bash
sudo chown -R $USER:$USER /mnt/data ~/media-server/appdata
docker compose up -d --force-recreate
```

### Radarr/Sonarr: "path does not exist" or downloads never import

Every app must see the same paths. In qBittorrent, the torrent's save path should start with
`/data/drive1/torrents/`. In Radarr/Sonarr, root folders start with `/data/drive1/media/`.
If qBittorrent saved to `/downloads` or anything else, fix its default save path and category
paths (docs/02, step 6). Check **Activity → Queue** in Radarr for the exact message.

### Files use double space / `stat` shows 1 link

Hardlinks aren't happening. Check:
- Radarr/Sonarr → Media Management → "Use Hardlinks instead of Copy" is on.
- Torrents and library are on the same drive (`./scripts/doctor.sh` tests this).
- No app has a different volume mapping than `compose.yaml`.

Don't try to "fix" existing copies by deleting files by hand. Ask first.

### Downloads stuck at 0% / stalled

- Torrent has no seeders: try another release (Radarr → movie → Interactive Search).
- Port: forward `TORRENT_PORT` (TCP+UDP) on the router to `SERVER_IP`, or use UPnP.
- Disk full: `df -h /mnt/data`.

### Plex: can't find the server / "not authorized"

- Open it from the home network: `http://SERVER_IP:32400/web`.
- Unclaimed server: get a new code from <https://plex.tv/claim>, put it in `PLEX_CLAIM`
  in `.env`, then `docker compose up -d --force-recreate plex` within 4 minutes.

### Plex doesn't show new movies

- Radarr/Sonarr → Settings → Connect → Plex → **Test**. If it fails, re-authenticate.
  Host must be `SERVER_IP`, not `plex` or `localhost`.
- Manual scan: Plex → library → ⋯ → Scan Library Files.

### qBittorrent: can't log in / "banned"

Too many wrong passwords bans the address for a while. `docker compose restart qbittorrent`.

### Port 53 / 80 "address already in use" (AdGuard or Caddy won't start)

```bash
sudo ss -lntup | grep -E ':(53|80) '
```

Port 53 is usually Ubuntu's DNS stub. Redo docs/05, part B step 1.

### `.lan` names stop working (or work on and off)

- AdGuard → protection must be **enabled** (rewrites stop when it's off).
- Router's DNS must point at `SERVER_IP`. A secondary DNS (like `1.1.1.1`) causes
  on-and-off failures (docs/05, step 5).
- Test the server directly: `nslookup radarr.lan SERVER_IP`. If that works, it's the
  device or router; reconnect the device's Wi-Fi.
- The server's own browser won't resolve `.lan`; that's expected.

### Seerr request stuck on "Processing"

The file is probably in Plex under the wrong match. In Plex: item → ⋯ → **Fix Match**.

### qbit_manage didn't run

```bash
tail -n 20 ~/media-server/appdata/qbit_manage/logs/keep_copies.log
```

`keep_copies.py` stops qbit_manage on purpose if the library is missing or tiny, or if
the qBittorrent login (in `.env`) is wrong.

### Everything broke after an update

```bash
docker compose logs --tail 50
```

Find the app with errors. Usually a restart fixes it (`docker compose restart <app>`).
If an app's new version is broken, check its GitHub issues page. The AI can help find it.

### Still stuck

Collect: what you did, what you expected, what happened, the `doctor.sh` output, and the
app's log. Send that to Will.
