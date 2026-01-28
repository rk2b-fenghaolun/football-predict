CREATE VIEW IF NOT EXISTS vw_match_train_pre_level2 AS
WITH base AS (
    SELECT *
    FROM vw_match_train_pre_level1
),

recent_form AS (
    SELECT
        match_id,

        -- 主队近10场
        homeWinGoalMatchCnt * 1.0 / 
        (homeWinGoalMatchCnt + homeDrawMatchCnt + homeLossGoalMatchCnt) 
        AS home_win_rate_10,

        homeDrawMatchCnt * 1.0 /
        (homeWinGoalMatchCnt + homeDrawMatchCnt + homeLossGoalMatchCnt)
        AS home_draw_rate_10,

        -- 客队近10场
        awayWinGoalMatchCnt * 1.0 /
        (awayWinGoalMatchCnt + awayDrawMatchCnt + awayLossGoalMatchCnt)
        AS away_win_rate_10,

        awayDrawMatchCnt * 1.0 /
        (awayWinGoalMatchCnt + awayDrawMatchCnt + awayLossGoalMatchCnt)
        AS away_draw_rate_10

    FROM football_match_preview_feature
    WHERE type = 'eachHomeAway'
),

goal_avg AS (
    SELECT
        match_id,
        homeGoalAvgCnt AS home_goal_avg,
        homeLossGoalAvgCnt AS home_concede_avg,
        awayGoalAvgCnt AS away_goal_avg,
        awayLossGoalAvgCnt AS away_concede_avg
    FROM football_match_preview_goal_avg
)

SELECT
    b.*,

    -- ===== 近10场状态 =====
    rf.home_win_rate_10,
    rf.home_draw_rate_10,
    rf.away_win_rate_10,
    rf.away_draw_rate_10,

    -- ===== 进球节奏 =====
    ga.home_goal_avg,
    ga.home_concede_avg,
    ga.away_goal_avg,
    ga.away_concede_avg,

    -- ===== 平局强化 =====
    ABS(ga.home_goal_avg - ga.away_goal_avg) AS goal_avg_diff,
    ABS(rf.home_draw_rate_10 - rf.away_draw_rate_10) AS draw_rate_diff

FROM base b
LEFT JOIN recent_form rf
    ON b.match_id = rf.match_id
LEFT JOIN goal_avg ga
    ON b.match_id = ga.match_id

WHERE
    rf.home_win_rate_10 IS NOT NULL
    AND ga.home_goal_avg IS NOT NULL;
