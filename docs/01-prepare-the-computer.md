# Stage 1: Prepare the computer

**Goal:** Ubuntu Linux installed, a fixed network address, Docker installed, and the big
drive mounted at `/mnt/data`. About 1–2 hours.

> **AI:** most of this happens before you can run commands on the server. Coach the
> person through the install screens. From step 3 on, they type into the server's
> Terminal app. After step 6 you may be running on the server yourself.

## 1. Check the hardware

- Spare PC with an SSD for the system and a big hard drive (HDD) for media.
- Connected to the router with an Ethernet cable (Wi-Fi works, but streaming and downloads suffer).
- Note the CPU (Intel with built-in graphics? an NVIDIA card?). It decides hardware
  transcoding later (docs/07). Write it in `my-setup.md` once that exists.

## 2. Install Ubuntu Desktop

1. On another computer, download **Ubuntu Desktop LTS** (the newest "LTS" version) from
   <https://ubuntu.com/download/desktop>.
2. Write it to a USB stick with **balenaEtcher** (<https://etcher.balena.io>), on
   Windows or Mac.
3. **Unplug the big media drive** (power or data cable) from the spare PC before
   installing. Then the installer can't wipe it by accident. Plug it back in after.
4. Boot the spare PC from the USB stick. You usually press F12, F11, F2 or Esc right as
   it powers on; the screen often says which key.
5. Choose **Install Ubuntu** → **Erase disk and install Ubuntu** on the **SSD**.
6. Create a user. Pick a short lowercase username and a password you'll remember.
   Turn on **"Log in automatically"** so the server recovers by itself after a power cut.
7. When it's done, remove the USB stick and restart. Power off, plug the media drive back
   in, and power on.

## 3. First updates and basic tools

Open **Terminal** (press the Windows/Super key, type `terminal`). Run:

```bash
sudo apt update && sudo apt full-upgrade -y && sudo apt install -y curl git openssh-server nano dnsutils
```

It asks for your password. Nothing shows while you type it; that's normal.

`openssh-server` lets you manage the server later from another computer
(`ssh username@SERVER_IP`), so it can live without a screen.

## 4. Stop it from sleeping

A server that goes to sleep stops serving. Run:

```bash
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

Also open **Settings → Power** and set **Automatic Suspend** to **Off**, and Screen Blank
to whatever you like.

Optional: in the PC's BIOS, set "Restore on AC power loss" to **Power On**, so it starts
by itself after a power cut.

## 5. Give it a fixed address

The other apps and devices find the server by its IP address, so the address must never change.

1. Find the current address and the network card's hardware (MAC) address:
   ```bash
   ip -4 -br addr show; ip -br link
   ```
   Look for the line that starts with `e` (like `enp3s0` or `eno1`). It shows something
   like `192.168.1.50/24`. The MAC looks like `a1:b2:c3:d4:e5:f6`.
2. Log into the router (often `http://192.168.1.1` or `http://192.168.0.1`; the
   address and password are usually on a sticker on the router).
3. Find **DHCP reservation** (also called "Address Reservation", "Static Lease", or
   "Fixed IP"), and reserve the current IP for that MAC address.

> **AI:** ask for the router brand and model and look up where that setting is.
> Record the IP and router model in `my-setup.md`. This IP is `SERVER_IP` from here on.

Restart the server (`sudo reboot`) and confirm the address stayed the same.

## 6. Get this guide onto the server (and, recommended, Claude Code)

```bash
git clone https://github.com/willReishus/Plex-docker.git ~/media-server
```

**Recommended:** install Claude Code, so the AI can run commands for you:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Close the terminal, open a new one, then:

```bash
cd ~/media-server && claude
```

Sign in when it asks. Tell it: *"Continue setting up my media server from
docs/01-prepare-the-computer.md step 7. Read AGENTS.md first."*

## 7. Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

**Log out and back in** (or `sudo reboot`) so the second line takes effect. Then check:

```bash
docker run --rm hello-world
```

It should print "Hello from Docker!" with no `sudo` needed.

## 8. Prepare the big drive

### 8a. Find it

```bash
lsblk -o NAME,SIZE,MODEL,FSTYPE,MOUNTPOINTS
```

The big drive is the one with the large size (e.g. `12.7T`). Note its name, like `sdb`.
The SSD with Ubuntu on it has mount points like `/` and `/boot/efi`; never touch that one.

> **AI:** stop here. Confirm the device with the person by size and model. Ask: is this
> drive brand new or empty, or does it hold files they want to keep?
> - **New or empty** → 8b.
> - **Has files to keep** → don't format. Find out what's on it and its filesystem
>   (`FSTYPE`). An NTFS drive from Windows can be mounted as it is, but permissions and
>   hardlinks are unreliable. The best plan is to copy the files elsewhere, format as ext4,
>   and copy them back into `media/movies` and `media/tv`. Work this out together.

### 8b. Format it (ERASES THE DRIVE)

Replace `sdX` with the real name **twice**. Read it back before pressing Enter.

```bash
sudo parted /dev/sdX --script mklabel gpt mkpart media ext4 0% 100%
sudo mkfs.ext4 -L media /dev/sdX1
```

### 8c. Mount it at /mnt/data, every boot

```bash
sudo mkdir -p /mnt/data
sudo blkid /dev/sdX1
```

Copy the `UUID="..."` value. Then add the drive to `/etc/fstab` (put the UUID in place of
`PASTE-UUID`):

```bash
sudo cp /etc/fstab /etc/fstab.bak
echo 'UUID=PASTE-UUID  /mnt/data  ext4  defaults,nofail  0  2' | sudo tee -a /etc/fstab
sudo systemctl daemon-reload && sudo mount -a
sudo chown -R $USER:$USER /mnt/data
df -h /mnt/data
```

`df` should show the big size mounted on `/mnt/data`. `nofail` means the server still
boots if the drive is ever unplugged.

Reboot once (`sudo reboot`) and check `df -h /mnt/data` again.

## Done when

- [ ] `docker run --rm hello-world` works without `sudo`
- [ ] The server keeps the same IP after a reboot (reserved in the router)
- [ ] `df -h /mnt/data` shows the big drive after a reboot
- [ ] Automatic suspend is off
- [ ] This repo is at `~/media-server`
- [ ] `my-setup.md` records the IP, router, drive, CPU/GPU

Next: [Stage 2, the core](02-core.md).
