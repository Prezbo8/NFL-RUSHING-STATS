#!/usr/bin/env python3
"""Rebuild nfl_rushing_latest.

A `select *` view freezes its column list at creation, so it must be rebuilt
whenever columns are added to nfl_rushing_team_stats or the new columns are
invisible (and selecting them returns a 400).
"""
import subprocess, sys, requests

PROJECT = "mfliuasrygxkembqmrkr"
DDL = """drop view if exists nfl_rushing_latest;
create view nfl_rushing_latest as
select distinct on (season, side, team) *
from nfl_rushing_team_stats
order by season, side, team, scraped_on desc;"""

tok = subprocess.run(["security", "find-generic-password", "-s", "Supabase CLI", "-w"],
                     capture_output=True, text=True).stdout.strip()
if not tok:
    sys.exit("no Supabase CLI token in keychain (run: supabase login)")
r = requests.post(f"https://api.supabase.com/v1/projects/{PROJECT}/database/query",
                  headers={"Authorization": f"Bearer {tok}"}, json={"query": DDL}, timeout=90)
print("rebuild:", r.status_code, r.text[:200])
r.raise_for_status()
