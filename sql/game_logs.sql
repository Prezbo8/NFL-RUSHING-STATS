-- Per-game rushing, both sides of every game, from nflverse.
-- A team's "allowed" line is simply its opponent's row for the same week.

create table if not exists nfl_game_logs (
    season            integer not null,
    week              integer not null,
    team              text    not null,
    opponent          text    not null,
    carries           integer,
    rush_yards        integer,
    rush_tds          integer,
    rush_first_downs  integer,
    rush_epa          numeric,
    ypc               numeric(6,4),
    primary key (season, week, team)
);
create index if not exists nfl_game_logs_lookup on nfl_game_logs (season, team, week desc);

create table if not exists nfl_rb_game_logs (
    season      integer not null,
    week        integer not null,
    team        text    not null,
    opponent    text    not null,
    player      text    not null,
    position    text,
    carries     integer,
    rush_yards  integer,
    rush_tds    integer,
    rush_epa    numeric,
    primary key (season, week, team, player)
);
create index if not exists nfl_rb_logs_lookup on nfl_rb_game_logs (season, opponent, week desc);
