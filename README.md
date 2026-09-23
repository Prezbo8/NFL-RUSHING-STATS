# NFL Rushing Stats

Scrapes NFL team rushing stats — volume, advanced efficiency, and tempo — from
FTN and stores a dated snapshot per team per side in Supabase.

## What it collects

One row per `(season, scrape date, side, team)`, 44 columns.

**Volume** (statshub API)
`games · attempts · rushing_yards · ypc · rushing_tds · first_downs · fumbles · fumbles_lost · long_run · rushing_snaps`

**Advanced** (Stats iQ `rushing-analytics` / `rush-analytics`)
`epa_att · succ_pct · dvoa · aryoe · exp_pct · stf_pct · aybco · ayaco · crt_pct`

**Overview** (Stats iQ `overview`)
`yd_ply · pt_gm · fd_pct · turnovers · dpbk_pct · pass_yd · pass_td · interceptions · rush_pct · rush_yd · rush_td`

**Tempo** (Stats iQ `tempo`, offense only)
`ply_gm · top · drv_gm · sec_ply · ply_drv · yd_drv · sec_drv · three_and_out_pct · scd_pct`

## Sources

Two endpoints, neither requiring authentication.

**1. statshub** — volume stats. The page at `ftnfantasy.com/nfl/stats` has no
stable per-view URL and renders client-side, so this hits the API it calls:

```
POST https://6u5we6fbxi.execute-api.us-east-1.amazonaws.com/Statshub/statshub/rushing/{team|defense}
Authorization: Bearer undefined      # literal; omitting the header returns 401
```

`team` is rushing offense, `defense` is rushing defense.

**2. Stats iQ CSV export** — everything else:

```
GET https://stats.ftnfantasy.com/api/v1/stats/categories/{category}/tables/{table}/export.csv?season=2026&seasonType=REG
```

The Stats iQ *web UI* gates these tables behind an account — logged out, only 3
of 32 teams render. The CSV export endpoint does not, and returns all 32.

Both endpoints require a real browser `User-Agent` or return 403.

## Gotchas worth knowing

**`aybco + ayaco` does NOT equal `ypc`.** The two sources count different
attempt universes — they diverge by ~0.9 yds/att on average, in both directions.
`ypc` is always computed from statshub `attempts`/`rushing_yards`, never derived
from the contact splits.

**FTN's displayed YPC is rounded to 1 decimal** (up to 0.05 of error), so it is
recomputed from attempts and yards.

**`crt_pct` is algebraically redundant** — it is `ayaco / (aybco + ayaco)`.
Stored for display; it carries no information not already in the two splits.

**No defensive tempo table exists.** `ply_gm` for defense rows is derived as
`(pass_yd + rush_yd) / yd_ply / games` and flagged with `ply_gm_derived = true`.
Validated against the published offense tempo table (KC 72.2 derived vs 72.5
published; the gap is `yd_ply` being rounded to 1dp).

**`aryoe` is empty this early in the season** — FTN has not populated rush yards
over expected yet. Expect it to fill in around Week 4-5.

**Rebuild the view after adding columns.** A `select *` view freezes its column
list at creation; new columns are invisible until `rebuild_view.py` is run.

## Integrity check

Every rushing attempt is one team's carry and another team's carry allowed, so
league totals must reconcile exactly. Asserted on every run — the scraper raises
rather than writing mismatched data.

## Credentials

macOS Keychain, or `SUPABASE_URL` / `SUPABASE_KEY` env vars:

```bash
security add-generic-password -s nfl-rushing-supabase-url -a "$USER" -w 'https://....supabase.co'
security add-generic-password -s nfl-rushing-supabase-key -a "$USER" -w 'eyJ...'
```

`rebuild_view.py` additionally needs the Supabase CLI token (`supabase login`).

## Schedule

`~/Library/LaunchAgents/com.daniell.nfl.rushing.plist` — Tue, Wed, Sun at 17:00.
Logs to `~/logs/nfl_rushing.log`.

```bash
launchctl list | grep nfl.rushing
launchctl start com.daniell.nfl.rushing
```

## Usage

```bash
python3 scrape_ftn_rushing.py --dry-run          # fetch + verify, no write
python3 scrape_ftn_rushing.py                    # fetch + write
python3 rebuild_view.py                          # after adding columns
```

## Live dashboard

`index.html` is served from GitHub Pages and reads Supabase directly, so it is always current
rather than a snapshot — compare any two teams' rushing offense against the other's rushing
defense, plus a sortable rankings table for all 32.

It uses the project's **anon** key, which is read-only: row-level security grants `select` only,
and insert/update/delete are revoked from the `anon` role outright. The scraper writes with the
service-role key from Keychain, which bypasses RLS and never appears in this repo.

The sample-size callout is computed from the loaded data, not hardcoded, and hides itself once
teams reach 8 games.

## Storage

Supabase project `mlb-2026-stats`, table `nfl_rushing_team_stats`, view
`nfl_rushing_latest` (most recent snapshot per team/side). Primary key
`(season, scraped_on, side, team)` — each run adds a dated snapshot rather than
overwriting, so history accumulates for backtesting.
