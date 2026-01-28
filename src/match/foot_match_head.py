import sys
import json

from src.util.match_api import fetch_api
from src.util.data_util import get_conn
from src.data.base import update_match_datetime, all_match_ids

from src.util.config import DB_NAME

def fetch_match_datetime(match_id):
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchHeadV1.qry?source=web&sportteryMatchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到赛果数据")
        return
    conn = get_conn(DB_NAME)
    try:
        value = feature_data.get('value', {})
        update_match_datetime(conn, match_id, value.get('matchDateTime'))
        print(f"已存储赛果: match_id={match_id}")
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        # 未传参数时自动从数据库获取所有match_id
        print("未指定match_id，自动从数据库获取所有比赛...")
        match_ids = all_match_ids(get_conn(DB_NAME))
    else:
        match_ids = sys.argv[1:]
        
    for match_id in match_ids:
        fetch_match_datetime(match_id)

if __name__ == "__main__":
    main()