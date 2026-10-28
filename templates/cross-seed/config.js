// cross-seed settings (docs/06). Keys and passwords come from .env through compose.yaml,
// so this file holds no secrets. After editing:  docker compose restart cross-seed
const env = process.env;
const prowlarr = (id) => `http://prowlarr:9696/${id}/api?apikey=${env.PROWLARR_API_KEY}`;

module.exports = {
  // Which Prowlarr indexers to search: CROSS_SEED_INDEXER_IDS in .env, e.g. 3,5,8
  torznab: (env.CROSS_SEED_INDEXER_IDS || "").split(",").map((s) => s.trim()).filter(Boolean).map(prowlarr),
  sonarr: [`http://sonarr:8989/?apikey=${env.SONARR_API_KEY}`],
  radarr: [`http://radarr:7878/?apikey=${env.RADARR_API_KEY}`],
  torrentClients: [
    `qbittorrent:http://${encodeURIComponent(env.QBIT_USER)}:${encodeURIComponent(env.QBIT_PASS)}@qbittorrent:8080`,
  ],

  // Hardlinks, never symlinks: with symlinks, deleting the original torrent breaks every cross-seed of it.
  linkType: "hardlink",
  linkDirs: ["/data/drive1/torrents/cross-seed-links"],
  dataDirs: ["/data/drive1/torrents/movies", "/data/drive1/torrents/tv"],

  action: "inject",
  matchMode: "partial",
  fuzzySizeThreshold: 0.1,
  autoResumeMaxDownload: 52428800,   // a partial match may download at most 50 MB of missing pieces
  ignoreNonRelevantFilesToResume: true,
  maxDataDepth: 3,
  seasonFromEpisodes: 0.5,
  excludeOlder: "15 days",           // the validator requires this to be >= 5x excludeRecentSearch
  excludeRecentSearch: "3 days",
  rssCadence: "30 minutes",
  searchCadence: "1 day",
};
