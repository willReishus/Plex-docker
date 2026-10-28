# Looking after it

## Updates (once a month or so)

```bash
cd ~/media-server
git pull                                   # newest version of this guide
docker compose pull && docker compose up -d
docker image prune -f                      # deletes the old app versions
sudo apt update && sudo apt full-upgrade -y
```

If `git pull` complains about local changes, ask your AI. You shouldn't normally edit
tracked files; your own settings live in `.env`, `appdata/` and `my-setup.md`, which git ignores.

After a Linux update that says a restart is needed: `sudo reboot`. Every app starts back up by itself.

## Backups

The library is replaceable. The **settings** are what's painful to lose: `appdata/` and `.env`.

```bash
cd ~/media-server
docker compose stop
sudo tar czf /mnt/data/backup-appdata-$(date +%F).tgz --exclude='appdata/plex/config/Library/Application Support/Plex Media Server/Cache' appdata .env
docker compose start
```

Copy that `.tgz` off the server too (USB stick, cloud). Radarr, Sonarr and Prowlarr also
make their own weekly backups (System → Backup).

## Check the drive's health

```bash
sudo apt install -y smartmontools
sudo smartctl -H /dev/sdX          # the big drive; should say PASSED
df -h /mnt/data                    # free space; keep at least ~10% free
```

## Hardware transcoding

Lets Plex convert video for weak devices (or remote streams) using the graphics chip
instead of straining the CPU. **Needs Plex Pass.**

- **Intel graphics**: `ls /dev/dri` shows `renderD128`. In `.env`:
  `COMPOSE_FILE=compose.yaml:extras/gpu-intel.yaml`, then `docker compose up -d`.
- **NVIDIA card**: install the driver (`sudo ubuntu-drivers install`, reboot,
  `nvidia-smi` should work), then the NVIDIA Container Toolkit following
  <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html>
  (the AI can walk through it), and run `sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`.
  In `.env`: `COMPOSE_FILE=compose.yaml:extras/gpu-nvidia.yaml`, then `docker compose up -d`.

Then Plex → Settings → Transcoder → tick "Use hardware acceleration when available".
Check it works: play something, change quality to something low, and the Plex dashboard
shows **(hw)** next to the stream.

## Adding a second drive

1. Mount it like stage 1, step 8, but at `/mnt/data2` (new UUID, new fstab line).
2. In `.env`: `DATA2_DIR=/mnt/data2` and append `:extras/second-drive.yaml` to `COMPOSE_FILE`.
3. Make its folders:
   ```bash
   mkdir -p /mnt/data2/{torrents/{movies,tv,cross-seed-links},media/{movies,tv},recycle}
   docker compose up -d
   ```
4. Inside the apps it's `/data/drive2`. Add `/data/drive2/media/movies` as a second folder of
   the Plex Movies library and as a root folder in Radarr; same for TV.

**The catch:** hardlinks only work *within* a drive. qBittorrent downloads to drive 1, so a
movie imported into a drive-2 root folder becomes a full **copy** (double space). Two ways
to live with it:

- **Switch over when drive 1 is full** (simplest): point qBittorrent's `radarr`/`tv-sonarr`
  category paths at `/data/drive2/torrents/...` *and* make drive 2 the root folder for new
  movies/shows, all at the same time.
- Or accept the copies for items you put on drive 2. `keep_copies.py` (docs/06) makes sure
  qbit_manage doesn't mistake them for deleted.

If you use cross-seed, add the drive-2 folders to `linkDirs` and `dataDirs` in
`appdata/cross-seed/config.js`.

## VPN

Optional. Some people send their downloads through a VPN for privacy. Will's way: the
NordVPN app on the whole server, with Plex's ports left outside the VPN so remote
streaming still works:

```bash
nordvpn login
nordvpn set lan-discovery on        # keep the home network reachable
nordvpn allowlist add port 32400    # Plex remote access
nordvpn set autoconnect on
nordvpn connect
```

(Install the app from <https://nordvpn.com/download/linux/> first.) Other VPNs work
similarly. The important parts are *keep LAN access* and *allow port 32400*. After
connecting, check that Plex → Settings → Remote Access is still green and that
`http://SERVER_IP:7878` still opens from another device.

With a VPN, forwarding `TORRENT_PORT` on your router does nothing. Port forwarding then
depends on the VPN provider.

## Moving or rebuilding the server

Everything that makes your setup *yours* is `.env`, `appdata/`, `my-setup.md`, and the
data drive. On a new machine: stage 1, clone this repo, put those back, `docker compose up -d`.
