#!/usr/bin/env python3
"""Copy each app's API key into .env, so the upgrades can talk to the apps.

Only fills keys that are still empty in .env; never overwrites. Prints which
keys it found, never the keys themselves. Safe to run again any time.
"""
import json, os, re
import _env

env = _env.load()
appdata = _env.path(env.get("APPDATA_DIR", "./appdata"))


def xml_key(app):
    p = os.path.join(appdata, app, "config.xml")
    m = re.search(r"<ApiKey>([^<]+)</ApiKey>", open(p).read()) if os.path.exists(p) else None
    return m and m.group(1)


def tautulli_key():
    p = os.path.join(appdata, "tautulli", "config.ini")
    m = re.search(r"^api_key\s*=\s*(\S+)", open(p).read(), flags=re.M) if os.path.exists(p) else None
    return m and m.group(1)


def seerr_key():
    p = os.path.join(appdata, "seerr", "settings.json")
    return os.path.exists(p) and json.load(open(p)).get("main", {}).get("apiKey")


def plex_token():
    p = os.path.join(appdata, "plex", "config", "Library", "Application Support",
                     "Plex Media Server", "Preferences.xml")
    m = re.search(r'PlexOnlineToken="([^"]+)"', open(p).read()) if os.path.exists(p) else None
    return m and m.group(1)


finders = {
    "RADARR_API_KEY": lambda: xml_key("radarr"),
    "SONARR_API_KEY": lambda: xml_key("sonarr"),
    "PROWLARR_API_KEY": lambda: xml_key("prowlarr"),
    "TAUTULLI_API_KEY": tautulli_key,
    "SEERR_API_KEY": seerr_key,
    "PLEX_TOKEN": plex_token,
}
for key, find in finders.items():
    if env.get(key):
        print(f"  already set   {key}")
        continue
    try:
        value = find()
    except OSError as e:
        value = None
        print(f"  can't read    {key}: {e}")
    if value:
        _env.set_value(key, value)
        print(f"  filled in     {key}")
    else:
        print(f"  not found     {key} (app not set up yet?)")
print("Done. Run  docker compose up -d  so running apps pick up new keys.")
