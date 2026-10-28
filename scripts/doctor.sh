#!/bin/bash
# Health check. Run it any time something seems off, and at the end of every stage:
#   ./scripts/doctor.sh
# It only reads and tests; the one thing it writes is a tiny test file it deletes again.
cd "$(dirname "$0")/.." || exit 1

ok=0; bad=0; warn=0
pass() { echo "  ✔ $*"; ok=$((ok+1)); }
fail() { echo "  ✘ $*"; bad=$((bad+1)); }
note() { echo "  ! $*"; warn=$((warn+1)); }
envv() { sed -n "s/^$1=//p" .env | tail -n 1 | sed -e 's/^["'\'']//' -e 's/["'\'']$//'; }

echo "Docker"
if ! command -v docker >/dev/null; then
  fail "docker is not installed (docs/01)"; exit 1
fi
if docker ps >/dev/null 2>&1; then pass "docker runs without sudo"
else fail "docker needs sudo or isn't running. Run: sudo usermod -aG docker \$USER  then log out and back in"; exit 1; fi
docker compose version >/dev/null 2>&1 && pass "docker compose installed" || fail "docker compose plugin missing (docs/01)"

echo ".env"
[ -f .env ] || { fail "no .env. Run: cp .env.example .env"; exit 1; }
for k in PUID PGID TZ SERVER_IP APPDATA_DIR DATA_DIR TORRENT_PORT; do
  [ -n "$(envv $k)" ] || fail "$k is empty in .env"
done
[ "$(envv PUID)" = "$(id -u)" ] && [ "$(envv PGID)" = "$(id -g)" ] && pass "PUID/PGID match your user" \
  || note "PUID/PGID in .env ($(envv PUID)/$(envv PGID)) differ from yours ($(id -u)/$(id -g))"
if docker compose config -q 2>/tmp/doctor-compose.err; then pass "compose.yaml + .env are valid"
else fail "compose config error: $(head -n 3 /tmp/doctor-compose.err)"; fi
SERVER_IP=$(envv SERVER_IP)
hostname -I | tr ' ' '\n' | grep -qx "$SERVER_IP" && pass "SERVER_IP $SERVER_IP belongs to this machine" \
  || fail "SERVER_IP $SERVER_IP is not this machine's address (it has: $(hostname -I))"
PROFILES=",$(envv COMPOSE_PROFILES),"
echo "  upgrades switched on: ${PROFILES//,/ }"

echo "Data drive"
DATA_DIR=$(envv DATA_DIR)
if [ -d "$DATA_DIR" ]; then
  mountpoint -q "$DATA_DIR" && pass "$DATA_DIR is a mounted drive" \
    || note "$DATA_DIR is NOT a separate mount; downloads would fill the system drive (docs/01)"
  df -h "$DATA_DIR" | awk 'NR==2 {print "  · " $4 " free of " $2 " (" $5 " used)"}'
  for d in torrents media; do [ -d "$DATA_DIR/$d" ] || fail "$DATA_DIR/$d missing. Run ./scripts/setup-folders.sh"; done
  if [ -d "$DATA_DIR/torrents" ] && [ -d "$DATA_DIR/media" ]; then
    t="$DATA_DIR/torrents/.doctor-$$"; m="$DATA_DIR/media/.doctor-$$"
    if echo test > "$t" 2>/dev/null && ln "$t" "$m" 2>/dev/null && [ "$(stat -c %i "$t")" = "$(stat -c %i "$m")" ]; then
      pass "hardlinks work between torrents/ and media/"
    else
      fail "hardlink test failed (not writable, or torrents/ and media/ are on different drives)"
    fi
    rm -f "$t" "$m"
  fi
else
  fail "DATA_DIR $DATA_DIR does not exist (docs/01)"
fi

echo "Containers"
for s in $(docker compose config --services 2>/dev/null); do
  state=$(docker inspect -f '{{.State.Status}}' "$s" 2>/dev/null || echo missing)
  case "$s:$state" in
    qbit_manage:exited|qbit_manage:created) pass "$s (runs from cron, exited is normal)";;
    *:running) pass "$s running";;
    *) fail "$s is $state. Try: docker compose up -d  then  docker logs $s --tail 50";;
  esac
done

echo "Web pages answer"
check() {  # name port path profile
  [ -z "$4" ] || [[ "$PROFILES" == *",$4,"* ]] || return 0
  code=$(curl -s -o /dev/null -m 5 -w '%{http_code}' "http://127.0.0.1:$2$3")
  [[ "$code" =~ ^(200|301|302|303|307|401)$ ]] && pass "$1  http://$SERVER_IP:$2" || fail "$1 not answering on port $2 (got $code)"
}
check Plex 32400 /identity ""
check Radarr 7878 /ping ""
check Sonarr 8989 /ping ""
check Prowlarr 9696 /ping ""
check qBittorrent 8080 / ""
check FlareSolverr 8191 / ""
check Seerr 5055 /api/v1/status requests
check Tautulli 8181 /status requests
check Tunarr 8008 / tunarr
check Homepage 3080 / dashboard
check AdGuard 3053 / dns
check Caddy 80 / dns
check cross-seed 2468 /api/ping trackers

echo "Keys in .env"
need() { [[ "$PROFILES" == *",$1,"* ]] || return 0; shift; for k; do [ -n "$(envv $k)" ] || fail "$k is empty in .env (API keys: ./scripts/collect-keys.py; others: see the upgrade's doc)"; done; }
need quality RADARR_API_KEY SONARR_API_KEY
need kometa PLEX_TOKEN TMDB_API_KEY
need dashboard RADARR_API_KEY SONARR_API_KEY PROWLARR_API_KEY
need trackers PROWLARR_API_KEY RADARR_API_KEY SONARR_API_KEY QBIT_PASS CROSS_SEED_INDEXER_IDS
if [[ "$PROFILES" == *",trackers,"* ]]; then
  crontab -l 2>/dev/null | grep -q 'qbit_manage/run.sh' && pass "qbit_manage cron is installed" \
    || note "qbit_manage cron not installed yet (docs/06)"
fi

echo
echo "Result: $ok ok, $warn warnings, $bad problems"
[ "$bad" -eq 0 ]
