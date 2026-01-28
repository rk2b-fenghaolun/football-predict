CREATE VIEW IF NOT EXISTS vw_match_train_pre_level1 AS
WITH odds_last AS (
    SELECT
        o.match_id,
        CAST(json_extract(o.odds_json, '$.h') AS REAL) AS odds_h,
        CAST(json_extract(o.odds_json, '$.d') AS REAL) AS odds_d,
        CAST(json_extract(o.odds_json, '$.a') AS REAL) AS odds_a
    FROM football_match_odds_his o
    JOIN football_match m ON o.match_id = m.match_id
    WHERE o.odds_type = 'hadList'
      -- 用户确认所有赔率数据均为赛前获取，无穿越风险，取最新一条即可
      AND (o.update_date || ' ' || o.update_time) = (
          SELECT MAX(o2.update_date || ' ' || o2.update_time)
          FROM football_match_odds_his o2
          WHERE o2.match_id = o.match_id
            AND o2.odds_type = 'hadList'
      )
),
odds_prob AS (
    SELECT
        match_id,
        (1.0 / odds_h) /
        ((1.0 / odds_h) + (1.0 / odds_d) + (1.0 / odds_a)) AS odds_h_prob,
        (1.0 / odds_d) /
        ((1.0 / odds_h) + (1.0 / odds_d) + (1.0 / odds_a)) AS odds_d_prob,
        (1.0 / odds_a) /
        ((1.0 / odds_h) + (1.0 / odds_d) + (1.0 / odds_a)) AS odds_a_prob
    FROM odds_last
),
table_home AS (
    SELECT
        match_id,
        points AS home_points,
        netGoal AS home_goal_diff
    FROM football_match_preview_tables
    WHERE type = 'home'
),
table_away AS (
    SELECT
        match_id,
        points AS away_points,
        netGoal AS away_goal_diff
    FROM football_match_preview_tables
    WHERE type = 'away'
)

SELECT
    m.match_id,
    m.match_date,
    m.league_id,
    m.home_team_id,
    m.away_team_id,

    r.win_flag,

    -- odds
    o.odds_h_prob,
    o.odds_d_prob,
    o.odds_a_prob,

    -- season strength
    h.home_points,
    a.away_points,
    h.home_goal_diff,
    a.away_goal_diff,

    -- diff features
    (h.home_points - a.away_points) AS points_diff,
    (h.home_goal_diff - a.away_goal_diff) AS goal_diff_diff

FROM football_match m
JOIN football_match_result r
  ON m.match_id = r.match_id

LEFT JOIN odds_prob o
  ON m.match_id = o.match_id

LEFT JOIN table_home h
  ON m.match_id = h.match_id

LEFT JOIN table_away a
  ON m.match_id = a.match_id

WHERE
    o.odds_h_prob IS NOT NULL
    AND h.home_points IS NOT NULL
    AND a.away_points IS NOT NULL;
