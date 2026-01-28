# 积分榜（稳定核心特征）
from ..util.data_util import query_df

def extract_rank_table(conn, match_id, match_date):
    sql = """
    SELECT type, totalLegCnt, winGoalMatchCnt, drawMatchCnt,
           lossGoalMatchCnt, goalCnt, lossGoalCnt,
           netGoal, points, ranking
    FROM football_match_preview_tables
    WHERE match_id = :match_id
    """
    df = query_df(conn, sql, {"match_id": match_id})
    if df.empty or len(df) < 2:
        return {}

    home = df[df["type"] == "home"].iloc[0]
    away = df[df["type"] == "away"].iloc[0]

    return {
        "rank_diff": home["ranking"] - away["ranking"],
        "point_per_match_diff":
            (home["points"] / max(home["totalLegCnt"], 1)) -
            (away["points"] / max(away["totalLegCnt"], 1)),
        "net_goal_avg_diff":
            (home["netGoal"] / max(home["totalLegCnt"], 1)) -
            (away["netGoal"] / max(away["totalLegCnt"], 1)),
    }

def insert_tables(conn, match_id, type, tables):
    cursor = conn.cursor()
    if tables:
        cursor.execute('''
            INSERT INTO football_match_preview_tables (
            match_id, type, totalLegCnt, winGoalMatchCnt, drawMatchCnt, lossGoalMatchCnt,
            goalCnt, lossGoalCnt, netGoal, points, ranking
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            type,
            tables.get('totalLegCnt', 0),
            tables.get('winGoalMatchCnt', 0),
            tables.get('drawMatchCnt', 0),
            tables.get('lossGoalMatchCnt', 0),
            tables.get('goalCnt', 0),
            tables.get('lossGoalCnt', 0),
            tables.get('netGoal', 0),
            int(tables.get('points', 0)),
            int(tables.get('ranking', 0))
        ))
    conn.commit()
