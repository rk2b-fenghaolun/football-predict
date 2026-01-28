import sys
import json

from src.util.match_api import fetch_api
from src.util.data_util import get_conn
from src.data.base import insert_match

from src.util.config import DB_NAME

# 采集足球比赛数据
def fetch_matches():
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry?channel=c"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到事件数据")
        return
    conn = get_conn(DB_NAME)
    try:
        match_info_list = feature_data.get("value", {}).get("matchInfoList", [])
        for match_info in match_info_list:
            for sub_match in match_info.get("subMatchList", []):
                match_data = {
                    "matchId": sub_match.get("matchId"),
                    "matchNum": sub_match.get("matchNum"),
                    "matchNumStr": sub_match.get("matchNumStr"),
                    "matchDate": sub_match.get("matchDate", ""),
                    "leagueId": sub_match.get("leagueId"),
                    "leagueName": sub_match.get("leagueAllName") or sub_match.get("leagueName"),
                    "leagueNameAbbr": sub_match.get("leagueAbbName") or "",
                    "leagueBackColor": sub_match.get("backColor") or "",
                    "homeTeam": sub_match.get("homeTeamAbbName") or sub_match.get("homeTeam"),
                    "homeTeamId": sub_match.get("homeTeamId"),
                    "awayTeam": sub_match.get("awayTeamAbbName") or sub_match.get("awayTeam"),
                    "awayTeamId": sub_match.get("awayTeamId"),
                    "allHomeTeam": sub_match.get("homeTeamAllName") or sub_match.get("homeTeam"),
                    "allAwayTeam": sub_match.get("awayTeamAllName") or sub_match.get("awayTeam"),
                    "goalLine": sub_match.get("hhad", {}).get("goalLine", "")
                }                    
                insert_match(conn, match_data)
            print(f"获取到 {len(match_info_list)} 场比赛")
    finally:
        conn.close()

if __name__ == "__main__":
    fetch_matches()