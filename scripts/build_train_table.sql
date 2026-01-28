DROP TABLE IF EXISTS train_baseline_pre;

CREATE TABLE train_baseline_pre AS
SELECT
    m.match_id,

    /* ===== Label ===== */
    r.win_flag,

    /* ===== Odds features ===== */
    CAST(json_extract(had.odds_json, '$.h') AS REAL) AS odds_h,
    CAST(json_extract(had.odds_json, '$.d') AS REAL) AS odds_d,
    CAST(json_extract(had.odds_json, '$.a') AS REAL) AS odds_a,

    /* ===== Form features (PRE-computed) ===== */
    f.homeWinGoalMatchCnt * 1.0 /
        NULLIF(
            f.homeWinGoalMatchCnt +
            f.homeDrawMatchCnt +
            f.homeLossGoalMatchCnt, 0
        ) AS home_win_rate,

    f.awayWinGoalMatchCnt * 1.0 /
        NULLIF(
            f.awayWinGoalMatchCnt +
            f.awayDrawMatchCnt +
            f.awayLossGoalMatchCnt, 0
        ) AS away_win_rate,

    /* 差值是关键 */
    (
        f.homeWinGoalMatchCnt * 1.0 /
        NULLIF(
            f.homeWinGoalMatchCnt +
            f.homeDrawMatchCnt +
            f.homeLossGoalMatchCnt, 0
        )
        -
        f.awayWinGoalMatchCnt * 1.0 /
        NULLIF(
            f.awayWinGoalMatchCnt +
            f.awayDrawMatchCnt +
            f.awayLossGoalMatchCnt, 0
        )
    ) AS win_rate_diff

FROM football_match m

JOIN football_match_result r
    ON m.match_id = r.match_id

LEFT JOIN football_match_odds_his had
    ON m.match_id = had.match_id
   AND had.odds_type = 'hadList'

LEFT JOIN football_match_preview_feature f
    ON m.match_id = f.match_id
   AND f.type = 'eachHomeAway'

WHERE
    r.win_flag IN ('H', 'D', 'A')
    AND had.odds_json IS NOT NULL;
