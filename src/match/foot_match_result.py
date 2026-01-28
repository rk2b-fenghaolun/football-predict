import sys

from util.data_util import get_conn
from data.base import insert_match_result
from util.match_api import fetch_api

from util.config import DB_NAME

def fetch_match_result(match_id):
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/fb/getMatchScoreV1.qry?matchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到赛果数据")
        return
    conn = get_conn(DB_NAME)
    try:
        value = feature_data.get('value', {})
        insert_match_result(conn, match_id, value.get('sectionsNos', []))
        print(f"已存储赛果: match_id={match_id}")
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_result.py <match_id>")
        return
    match_id = sys.argv[1]
    fetch_match_result(match_id)

if __name__ == "__main__":
    main()