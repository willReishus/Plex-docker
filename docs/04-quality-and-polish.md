# Upgrade: Better quality, posters, and live TV

Three independent pieces. Do any or all of them, in any order.

| Piece | What it does | Turn on |
|---|---|---|
| Recyclarr | Copies the expert [TRaSH guides](https://trash-guides.info) quality rules into Radarr/Sonarr, and keeps them updated daily | `quality` |
| Kometa | Badges on posters (4K, HDR, …) and ready-made collections (IMDb Top 250, genres, franchises) | `kometa` |
| Tunarr | 24/7 "TV channels" from your own library (a cartoon channel, an 80s movie channel…), shown in Plex's Live TV | `tunarr` |

Prerequisite: stage 2 done, and `./scripts/collect-keys.py` has been run.

---

## Recyclarr: smarter quality choices

Out of the box, Radarr grabs anything labeled "1080p". The TRaSH profiles prefer good
release groups and avoid bad encodes.

> **AI:** ask how big the drive is and how much they care about picture quality.
> The template uses Will's **"Remux + WEB"** profiles: top quality, but movies are often
> 20–40 GB (1080p) or 40–80 GB (4K). With less than ~20 TB, suggest the smaller TRaSH
> profiles instead ("HD Bluray + WEB" for Radarr, "WEB-1080p" for Sonarr). Look up their
> `trash_id` values at <https://recyclarr.dev/guide/> and edit the templates.

1. Copy in the config:
   ```bash
   cd ~/media-server && ./scripts/install-config.py recyclarr
   ```
   (It lands in `appdata/recyclarr/configs/`; edit it there if you change profiles.)
2. Add `quality` to `COMPOSE_PROFILES` in `.env`, then:
   ```bash
   docker compose up -d
   docker exec recyclarr recyclarr sync
   ```
   The sync output should end without red errors and list the profiles it created.
3. In Radarr: **Movies → Select Movies → select all → Edit** → set Quality Profile to
   the new one. Same in Sonarr for series.
4. If you use Seerr: Settings → Services → edit Radarr/Sonarr → set the new default profile.

It re-syncs every day by itself.

---

## Kometa: posters and collections

1. Get a free TMDB API key: create an account at <https://www.themoviedb.org>, then
   **Settings → API** → request a key (choose "Personal"). Copy the **API Key** (the
   short one, not the "Read Access Token") into `.env` as `TMDB_API_KEY=`.
2. Make sure `PLEX_TOKEN` is filled in `.env` (`./scripts/collect-keys.py` does it).
3. Copy in the config (this fills in your keys and IP):
   ```bash
   ./scripts/install-config.py kometa
   ```
   Your Plex libraries must be named exactly **Movies** and **TV Shows**, or edit the
   names in `appdata/kometa/config.yml`.
4. Add `kometa` to `COMPOSE_PROFILES`, then `docker compose up -d`.
5. It runs every night at 3am. To run it right now (the first run can take an hour or more):
   ```bash
   docker compose run --rm -e KOMETA_RUN=true kometa
   ```
6. Check Plex: posters get resolution badges; Collections tabs fill up.

Want different collections? Kometa's defaults are listed at <https://kometa.wiki>, under
"Defaults". Edit `collection_files` / `overlay_files` in the config.

---

## Tunarr: your own TV channels

1. Add `tunarr` to `COMPOSE_PROFILES`, then `docker compose up -d`.
2. Open `http://SERVER_IP:8008`.
3. **Settings → Media Sources → Add Plex**: sign in, or enter `http://SERVER_IP:32400`
   with your Plex token.
4. **Channels → New Channel**: name it, add shows/movies, choose shuffle or in order,
   and set it to fill 24 hours.
5. Put it in Plex: Plex → **Settings → Live TV & DVR → Set up Plex DVR**. If it doesn't
   find Tunarr by itself, type `SERVER_IP:8008` as the device address. Pick the channels
   and use Tunarr's XMLTV guide when asked (`http://SERVER_IP:8008/api/xmltv.xml`).
6. Watch in Plex under **Live TV**.

---

## Done when

- [ ] (Recyclarr) the new quality profiles exist in Radarr and Sonarr and are assigned
- [ ] (Kometa) posters have badges; collections show in Plex
- [ ] (Tunarr) a channel plays in Plex's Live TV
- [ ] `./scripts/doctor.sh` shows no ✘
