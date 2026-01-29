import sys
import json

from util.data_util import get_conn
from data.event import insert_event
from match.foot_match_player import fetch_api

from util.config import DB_NAME

def get_match_team_ids(conn, match_id):
    cursor = conn.cursor()
    cursor.execute("SELECT home_team_id, away_team_id FROM football_match WHERE match_id = ?", (match_id,))
    row = cursor.fetchone()
    if row:
        return row[0], row[1]
    return 0, 0

def fetch_match_event(match_id):
    
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/fb/getMatchEventV1.qry?matchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到事件数据")
        return
    conn = get_conn(DB_NAME)
    try:
        home_team_id, away_team_id = get_match_team_ids(conn, match_id)

        value = feature_data.get('value', {})
        event_list = value.get('eventList', [])
        for event in event_list:
            event_type = event.get('eventCode', '')
            event_time = event.get('matchMinute', '')
            event_team = event.get('teamType', '')
            event_player = event.get('personEnName', '')
            
            team_id = 0
            if event_team == 'home':
                team_id = home_team_id
            elif event_team == 'away':
                team_id = away_team_id

            insert_event(conn, match_id, event_type, event_time, event_team, event_player, json.dumps(event, ensure_ascii=False), team_id)
        print(f"已保存 {len(event_list)} 条事件到 football_match_result_event")
    finally:
        conn.close()


def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_event.py <match_id>")
        return
    match_id = sys.argv[1]
    fetch_match_event(match_id)

if __name__ == "__main__":
    main()
