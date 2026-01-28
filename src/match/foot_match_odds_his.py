import sys
import json

from util.data_util import get_conn
from match.foot_match_player import fetch_api
from src.data.odds import insert_odds_history

from util.config import DB_NAME

# 获取历史赔率
def fetch_odds_history(match_id):
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getFixedBonusV1.qry?clientCode=3001&matchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到事件数据")
        return
    conn = get_conn(DB_NAME)
    try:
        value = feature_data.get('value', {})
        for odds_type in ['hadList', 'hhadList', 'crsList', 'hafuList', 'ttgList']:
            odds_list = value.get('oddsHistory', {}).get(odds_type, [])
            for item in odds_list:
                update_date = item.get('updateDate', '')
                update_time = item.get('updateTime', '')
                insert_odds_history(match_id, update_date, update_time, odds_type, json.dumps(item, ensure_ascii=False))
            print(f"已保存 {len(odds_list)} 条事件到 football_match_result_event")
    finally:
        conn.close()    


def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_odds_his.py <match_id>")
        return
    match_id = sys.argv[1]
    fetch_odds_history(match_id)

if __name__ == "__main__":
    main()
