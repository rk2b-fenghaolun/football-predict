# 赔率时间序列（最关键）
from ..util.data_util import query_df
import numpy as np

def extract_odds(conn, match_id, match_date):
    sql = """
    SELECT *
    FROM football_match_odds_his
    WHERE match_id = :match_id
      AND odds_type = 'hadList'
      AND (update_date || ' ' || update_time) <= :match_date
    ORDER BY update_date, update_time
    """
    df = query_df(conn, sql, {
        "match_id": match_id,
        "match_date": match_date
    })

    if df.empty:
        return {
            "home_odds": None,
            "draw_odds": None,
            "away_odds": None,
            "odds_available": 0
        }

    # 假设 odds_json 已解析为 dict 或你在入库前处理过
    open_odds = df.iloc[0]["odds_json"]
    close_odds = df.iloc[-1]["odds_json"]

    return {
        "home_odds": close_odds["home"],
        "draw_odds": close_odds["draw"],
        "away_odds": close_odds["away"],
        "home_odds_delta": close_odds["home"] - open_odds["home"],
        "draw_odds_delta": close_odds["draw"] - open_odds["draw"],
        "away_odds_delta": close_odds["away"] - open_odds["away"],
        "odds_available": 1
    }


def insert_odds_history(conn, match_id, update_date, update_time, odds_type, odds_json):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO football_match_odds_his (match_id, update_date, update_time, odds_type, odds_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (match_id, update_date, update_time, odds_type, odds_json))
    conn.commit()
