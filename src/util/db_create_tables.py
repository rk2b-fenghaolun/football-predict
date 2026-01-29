from util.data_util import get_conn

from util.config import DB_NAME

CREATE_TABLES_SQL = [
    '''CREATE TABLE IF NOT EXISTS football_league (
        league_id INTEGER PRIMARY KEY,
        league_abb_name TEXT, -- 联赛简称
        league_all_name TEXT -- 联赛全称
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match (
        match_id INTEGER PRIMARY KEY,
        match_num TEXT, -- 比赛编号
        match_num_str TEXT, -- 比赛编号字符串
        match_date TEXT, -- 比赛日期 YYYY-MM-DD
        league_id INTEGER, -- 联赛ID
        league_name TEXT, -- 联赛名称
        league_name_abbr TEXT, -- 联赛简称
        league_back_color TEXT, -- 联赛背景色
        home_team TEXT, -- 主队名称
        home_team_id INTEGER, -- 主队ID
        away_team TEXT, -- 客队名称
        away_team_id INTEGER, -- 客队ID
        all_home_team TEXT, -- 主队全称
        all_away_team TEXT, -- 客队全称
        goal_line TEXT -- 让球数
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_result (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER UNIQUE,
        home_score INTEGER,  -- 主队得分
        away_score INTEGER, -- 客队得分
        sections_no1 TEXT, -- 半场比分
        sections_no999 TEXT, -- 总比分
        win_flag TEXT, -- 结果标志 H 主胜 D 平 A 客胜
        FOREIGN KEY(match_id) REFERENCES football_match(match_id)
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_result_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        type TEXT,   -- 类型 home 主队 away 客队
        team_id INTEGER, -- 球队ID
        stats_data TEXT,   -- 客队
        stats_tc TEXT, -- 统计类型(控球,进球,射正,射偏,角球,越位,犯规,黄牌)
        stats_tc_desc TEXT -- 统计类型描述
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_result_lineup (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team_type TEXT, -- home/away
        team_id INTEGER, -- 球队ID
        team_name TEXT, -- 球队名称
        formation TEXT, -- 4-3-3, 4-4-2, etc
        player_positions_json TEXT, -- JSON存储球员位置
        starting_xi TEXT, -- 首发11人ID列表
        substitutes TEXT, -- 替补ID列表
        FOREIGN KEY(match_id) REFERENCES football_match(match_id)
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_result_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        team_id INTEGER, -- 球队ID
        event_team TEXT, -- home/away
        event_type TEXT, -- 类型
        event_time TEXT, -- 事件时间
        event_player TEXT, -- 球员
        event_json TEXT, -- 事件详情JSON
        FOREIGN KEY(match_id) REFERENCES football_match(match_id)
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_odds_his (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        update_date TEXT, -- YYYY-MM-DD
        update_time TEXT, -- HH:MM:SS
        odds_type TEXT, -- hadList 胜平负, hhadList 让球胜平负, crsList 总比分, hafuList 半场比分, ttgList 总进球
        odds_json TEXT
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_preview_player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        type TEXT,   -- 类型 home 主队 away 客队
        team_id INTEGER,   -- 球队ID
        player_id TEXT, -- 球员ID
        player_name TEXT, -- 球员名称
        position TEXT, -- 位置
        appearanceCnt INTEGER, -- 出场次数
        startedMatchCnt INTEGER, -- 首发次数
        substituteMatchCnt INTEGER, -- 替补登场次数
        goalCnt INTEGER, -- 进球数
        goalAvgCnt REAL, -- 场均进球
        goalProbability REAL, -- 进球率
        assistCnt INTEGER, -- 助攻数
        assistAvgCnt REAL, -- 场均助攻
        assistProbability REAL, -- 助攻率
        goals INTEGER, -- 进球数
        assists INTEGER, -- 助攻数
        injury_flag INTEGER, -- 伤停标志 0 否 1 是
        suspension_flag INTEGER -- 停赛标志 0 否 1 是
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_preview_feature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        type TEXT,   -- 类型 eachHomeAway 近10场战况 eachSameHomeAway 同主客战况 last 近10场交锋 sameHomeAway 同主客交锋
        awayDrawMatchCnt INTEGER, -- 客队平场次
        awayLossGoalMatchCnt INTEGER,  -- 客队负场次
        awayWinGoalMatchCnt INTEGER,      -- 客队胜场次
        homeDrawMatchCnt INTEGER,  -- 主队平场次
        homeLossGoalMatchCnt INTEGER,      -- 主队负场次
        homeWinGoalMatchCnt INTEGER      -- 主队胜场次
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_preview_goal_avg (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        awayGoalAvgCnt INTEGER,  -- 客队场均进球
        homeGoalAvgCnt INTEGER,  -- 主队场均进球
        awayLossGoalAvgCnt INTEGER,  -- 客队场均失球
        homeLossGoalAvgCnt INTEGER -- 主队场均失球
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_preview_tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        type TEXT,   -- 类型 home 主队 away 客队
        team_id INTEGER,   -- 球队ID
        totalLegCnt INTEGER, -- 联赛总场次
        winGoalMatchCnt INTEGER,   -- 胜
        drawMatchCnt INTEGER,      -- 平
        lossGoalMatchCnt INTEGER,  -- 负
        goalCnt INTEGER,   -- 进球
        lossGoalCnt INTEGER,  -- 失球
        netGoal INTEGER, -- 净进球
        points INTEGER, -- 积分
        ranking INTEGER -- 排名
    );''',
    '''CREATE TABLE IF NOT EXISTS football_team_match_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        type TEXT,   -- 类型 home 主队 away 客队,
        season_id INTEGER, -- 赛季ID
        league_id INTEGER, -- 联赛ID
        league_name TEXT, -- 联赛名称
        current_round INTEGER,  -- 当前第几轮
        league_total_rounds INTEGER, -- 联赛总轮数
        matches_played INTEGER,  -- 累计比赛数
        wins INTEGER, -- 胜
        draws INTEGER, -- 平
        losses INTEGER, -- 负
        goals_for INTEGER, -- 进球
        goals_against INTEGER, -- 失球
        goal_diff INTEGER, -- 净进球
        points INTEGER, -- 积分
        ranking INTEGER, -- 排名
        ranking_missing_flag INTEGER,        -- 1 = 该轮排名无意义
        round_ratio REAL, -- current_round / league_total_rounds
        points_per_match REAL, -- 场均积分 = points / matches_played
        goals_for_per_match REAL, -- 场均进球 = goals_for / matches_played
        goals_against_per_match REAL, -- 场均失球 = goals_against / matches_played
        goal_diff_per_match REAL, -- 场均净进球 = goal_diff / matches_played
        win_rate REAL, -- 胜率
        draw_rate REAL, -- 平率
        loss_rate REAL -- 负率
    );''',
    '''CREATE TABLE IF NOT EXISTS football_match_preview_future_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        type TEXT,   -- 类型 home 主队 away 客队
        team_id INTEGER, -- 球队ID
        matchDateTime TEXT, -- 比赛日期时间
        tournamentId INTEGER,   -- 赛制ID
        tournamentShortName TEXT,      -- 赛制名称
        seasonId INTEGER,  -- 轮次ID
        gameweek INTEGER,   -- 轮次
        awayTeamId INTEGER, -- 客队ID
        awayTeamShortName TEXT, -- 客队简称
        homeTeamId INTEGER, -- 主队ID
        homeTeamShortName TEXT  -- 主队简称
    );'''
]

def create_tables():
    conn = get_conn(DB_NAME)
    cursor = conn.cursor()
    for sql in CREATE_TABLES_SQL:
        cursor.execute(sql)
    conn.commit()
    conn.close()
    print(f"数据库 {DB_NAME} 表结构已创建！")

if __name__ == "__main__":
    create_tables()
