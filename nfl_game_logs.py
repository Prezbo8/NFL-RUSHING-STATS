"""Per-game rushing logs from nflverse.

FTN's statshub can filter by week, but it lags a day or two and carries no
schedule, so pairing a defense to the offense it faced means guessing. nflverse
publishes weekly player rows that already carry `opponent_team`, which gives
both the game log and the "allowed" side for free.

Cross-checked against FTN: KC weeks 1 and 2 agree to the carry.
"""
import csv
import io
from collections import defaultdict

import requests

WEEKLY = ("https://github.com/nflverse/nflverse-data/releases/download/"
          "stats_player/stats_player_week_{season}.csv")
SCHEDULE = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"

# nflverse uses standard codes; the rest of this project uses FTN's
TO_FTN = {"ARI":"ARZ", "BAL":"BLT", "CLE":"CLV", "HOU":"HST", "LAR":"LA", "WAS":"WAS"}
ftn = lambda t: TO_FTN.get(t, t)

RUSH_POS = {"RB", "FB", "WR", "QB", "TE"}


def fetch(season):
    r = requests.get(WEEKLY.format(season=season), timeout=90)
    r.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(r.text)))
    if not rows:
        raise RuntimeError("nflverse returned no rows")
    return [r for r in rows if (r.get("season_type") or "REG") == "REG"]


def scores(season):
    """(week, team) -> (points for, points against). Final scores only."""
    r = requests.get(SCHEDULE, timeout=90)
    r.raise_for_status()
    out = {}
    for g in csv.DictReader(io.StringIO(r.text)):
        if g["season"] != str(season) or g.get("game_type") != "REG":
            continue
        if not g.get("home_score") or not g.get("away_score"):
            continue                                   # not played yet
        wk, h, a = int(g["week"]), ftn(g["home_team"]), ftn(g["away_team"])
        hs, as_ = int(g["home_score"]), int(g["away_score"])
        out[(wk, h)] = (hs, as_)
        out[(wk, a)] = (as_, hs)
    return out


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def build(season):
    """-> (team game logs, per-player game logs)"""
    rows = fetch(season)
    sc = scores(season)
    games, players = defaultdict(lambda: defaultdict(float)), []

    for r in rows:
        car = num(r.get("carries"))
        if car <= 0:
            continue
        team, opp, wk = ftn(r["team"]), ftn(r["opponent_team"]), int(r["week"])
        g = games[(wk, team, opp)]
        g["carries"] += car
        g["rush_yards"] += num(r.get("rushing_yards"))
        g["rush_tds"] += num(r.get("rushing_tds"))
        g["rush_first_downs"] += num(r.get("rushing_first_downs"))
        g["rush_epa"] += num(r.get("rushing_epa"))
        if r.get("position") in RUSH_POS:
            players.append({
                "season": season, "week": wk, "team": team, "opponent": opp,
                "player": r.get("player_display_name"), "position": r.get("position"),
                "carries": int(car), "rush_yards": int(num(r.get("rushing_yards"))),
                "rush_tds": int(num(r.get("rushing_tds"))),
                "rush_epa": round(num(r.get("rushing_epa")), 3),
            })

    team_rows = [{
        "season": season, "week": wk, "team": t, "opponent": o,
        "points_for": sc.get((wk, t), (None, None))[0],
        "points_against": sc.get((wk, t), (None, None))[1],
        "carries": int(v["carries"]), "rush_yards": int(v["rush_yards"]),
        "rush_tds": int(v["rush_tds"]), "rush_first_downs": int(v["rush_first_downs"]),
        "rush_epa": round(v["rush_epa"], 3),
        "ypc": round(v["rush_yards"] / v["carries"], 4) if v["carries"] else None,
    } for (wk, t, o), v in games.items()]

    verify(team_rows)
    players.sort(key=lambda p: (-p["week"], p["team"], -p["rush_yards"]))
    return team_rows, players


def verify(team_rows):
    """Every game must appear twice, once from each side."""
    seen = {(r["week"], r["team"], r["opponent"]) for r in team_rows}
    orphans = [k for k in seen if (k[0], k[2], k[1]) not in seen]
    if orphans:
        # a shutout-on-the-ground team has no rushing rows at all, so a missing
        # mirror is possible; flag rather than fail
        print(f"  note: {len(orphans)} game(s) with only one side logged: {orphans[:4]}")


if __name__ == "__main__":
    t, p = build(2026)
    print(f"{len(t)} team-games, {len(p)} player-games")
    missing = [r for r in t if r["points_for"] is None]
    print(f"games without a final score: {len(missing)}")
    wks = sorted({r['week'] for r in t})
    print("weeks:", wks)
    kc = sorted([r for r in t if r["team"] == "KC"], key=lambda r: r["week"])
    for r in kc:
        res = ("W" if r["points_for"] > r["points_against"] else
               "L" if r["points_for"] < r["points_against"] else "T") if r["points_for"] is not None else "?"
        print(f"  KC wk{r['week']} vs {r['opponent']}: {r['carries']} car "
              f"{r['rush_yards']} yds {r['rush_tds']} td | {res} "
              f"{r['points_for']}-{r['points_against']}")
