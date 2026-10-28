# Upgrade: Dashboard and friendly names

Two parts:

- **A. Dashboard**: one page with a tile for every app, showing what's downloading, what's
  playing, and free space. Easy, about 15 minutes.
- **B. Friendly names**: type `plex.lan`, `radarr.lan`, `requests.lan` instead of
  `192.168.1.50:7878`, on every device in the house. About 45 minutes. **This changes the
  internet settings for your whole house**, so do it when a short hiccup won't upset anyone.

Part A works fine without part B.

---

## A. Dashboard (Homepage)

1. Fill in the keys:
   ```bash
   cd ~/media-server && ./scripts/collect-keys.py
   ```
2. Copy in the config:
   ```bash
   ./scripts/install-config.py homepage
   ```
3. Edit `appdata/homepage/services.yaml`: **delete the tiles for apps you haven't switched
   on** (e.g. Requests and Tautulli if you skipped that upgrade; AdGuard if you skip part B),
   and set the Router tile's address to your router's.
4. Add `dashboard` to `COMPOSE_PROFILES` in `.env`, then `docker compose up -d`.
5. Open `http://SERVER_IP:3080`. Bookmark it on your phone and computer.

Edits to the files in `appdata/homepage/` show up when you refresh the page.

---

## B. Friendly `.lan` names (AdGuard Home + Caddy)

How it works: the router tells every device to use the server as its DNS server (the thing
that turns names into addresses). AdGuard on the server answers "anything ending in `.lan`
is the server", and Caddy on the server sends each name to the right app.

### 1. Free up port 53 on Ubuntu

Ubuntu has a small built-in DNS helper on port 53 that would block AdGuard. Turn it off:

```bash
sudo mkdir -p /etc/systemd/resolved.conf.d
printf '[Resolve]\nDNSStubListener=no\n' | sudo tee /etc/systemd/resolved.conf.d/adguard.conf
sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
sudo systemctl restart systemd-resolved
```

Check that nothing is on ports 53, 80, 3000 or 3053 any more (no output = good):

```bash
sudo ss -lntup | grep -E ':(53|80|3000|3053) '
```

### 2. Start AdGuard and Caddy

```bash
cd ~/media-server && ./scripts/install-config.py caddy
```

Add `dns` to `COMPOSE_PROFILES`, then `docker compose up -d`.

### 3. AdGuard first-time setup

Open `http://SERVER_IP:3000` (only the first time):

- **Admin Web Interface**: All interfaces, port **3053** (port 80 belongs to Caddy)
- **DNS server**: All interfaces, port **53**
- Create an admin username and password. Save them in your password manager.

From now on AdGuard is at `http://SERVER_IP:3053`.

### 4. The `.lan` rule

AdGuard → **Filters → DNS rewrites → Add DNS rewrite**:
- Domain: `*.lan`
- Answer: your `SERVER_IP`

**Leave protection on** (top of the dashboard: "Protection is enabled"). If protection is
turned off, the `.lan` rewrite silently stops working. Ad-blocking lists are optional;
Will keeps them off. Turn on the default list under **Filters → DNS blocklists** if you
want ad-blocking for the house.

Test it from the server:

```bash
nslookup radarr.lan 127.0.0.1
```

It should answer with `SERVER_IP`.

### 5. Point the house at it (router)

In the router's **DHCP / LAN settings**, set **Primary DNS** to `SERVER_IP`.

> **AI:** explain the trade-off and let them choose.
> - **Leave Secondary DNS empty** (Will's choice): `.lan` names always work, but if the
>   server is off, websites stop loading in the house until it's back.
> - **Secondary DNS `1.1.1.1`**: the internet keeps working when the server is off, but
>   devices sometimes ask 1.1.1.1 first, and then `.lan` names fail on and off.
>
> Record the choice in `my-setup.md`.

Devices pick up the change when they reconnect to Wi-Fi (toggle Wi-Fi off and on, or wait a day).

### 6. Try it

On a phone or laptop at home: `http://home.lan` (dashboard), `http://plex.lan`,
`http://radarr.lan`, `http://requests.lan`, `http://qbit.lan`. The full list is in
`appdata/caddy/etc/Caddyfile`. Unknown names go to the dashboard.

Optional: change the `href:` addresses in `appdata/homepage/services.yaml` to the `.lan` names.

> **Note:** the server itself doesn't use `.lan` names (its own DNS still points elsewhere).
> That's fine. The apps talk to each other by container name or IP.

### Adding a name later

Copy a block in `appdata/caddy/etc/Caddyfile`, change the name and port, then:

```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## Done when

- [ ] (A) The dashboard loads and tiles show numbers, not errors
- [ ] (B) `http://radarr.lan` opens Radarr from a phone on home Wi-Fi
- [ ] (B) Normal websites still load on every device
- [ ] `./scripts/doctor.sh` shows no ✘
