"""Stats iQ table exports from stats.ftnfantasy.com.

The web UI gates these tables behind an account (only 3 of 32 teams render),
but the CSV export endpoint the app uses returns every team with no auth.
"""
import csv
import io

import requests

BFF = "https://stats.ftnfantasy.com/api/v1/stats/categories"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

# category, table slug, which side of the ball it describes
TABLES = {
    "off_rush":  ("team-offense", "rushing-analytics", "offense"),
    "def_rush":  ("team-defense", "rush-analytics", "defense"),
    "tempo":     ("team-offense", "tempo", "offense"),
    "off_ovw":   ("team-offense", "overview", "offense"),
    "def_ovw":   ("team-defense", "overview", "defense"),
}

TEAMS = {
    "Arizona Cardinals": "ARZ", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BLT",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLV", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HST", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LA", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS",
}

# Overview repeats YD/TD for passing then rushing; disambiguate positionally.
OVERVIEW_COLS = ["Team", "GP", "yd_ply", "pt_gm", "fd_pct", "turnovers", "dpbk_pct",
                 "pass_yd", "pass_td", "interceptions", "rush_pct", "rush_yd", "rush_td"]

RENAME = {
    "EPA/ATT": "epa_att", "SUCC%": "succ_pct", "DVOA": "dvoa", "aRYOE": "aryoe",
    "EXP%": "exp_pct", "STF%": "stf_pct", "aYBCO": "aybco", "aYACO": "ayaco",
    "YBCO": "aybco", "YACO": "ayaco", "CRT%": "crt_pct",
    "PLY/GM": "ply_gm", "TOP": "top", "DRV/GM": "drv_gm", "SEC/PLY": "sec_ply",
    "PLY/DRV": "ply_drv", "YD/DRV": "yd_drv", "SEC/DRV": "sec_drv",
    "3&O": "three_and_out_pct", "SCD%": "scd_pct",
}


def num(v):
    """'46.9%' -> 46.9 ; '' -> None ; '1,234' -> 1234.0"""
    if v is None:
        return None
    v = v.strip().replace(",", "").rstrip("%")
    if v in ("", "-", "--"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch(category, table, season):
    r = requests.get(f"{BFF}/{category}/tables/{table}/export.csv",
                     params={"season": season, "seasonType": "REG"},
                     headers={"User-Agent": UA}, timeout=45)
    r.raise_for_status()
    rows = list(csv.reader(io.StringIO(r.text)))
    if not rows:
        raise RuntimeError(f"{category}/{table}: empty export")
    header, body = rows[0], rows[1:]
    if len(body) != 32:
        raise RuntimeError(f"{category}/{table}: expected 32 teams, got {len(body)}")

    is_overview = table == "overview"
    out = {}
    for row in body:
        name = row[0]
        if name not in TEAMS:
            raise RuntimeError(f"{category}/{table}: unmapped team {name!r}")
        rec = {}
        if is_overview:
            for key, val in zip(OVERVIEW_COLS[1:], row[1:]):
                rec[key] = num(val)
        else:
            for col, val in zip(header[1:], row[1:]):
                rec[RENAME.get(col, col.lower().replace("/", "_").replace("%", "_pct"))] = num(val)
        rec.pop("gp", None); rec.pop("GP", None)
        out[TEAMS[name]] = rec
    return out


def fetch_all(season):
    return {k: fetch(cat, tbl, season) for k, (cat, tbl, _) in TABLES.items()}
