# Upgrade: Private-tracker extras

**Only for people who use private trackers** (invite-only torrent sites that expect you
to keep seeding). With only public sites, skip this.

- **cross-seed** notices when a torrent you already have also exists on your *other*
  private trackers, and seeds it there too, with no extra download and no extra space.
- **qbit_manage** cleans up. A torrent keeps seeding **forever while the movie/show is in
  your library**. Once you delete it from the library, it seeds 2 more weeks (to meet
  tracker rules), then the torrent and its files are deleted. Without this, deleted movies
  keep using disk space as torrents forever.

Prerequisites: stage 2 done, the library has at least ~20 movies/episodes, Radarr/Sonarr
have the 7-day **recycling bin** set (stage 2, steps 9–10), and `QBIT_PASS` is set in `.env`.

---

## 1. cross-seed

1. In Prowlarr, find the ID of each **private** tracker: click the tracker in **Indexers**;
   the number at the end of the browser's address is its ID. (The AI can also list
   them: `curl -s -H "X-Api-Key: $(sed -n 's/^PROWLARR_API_KEY=//p' .env)" http://localhost:9696/api/v1/indexer | python3 -c 'import json,sys; [print(i["id"], i["name"], i["privacy"]) for i in json.load(sys.stdin)]'`.)
2. Put them in `.env`: `CROSS_SEED_INDEXER_IDS=3,5,8`
3. ```bash
   cd ~/media-server && ./scripts/install-config.py cross-seed
   ```
4. Add `trackers` to `COMPOSE_PROFILES`, then `docker compose up -d`.
5. Check the log:
   ```bash
   docker logs cross-seed --tail 50
   ```
   It should validate the config and list your trackers. Over the next day, torrents with
   category `cross-seed-link` appear in qBittorrent.

The config always uses **hardlinks**. Don't change `linkType` to symlinks: with symlinks,
deleting an original torrent breaks every cross-seed of it.

---

## 2. qbit_manage (cleanup)

### How a deletion flows

```
You (or someone in Seerr) delete a movie
  → Radarr moves it to /data/drive1/recycle for 7 days   (your undo window)
  → after 7 days the library copy is gone; the torrent has no library hardlink left
  → qbit_manage tags it "noHL"
  → it seeds until it has 2 weeks of total seeding time, then it's stopped and deleted
  → the deleted files wait 3 more days in torrents/.RecycleBin, then they're gone
```

Tag any torrent `keep` in qBittorrent to protect it forever.

`scripts/qbit_manage/keep_copies.py` runs before every pass. If the library holds a
*copy* of a file instead of a hardlink (a manual copy, or an import across two drives),
the torrent would look deleted. This script spots those and tags them `keep`. If anything
looks wrong (drive missing, tiny library, can't log in to qBittorrent), qbit_manage doesn't
run at all.

### Set it up

1. Copy in the config:
   ```bash
   ./scripts/install-config.py qbit_manage
   ```
2. Edit `appdata/qbit_manage/config.yml`:
   - `max_seeding_time: 2w`: check your trackers' rules. If any needs longer, raise it.
   - `tracker:`: add one line per tracker, so torrents get tagged by site (optional).
   - **Leave `dry_run: true`** for now.
3. Run one pass by hand:
   ```bash
   ./scripts/qbit_manage/run.sh
   tail -n 20 appdata/qbit_manage/logs/keep_copies.log
   tail -n 80 appdata/qbit_manage/logs/qbit_manage.log
   ```
4. Install the 30-minute timer (cron):
   ```bash
   (crontab -l 2>/dev/null; echo "*/30 * * * * $HOME/media-server/scripts/qbit_manage/run.sh") | crontab -
   crontab -l
   ```

### Turn on real deletion (after a few days)

> **AI:** don't skip this check. Read the qbit_manage log with the person. Every torrent it
> says it would tag `noHL` or delete must really be gone from the library (search for it in
> Radarr/Sonarr and Plex). If anything still in the library shows up, stop and find out why
> before going further.

When it looks right, change `dry_run: true` to `dry_run: false` in
`appdata/qbit_manage/config.yml`. The next pass (within 30 minutes) is live.

### Gotchas

- Setting `QBT_DRY_RUN` in the environment does nothing; only `dry_run:` in the file counts.
- qbit_manage rewrites its own `config.yml` when it starts. Comments may move; that's normal.
- Don't add a schedule to the container. Cron + `run.sh` is what makes sure `keep_copies.py` runs first.
- To pause it: `crontab -e` and put `#` in front of the line.

## Done when

- [ ] `docker logs cross-seed` shows it searching your trackers without errors
- [ ] qbit_manage dry-run logs look right for a few days, then `dry_run: false`
- [ ] `crontab -l` shows the `run.sh` line
- [ ] `./scripts/doctor.sh` shows no ✘
