# NFL Rushing Stats

Scrapes NFL team rushing stats (offense and defense) from FTN's statshub API
and stores a dated snapshot in Supabase.

## What it collects

Per team, per side (offense / defense), per scrape date:

`games · attempts · rushing_yards · ypc · rushing_tds · first_downs · fumbles · fumbles_lost · long_run · rushing_snaps`

`ypc` is computed as `rushing_yards / attempts` rather than taken from FTN's
displayed column, which is rounded to one decimal (up to 0.05 of error).

**Not included:** DVOA, SUC%, YBCO/YACO, STF%, EXP%, EPA/ATT, WINPA. Those are
behind FTN's account wall — logged out, only 3 of 32 teams render. Adding them
requires an authenticated session.

## Source

The page at `ftnfantasy.com/nfl/stats` has no stable URL per view and renders
client-side, so this hits the API the page itself calls:

```
POST https://6u5we6fbxi.execute-api.us-east-1.amazonaws.com/Statshub/statshub/rushing/{team|defense}
Authorization: Bearer undefined      # literal, what the page sends when logged out
```

`team` is rushing offense, `defense` is rushing defense.

## Integrity check

Every rushing attempt is one team's carry and another team's carry allowed, so
league totals must reconcile exactly. The scraper asserts this on every run and
fails loudly rather than writing mismatched data.

## Credentials

Read from macOS Keychain (or `SUPABASE_URL` / `SUPABASE_KEY` env vars):

```bash
security add-generic-password -s nfl-rushing-supabase-url -a "$USER" -w 'https://...supabase.co'
security add-generic-password -s nfl-rushing-supabase-key -a "$USER" -w 'eyJ...'
```

## Schedule

`~/Library/LaunchAgents/com.daniell.nfl.rushing.plist` — Tue, Wed, Sun at 17:00.
Logs to `~/logs/nfl_rushing.log`.

```bash
launchctl list | grep nfl.rushing          # check loaded
launchctl start com.daniell.nfl.rushing    # run now
```

## Usage

```bash
python3 scrape_ftn_rushing.py --dry-run    # fetch + verify, no write
python3 scrape_ftn_rushing.py              # fetch + write
FTN_SEASON=2025 python3 scrape_ftn_rushing.py   # a different season
```
