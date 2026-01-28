# 近期战况
from ..util.data_util import query_df

def extract_recent_form(conn, match_id, match_date, n=10):
    sql = """
    SELECT m.match_date, r.win_flag,
           m.home_team_id, m.away_team_id
    FROM football_match m
    JOIN football_match_result r ON m.match_id = r.match_id
    WHERE m.match_date < :match_date
      AND (
        m.home_team_id = :home_id OR m.away_team_id = :home_id
        OR m.home_team_id = :away_id OR m.away_team_id = :away_id
      )
    ORDER BY m.match_date DESC
    LIMIT :n
    """
    base = query_df(conn, """
        SELECT home_team_id, away_team_id
        FROM football_match
        WHERE match_id = :match_id
    """, {"match_id": match_id}).iloc[0]

    df = query_df(conn, sql, {
        "match_date": match_date,
        "home_id": base["home_team_id"],
        "away_id": base["away_team_id"],
        "n": n
    })

    if df.empty:
        return {}

    win_cnt = (df["win_flag"] == "H").sum()
    draw_cnt = (df["win_flag"] == "D").sum()
    loss_cnt = (df["win_flag"] == "A").sum()

    return {
        "recent_win_rate": win_cnt / len(df),
        "recent_draw_rate": draw_cnt / len(df),
        "recent_loss_rate": loss_cnt / len(df),
    }
