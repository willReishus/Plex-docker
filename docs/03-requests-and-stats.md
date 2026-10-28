# Upgrade: Request page + watch stats

**Seerr** gives family and friends a simple site where they search for a movie or show
and click **Request**. It lands in Radarr/Sonarr automatically. **Tautulli** shows
who's watching what, and the history. About 30 minutes.

Prerequisite: stage 2 done.

## 1. Switch it on

In `.env`, add `requests` to `COMPOSE_PROFILES` (e.g. `COMPOSE_PROFILES=requests`), then:

```bash
cd ~/media-server && docker compose up -d
```

## 2. Seerr

Open `http://SERVER_IP:5055`.

1. Choose **Plex** and sign in with your Plex account.
2. Plex server: enter it by hand. Hostname = your `SERVER_IP`, port `32400`
   (it can't use the name `plex`). Save → **Sync Libraries** → tick Movies and TV Shows
   → **Start Scan**.
3. **Add Radarr server**:
   - Default Server ✔, Server Name `Radarr`, Hostname `radarr`, Port `7878`
   - API key: from `.env` (`RADARR_API_KEY`) or Radarr → Settings → General
   - Test, then choose Quality Profile (e.g. HD-1080p) and Root Folder `/data/drive1/media/movies`
   - Enable Scan ✔ · Enable Automatic Search ✔
4. **Add Sonarr server**: Hostname `sonarr`, Port `8989`, its API key, Root Folder
   `/data/drive1/media/tv`, Season Folders ✔.
5. Finish.

### Let people in

1. First share your Plex library with them: Plex → **Settings → Manage Library Access**
   (or plex.tv → Friends) → invite by email.
2. Seerr → **Users → Import Plex Users**.
3. Click a user → **Permissions**. A good default: **Request** + **Auto-Approve**
   (requests go straight through, so you don't have to approve each one).
   - **Manage Requests** also lets them *remove* movies/shows, and that means **any**
     movie or show, not only theirs. Will gives it to his roommates; decide for yourself.
4. Send them the link `http://SERVER_IP:5055` (or `http://requests.lan` after the
   [names upgrade](05-dashboard-and-names.md)). Seerr only works at home unless you
   set up remote access separately.

## 3. Tautulli

Open `http://SERVER_IP:8181` and follow the setup wizard:

- Sign in with Plex.
- Plex IP or hostname: your `SERVER_IP`, port `32400`, SSL off. Verify.
- Finish. History starts from now.

## 4. Save the new keys

```bash
./scripts/collect-keys.py
```

This adds `SEERR_API_KEY` and `TAUTULLI_API_KEY` to `.env`, for the dashboard later.

## Good to know

- A request stuck on **"Processing"** when the file is already in Plex almost always
  means Plex matched it to the wrong title. In Plex: the item's **⋯ → Fix Match**.
- If a movie gets deleted and re-added in Radarr, Seerr can keep pointing at the old one.
  Removing and re-requesting it in Seerr fixes it.

## Done when

- [ ] A test request in Seerr shows up in Radarr and downloads
- [ ] Someone else can sign into Seerr with their Plex account
- [ ] Tautulli shows activity when you play something
- [ ] `./scripts/doctor.sh` shows no ✘
