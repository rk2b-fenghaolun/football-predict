DROP TABLE IF EXISTS train_baseline_draw_lineup;

CREATE TABLE train_baseline_draw_lineup AS
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

    /* ===== 阵容稳定性：主队 ===== */
    (
        SELECT COUNT(1)
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'home'
          AND (p.injury_flag = 1 OR p.suspension_flag = 1)
    ) AS home_unavailable_cnt,

    (
        SELECT AVG(
            CASE
                WHEN p.appearanceCnt > 0
                THEN p.startedMatchCnt * 1.0 / p.appearanceCnt
                ELSE 0
            END
        )
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'home'
    ) AS home_start_ratio_avg,

    (
        SELECT AVG(p.appearanceCnt)
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'home'
    ) AS home_appearance_avg,

    /* ===== 阵容稳定性：客队 ===== */
    (
        SELECT COUNT(1)
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'away'
          AND (p.injury_flag = 1 OR p.suspension_flag = 1)
    ) AS away_unavailable_cnt,

    (
        SELECT AVG(
            CASE
                WHEN p.appearanceCnt > 0
                THEN p.startedMatchCnt * 1.0 / p.appearanceCnt
                ELSE 0
            END
        )
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'away'
    ) AS away_start_ratio_avg,

    (
        SELECT AVG(p.appearanceCnt)
        FROM football_match_preview_player p
        WHERE p.match_id = m.match_id
          AND p.type = 'away'
    ) AS away_appearance_avg

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
