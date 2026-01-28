DROP TABLE IF EXISTS train_baseline_draw;

CREATE TABLE train_baseline_draw AS
SELECT
    m.match_id,

    /* ===== Label ===== */
    r.win_flag,

    /* ===== Odds ===== */
    CAST(json_extract(had.odds_json, '$.h') AS REAL) AS odds_h,
    CAST(json_extract(had.odds_json, '$.d') AS REAL) AS odds_d,
    CAST(json_extract(had.odds_json, '$.a') AS REAL) AS odds_a,

    /* 市场犹豫度 */
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
    g.homeLossGoalAvgCnt + g.awayLossGoalAvgCnt AS total_loss_goal_avg

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
