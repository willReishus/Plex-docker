# Plex-docker: a home media server you build with an AI helper

This is the recipe for the media server Will runs at home, written so that someone who
isn't "a computer person" can build the same thing with an AI assistant walking them
through it.

When it's done you get:

- **Plex**: your own Netflix. Watch your movies and shows on the TV, phone, or laptop,
  at home or away.
- **Radarr** (movies) and **Sonarr** (TV): you pick a movie or show, and they find it,
  download it, rename it, and put it in Plex. New episodes arrive by themselves.
- **Prowlarr** and **qBittorrent**: the search and download engines behind them.
- Optional upgrades, added later when you're ready: a request page for family and friends,
  watch stats, better-quality rules, nicer posters, live-TV-style channels, a dashboard,
  easy addresses like `http://radarr.lan`, and extras for private trackers.

## What you need

- **A spare computer** that can stay on all the time. Something from the last ~8 years is
  plenty. An Intel CPU with built-in graphics (7th gen or newer) is ideal, because it
  converts video for weaker devices with very little effort.
- **A small SSD** (120 GB or more) for the system, and **one big hard drive** (8 TB or more)
  for movies and shows.
- **A wired (Ethernet) connection** to your router.
- A USB stick (8 GB+) to install Linux from.
- A free [Plex account](https://www.plex.tv). Plex Pass (paid) is optional; it unlocks
  hardware video conversion.
- About **2–4 hours** for the first part, split over as many sittings as you like.

You don't need to know Linux. The AI does the hard parts.

## How to start

### Before Linux is installed (use any device)

Open [Claude](https://claude.ai) (or another AI assistant that can read web pages) on your
phone or laptop, and paste this:

> I want to build a home media server using this guide:
> https://github.com/willReishus/Plex-docker
> Please read AGENTS.md and README.md in that repository first, then walk me through
> it one step at a time. I'm not very technical.

It'll help you pick hardware and install Ubuntu Linux on the spare computer
([docs/01](docs/01-prepare-the-computer.md)).

### Once Linux is installed (recommended)

Install [Claude Code](https://claude.com/claude-code) on the server itself (docs/01 shows
how). Then it can run the commands for you instead of you typing them. Open a terminal
on the server and run:

```bash
cd ~/media-server && claude
```

Then say: *"Help me set up my media server. Start by reading AGENTS.md."*

The AI keeps notes in `my-setup.md` on the server, so you can stop at any time and pick
up later, even in a new chat.

## The stages

| | What you get | Guide |
|---|---|---|
| **1** | Linux, Docker, and your big drive ready | [Prepare the computer](docs/01-prepare-the-computer.md) |
| **2** | Plex + automatic movie & TV downloads, working end to end | [The core](docs/02-core.md) |
| ⬆ | Request page for friends and family, plus "who watched what" | [Requests & stats](docs/03-requests-and-stats.md) |
| ⬆ | Better quality picks, poster overlays & collections, 24/7 channels | [Quality & polish](docs/04-quality-and-polish.md) |
| ⬆ | One dashboard page, and names like `http://plex.lan` | [Dashboard & names](docs/05-dashboard-and-names.md) |
| ⬆ | Cross-seeding, and automatic cleanup that respects seeding rules | [Private trackers](docs/06-private-trackers.md) |
| 🔧 | Updates, backups, adding a drive, hardware transcoding, VPN | [Maintenance](docs/07-maintenance.md) |

Do stages 1 and 2 first. Use the server for a few days. Then add upgrades (⬆) one at a
time, in any order, whenever you feel like it. Each one is switched on with a single word
in the settings file.

Something not working? See [troubleshooting](docs/troubleshooting.md), or ask your AI to
run `./scripts/doctor.sh`.

## What's in this repository

```
AGENTS.md          instructions for the AI helper (read this, AI!)
compose.yaml       every app and how it's wired together
.env.example       your settings file template (copied to .env, which stays private)
docs/              the step-by-step guides above
templates/         ready-made settings for the upgrade apps
scripts/           helpers: folder setup, health check, key collector, cleanup safety net
extras/            add-ons: graphics-card transcoding, a second drive
```

## A word on responsibility

These apps download whatever you point them at. You're responsible for what you download,
for following the law where you live, and for following the rules of any site you join.
