# How it all fits together

## The pieces, in plain words

| App | Think of it as | Web address (port) |
|---|---|---|
| **Plex** | Your own Netflix. Shows your library on every screen. | `:32400/web` |
| **Radarr** | A movie shopping list that fills itself. | `:7878` |
| **Sonarr** | The same, for TV shows; grabs new episodes as they air. | `:8989` |
| **Prowlarr** | The phone book of torrent sites. Radarr and Sonarr ask it where to look. | `:9696` |
| **qBittorrent** | The downloader. | `:8080` |
| **FlareSolverr** | Helps Prowlarr get past "are you human?" checks on some sites. | `:8191` (no page) |

Upgrades:

| App | What it does | Port | Turn on with |
|---|---|---|---|
| **Seerr** | A simple "request a movie/show" site for family and friends | `:5055` | `requests` |
| **Tautulli** | Who's watching what, history, stats | `:8181` | `requests` |
| **Recyclarr** | Copies expert quality rules (TRaSH guides) into Radarr/Sonarr | none | `quality` |
| **Kometa** | Resolution badges on posters, "IMDb Top 250"-style collections | none | `kometa` |
| **Tunarr** | Makes 24/7 "TV channels" out of your library, shown in Plex's Live TV | `:8008` | `tunarr` |
| **Homepage** | One dashboard with every app and its status | `:3080` | `dashboard` |
| **AdGuard + Caddy** | Lets you type `radarr.lan` instead of `192.168.1.50:7878` | `:3053`, `:80` | `dns` |
| **cross-seed** | Finds the same torrent on your other private trackers to seed more | `:2468` | `trackers` |
| **qbit_manage** | Deletes old torrents, but only after they've left the library and seeded 2 weeks | none | `trackers` |

"Port" is the number after the server's address. If the server is `192.168.1.50`,
Radarr is at `http://192.168.1.50:7878`.

## What happens when you add a movie

```
You (or a friend in Seerr) pick a movie
        │
        ▼
Radarr ──asks──▶ Prowlarr ──searches──▶ torrent sites
        │
        ▼
qBittorrent downloads it to   /data/drive1/torrents/movies/
        │
        ▼
Radarr "imports" it to        /data/drive1/media/movies/Movie (Year)/
   as a HARDLINK (same file, two names, no extra space)
        │
        ▼
Radarr tells Plex ──▶ it shows up on your TV
        │
        ▼
qBittorrent keeps sharing (seeding) the original
```

## The folder layout (don't change this)

On the server, the big drive is mounted at `/mnt/data` (the `DATA_DIR` setting).
Inside every app it's called `/data/drive1`:

```
/mnt/data                    = /data/drive1 inside the apps
├── torrents/                downloads; qBittorrent's world
│   ├── movies/
│   ├── tv/
│   └── cross-seed-links/
├── media/                   the library; Plex's world
│   ├── movies/
│   └── tv/
└── recycle/                 Radarr/Sonarr's 7-day recycle bin
```

**Why it matters: hardlinks.** A hardlink is one file that appears in two folders. The
movie in `torrents/` (which keeps seeding) and the movie in `media/` (which Plex shows)
are the *same bytes on disk*, so it takes the space only once. That only works when both
folders are on the same drive and every app uses the same paths. That's why everything
here mounts the whole drive at the same place.

App settings (small, but precious) live in `appdata/` inside this folder, on the SSD.

## How upgrades are switched on

All settings are in one file, `.env`. One line lists the upgrades that are on:

```
COMPOSE_PROFILES=requests,quality
```

Add a word, run `docker compose up -d`, and that upgrade starts. Remove it and run
`docker compose up -d --remove-orphans` to stop it. Its settings are kept.

## Words you'll run into

- **Terminal**: the text window where you type commands.
- **Docker / container**: Docker runs each app in its own sealed box (a container), so
  apps can't mess up the computer or each other, and updating is one command.
- **Docker Compose / `compose.yaml`**: the list of all the containers and how they connect.
- **IP address**: a device's number on your home network, like `192.168.1.50`.
- **API key**: a password one app uses to talk to another. The apps make these themselves.
- **Indexer / tracker**: a torrent site. *Public* ones are open to all; *private* ones
  need an invite and expect you to keep sharing (seeding).
- **Seeding**: sharing a finished download back to others.
- **Hardlink**: see above. One file, two names, no extra space.

## How Will's own server differs

So you're not confused if Will describes his: it has two data drives (`/data/drive1` and
`/data/drive2`; see docs/07 for adding a second drive), uses ZFS instead of ext4, an
NVIDIA card for transcoding, NordVPN on the host, and a few extra apps (Lidarr, Readarr,
Audiobookshelf, Deluge) that aren't part of this guide. The core design is the same.
