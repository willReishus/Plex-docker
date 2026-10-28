"""Tiny .env reader/writer shared by the scripts. Run from anywhere; paths resolve to the repo root."""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(ROOT, ".env")


def load():
    if not os.path.exists(ENV_FILE):
        raise SystemExit("No .env yet. Run:  cp .env.example .env   then fill it in (docs/02).")
    env = {}
    for line in open(ENV_FILE):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("'\"")
    return env


def path(value):
    """APPDATA_DIR may be relative (./appdata); compose resolves it from the repo root, so do we."""
    return os.path.normpath(os.path.join(ROOT, value))


def set_value(key, value):
    text = open(ENV_FILE).read()
    line = f"{key}={value}"
    if re.search(rf"^{re.escape(key)}=.*$", text, flags=re.M):
        text = re.sub(rf"^{re.escape(key)}=.*$", lambda _: line, text, count=1, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n" + line + "\n"
    open(ENV_FILE, "w").write(text)
