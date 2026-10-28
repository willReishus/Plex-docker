#!/bin/sh
# Creates the folder layout on the data drive and the appdata folders.
# Safe to run again; it only creates what is missing and never deletes anything.
set -e
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "No .env yet. Run: cp .env.example .env  and fill it in (docs/02)."; exit 1; }
envv() { sed -n "s/^$1=//p" .env | tail -n 1 | sed -e 's/^["'\'']//' -e 's/["'\'']$//'; }

DATA_DIR=$(envv DATA_DIR)
APPDATA_DIR=$(envv APPDATA_DIR)
[ -d "$DATA_DIR" ] || { echo "DATA_DIR ($DATA_DIR) does not exist. Mount the drive first (docs/01)."; exit 1; }
[ -w "$DATA_DIR" ] || { echo "Can't write to $DATA_DIR. Fix ownership: sudo chown -R $(id -u):$(id -g) $DATA_DIR"; exit 1; }

for d in torrents/movies torrents/tv torrents/cross-seed-links media/movies media/tv recycle; do
  mkdir -p "$DATA_DIR/$d"
done
for d in plex/config plex/transcode radarr sonarr prowlarr qbittorrent seerr tautulli recyclarr/configs \
         kometa tunarr homepage adguard/work adguard/conf caddy/etc caddy/data caddy/config \
         cross-seed qbit_manage/logs; do
  mkdir -p "$APPDATA_DIR/$d"
done
echo "Folders ready:"
echo "  downloads  $DATA_DIR/torrents/{movies,tv}"
echo "  library    $DATA_DIR/media/{movies,tv}"
echo "  settings   $APPDATA_DIR/"
