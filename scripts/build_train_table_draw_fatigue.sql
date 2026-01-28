DROP TABLE IF EXISTS train_baseline_draw_fatigue;

CREATE TABLE train_baseline_draw_fatigue AS
SELECT
    m.match_id,
    r.win_flag,

    /* ===== Odds ===== */
    CAST(json_extract(had.odds_json, '$.h') AS REAL) AS odds_h,
    CAST(json_extract(had.odds_json, '$.d') AS REAL) AS odds_d,
    CAST(json_extract(had.odds_json, '$.a') AS REAL) AS odds_a,
    ABS(
        CAST(json_extract(had.odds_json, '$.h') AS REAL) -
        CAST(json_extract(had.odds_json, '$.a') AS REAL)
    ) AS odds_ha_gap,

    /* ===== 实力接近度 ===== */
    ABS(
        (
            f.homeWinGoalMatchCnt * 1.0 /
            NULLIF(
                f.homeWinGoalMatchCnt +
                f.homeDrawMatchCnt +
                f.homeLossGoalMatchCnt, 0
            )
        )
        -
        (
            f.awayWinGoalMatchCnt * 1.0 /
            NULLIF(
                f.awayWinGoalMatchCnt +
                f.awayDrawMatchCnt +
                f.awayLossGoalMatchCnt, 0
            )
        )
    ) AS win_rate_gap,

    /* ===== 进球期望 ===== */
    g.homeGoalAvgCnt + g.awayGoalAvgCnt AS total_goal_avg,

    /* ===== 疲劳：过去 7 天比赛数 ===== */
    (
        SELECT COUNT(1)
        FROM football_match fm2
        WHERE fm2.home_team_id = m.home_team_id
           OR fm2.away_team_id = m.home_team_id
          AND fm2.match_date BETWEEN
              date(m.match_date, '-7 day')
              AND m.match_date
    ) AS home_matches_last_7d,

    (
        SELECT COUNT(1)
        FROM football_match fm2
        WHERE fm2.home_team_id = m.away_team_id
           OR fm2.away_team_id = m.away_team_id
          AND fm2.match_date BETWEEN
              date(m.match_date, '-7 day')
              AND m.match_date
    ) AS away_matches_last_7d,

    /* ===== 分心：未来 5 天是否有比赛 ===== */
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM football_match_preview_future_matches fmf
            WHERE fmf.team_id = m.home_team_id
              AND fmf.matchDateTime BETWEEN
                  m.match_date
                  AND date(m.match_date, '+5 day')
        ) THEN 1 ELSE 0
    END AS home_has_future_match,

    CASE
        WHEN EXISTS (
            SELECT 1
            FROM football_match_preview_future_matches fmf
            WHERE fmf.team_id = m.away_team_id
              AND fmf.matchDateTime BETWEEN
                  m.match_date
                  AND date(m.match_date, '+5 day')
        ) THEN 1 ELSE 0
    END AS away_has_future_match

FROM football_match m

JOIN football_match_result r
    ON m.match_id = r.match_id

LEFT JOIN football_match_odds_his had
    ON m.match_id = had.match_id
   AND had.odds_type = 'hadList'

LEFT JOIN football_match_preview_feature f
    ON m.match_id = f.match_id
   AND f.type = 'eachHomeAway'

LEFT JOIN football_match_preview_goal_avg g
    ON m.match_id = g.match_id

WHERE
    r.win_flag IN ('H', 'D', 'A')
    AND had.odds_json IS NOT NULL;
