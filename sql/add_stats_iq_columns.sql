-- Stats iQ advanced columns (rushing-analytics, overview, tempo).
-- tempo_* columns are offense-only; FTN publishes no defensive tempo table.

alter table nfl_rushing_team_stats add column if not exists "epa_att" numeric;
alter table nfl_rushing_team_stats add column if not exists "succ_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "dvoa" numeric;
alter table nfl_rushing_team_stats add column if not exists "aryoe" numeric;
alter table nfl_rushing_team_stats add column if not exists "exp_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "stf_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "aybco" numeric;
alter table nfl_rushing_team_stats add column if not exists "ayaco" numeric;
alter table nfl_rushing_team_stats add column if not exists "crt_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "yd_ply" numeric;
alter table nfl_rushing_team_stats add column if not exists "pt_gm" numeric;
alter table nfl_rushing_team_stats add column if not exists "fd_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "turnovers" numeric;
alter table nfl_rushing_team_stats add column if not exists "dpbk_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "pass_yd" numeric;
alter table nfl_rushing_team_stats add column if not exists "pass_td" numeric;
alter table nfl_rushing_team_stats add column if not exists "interceptions" numeric;
alter table nfl_rushing_team_stats add column if not exists "rush_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "rush_yd" numeric;
alter table nfl_rushing_team_stats add column if not exists "rush_td" numeric;
alter table nfl_rushing_team_stats add column if not exists "ply_gm" numeric;
alter table nfl_rushing_team_stats add column if not exists "top" numeric;
alter table nfl_rushing_team_stats add column if not exists "drv_gm" numeric;
alter table nfl_rushing_team_stats add column if not exists "sec_ply" numeric;
alter table nfl_rushing_team_stats add column if not exists "ply_drv" numeric;
alter table nfl_rushing_team_stats add column if not exists "yd_drv" numeric;
alter table nfl_rushing_team_stats add column if not exists "sec_drv" numeric;
alter table nfl_rushing_team_stats add column if not exists "three_and_out_pct" numeric;
alter table nfl_rushing_team_stats add column if not exists "scd_pct" numeric;
