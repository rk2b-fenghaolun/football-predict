import sys

from util.data_util import get_conn
from data.injury import parse_and_insert_players
from data.injury import parse_and_insert_players_with_injury
from util.match_api import fetch_api

from util.config import DB_NAME

# 采集球员信息
def insert_players_by_match_id(match_id):
    # 采集球员信息
    player_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchPlayerV1.qry?sportteryMatchId={match_id}&termLimits=100"
    player_data = fetch_api(player_url)
    
    if not player_data:
        print("未获取到球员数据")
        return
    away_player_list = player_data.get('value', {}).get('away', {}).get('playerList', [])
    home_player_list = player_data.get('value', {}).get('home', {}).get('playerList', [])

    conn = get_conn(DB_NAME)
    try:
        if away_player_list:
            parse_and_insert_players(conn, match_id, 'away', away_player_list)
            print(f"已存客队球员信息: match_id={match_id}")
        if home_player_list:
            parse_and_insert_players(conn, match_id, 'home', home_player_list)
            print(f"已存主队球员信息: match_id={match_id}")
    finally:
        conn.close()
    
# 采集伤停信息
def insert_injury_by_match_id(match_id):
    # 采集伤停信息
    injury_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getInjurySuspensionV1.qry?sportteryMatchId={match_id}"
    injury_data = fetch_api(injury_url)
    
    if not injury_data:
        print("未获取到伤停数据")
        return
    away_injury_list = injury_data.get('value', {}).get('away', {}).get('injuriesAndSuspensionsList', [])
    home_injury_list = injury_data.get('value', {}).get('home', {}).get('injuriesAndSuspensionsList', [])

    conn = get_conn(DB_NAME)
    try:
        if away_injury_list:
            parse_and_insert_players_with_injury(conn, match_id, 'away', away_injury_list)
            print(f"已存客队伤停信息: match_id={match_id}")
        if home_injury_list:
            parse_and_insert_players_with_injury(conn, match_id, 'home', home_injury_list)
            print(f"已存主队伤停信息: match_id={match_id}")
    finally:
        conn.close()    
    
    
def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_event.py <match_id>")
        return
    match_id = sys.argv[1]
    insert_players_by_match_id(match_id)
    insert_injury_by_match_id(match_id)

if __name__ == "__main__":
    main()