# 场均进失球
from ..util.data_util import query_one

def extract_goal_avg(conn, match_id):
    row = query_one(conn, """
        SELECT *
        FROM football_match_preview_goal_avg
        WHERE match_id = :match_id
    """, {"match_id": match_id})

    if row is None:
        return {}

    return {
        "goal_avg_diff": row["homeGoalAvgCnt"] - row["awayGoalAvgCnt"],
        "loss_goal_avg_diff": row["homeLossGoalAvgCnt"] - row["awayLossGoalAvgCnt"],
    }

def insert_goal_avg(conn, match_id, goal_avg, loss_goal_avg):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO football_match_preview_goal_avg (
            match_id, awayGoalAvgCnt, homeGoalAvgCnt, awayLossGoalAvgCnt, homeLossGoalAvgCnt
        ) VALUES (?, ?, ?, ?, ?)
    ''', (
        match_id,
        goal_avg.get('awayGoalAvgCnt', 0),
        goal_avg.get('homeGoalAvgCnt', 0),
        loss_goal_avg.get('awayLossGoalAvgCnt', 0),
        loss_goal_avg.get('homeLossGoalAvgCnt', 0)
    ))
    conn.commit()
