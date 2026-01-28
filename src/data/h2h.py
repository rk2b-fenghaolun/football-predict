# 历史交锋
from ..util.data_util import query_df

def extract_h2h(conn, match_id):
    sql = """
    SELECT *
    FROM football_match_preview_feature
    WHERE match_id = :match_id
      AND type = 'last'
    """
    df = query_df(conn, sql, {"match_id": match_id})
    if df.empty:
        return {}

    r = df.iloc[0]
    total = (
        r["homeWinGoalMatchCnt"] + r["homeDrawMatchCnt"] +
        r["homeLossGoalMatchCnt"]
    )

    if total == 0:
        return {}

    return {
        "h2h_home_win_rate": r["homeWinGoalMatchCnt"] / total,
        "h2h_draw_rate": r["homeDrawMatchCnt"] / total,
        "h2h_away_win_rate": r["homeLossGoalMatchCnt"] / total,
    }
