-- NFL team rushing stats scraped from FTN's statshub API.
-- One row per (season, scrape date, side, team) so history accumulates
-- for backtesting rather than being overwritten.

create table if not exists nfl_rushing_team_stats (
    season         integer     not null,
    scraped_on     date        not null,
    scraped_at     timestamptz not null default now(),
    side           text        not null check (side in ('offense','defense')),
    team           text        not null,
    games          integer,
    attempts       integer,
    rushing_yards  integer,
    ypc            numeric(6,4),
    rushing_tds    integer,
    first_downs    integer,
    fumbles        integer,
    fumbles_lost   integer,
    long_run       integer,
    rushing_snaps  integer,
    primary key (season, scraped_on, side, team)
);

create index if not exists nfl_rushing_team_stats_lookup
    on nfl_rushing_team_stats (season, side, team, scraped_on desc);

-- Latest snapshot per team/side, which is what a model should read.
create or replace view nfl_rushing_latest as
select distinct on (season, side, team) *
from nfl_rushing_team_stats
order by season, side, team, scraped_on desc;

-- Rebuilt after adding Stats iQ columns; `select *` views freeze their
-- column list at creation, so this must be re-run whenever columns are added.
drop view if exists nfl_rushing_latest;
create view nfl_rushing_latest as
select distinct on (season, side, team) *
from nfl_rushing_team_stats
order by season, side, team, scraped_on desc;
