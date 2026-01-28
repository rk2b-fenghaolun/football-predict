# 特征分析
from ..util.data_util import query_df

def insert_feature(conn, match_id, type, feature_away):
    cursor = conn.cursor()
    if feature_away:
        cursor.execute('''
            INSERT INTO football_match_preview_feature (
                match_id, type, awayDrawMatchCnt, awayLossGoalMatchCnt, awayWinGoalMatchCnt,
                homeDrawMatchCnt, homeLossGoalMatchCnt, homeWinGoalMatchCnt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            type,
            feature_away.get('awayDrawMatchCnt', 0),
            feature_away.get('awayLossGoalMatchCnt', 0),
            feature_away.get('awayWinGoalMatchCnt', 0),
            feature_away.get('homeDrawMatchCnt', 0),
            feature_away.get('homeLossGoalMatchCnt', 0),
            feature_away.get('homeWinGoalMatchCnt', 0)
        ))
    conn.commit()
