#!/usr/bin/env python3
"""Copy a ready-made config from templates/ into appdata/, filling in ${VALUES} from .env.

Usage:  scripts/install-config.py <app> [--force]
Apps:   caddy, homepage, recyclarr, kometa, cross-seed, qbit_manage

It never overwrites a config that already exists unless you add --force
(the old file is kept as <name>.bak).
"""
import os, shutil, string, sys
import _env

TARGETS = {   # template folder -> where the files go inside APPDATA_DIR
    "caddy": "caddy/etc",
    "homepage": "homepage",
    "recyclarr": "recyclarr/configs",
    "kometa": "kometa",
    "cross-seed": "cross-seed",
    "qbit_manage": "qbit_manage",
}

args = [a for a in sys.argv[1:] if not a.startswith("--")]
force = "--force" in sys.argv
if len(args) != 1 or args[0] not in TARGETS:
    raise SystemExit(__doc__)
app = args[0]
env = _env.load()
src = os.path.join(_env.ROOT, "templates", app)
dst = os.path.join(_env.path(env.get("APPDATA_DIR", "./appdata")), TARGETS[app])
os.makedirs(dst, exist_ok=True)

for name in sorted(os.listdir(src)):
    out = os.path.join(dst, name)
    if os.path.exists(out) and not force:
        print(f"  kept existing {out}  (use --force to replace it)")
        continue
    if os.path.exists(out):
        shutil.copy2(out, out + ".bak")
    text = string.Template(open(os.path.join(src, name)).read()).safe_substitute(env)
    open(out, "w").write(text)
    print(f"  wrote         {out}")
