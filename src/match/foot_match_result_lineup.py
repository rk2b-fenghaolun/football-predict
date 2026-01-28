import sys

from util.data_util import get_conn
from data.result_lineup import insert_lineup
from util.match_api import fetch_api

from util.config import DB_NAME

def fetch_match_result_analysis(match_id):
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/matchlive/getPlayerStatisV1.qry?gmMatchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到本场分析数据")
        return
    conn = get_conn(DB_NAME)
    try:
        value = feature_data.get('value', {})

        if not value:
            print("本场分析数据为空")
            return
        
        awayTeamFormation = value.get('awayTeamFormation', '')
        homeTeamFormation = value.get('homeTeamFormation', '')

        homeTeamId = value.get('homeTeamId', 0)
        homeTeamShortName = value.get('homeTeamShortName', '')
        awayTeamId = value.get('awayTeamId', 0)
        awayTeamShortName = value.get('awayTeamShortName', '')

        awayPlayerStats = value.get('awayPlayerStats', [])
        homePlayerStats = value.get('homePlayerStats', [])
        
        if homePlayerStats:
            starting_xi, substitutes = '', ''
            for homePlayer in homePlayerStats:
                playerId = homePlayer.get('personId', 0)
                isStarting = homePlayer.get('starterFlag', False)
                if isStarting:
                    starting_xi += f"{playerId},"
                else:
                    substitutes += f"{playerId},"

            insert_lineup(conn, match_id, 'home', homeTeamId, homeTeamShortName, homeTeamFormation, homePlayerStats, starting_xi, substitutes)


        if awayPlayerStats:
            starting_xi, substitutes = '', ''
            for awayPlayer in awayPlayerStats:
                playerId = awayPlayer.get('personId', 0)
                isStarting = awayPlayer.get('starterFlag', False)
                if isStarting:
                    starting_xi += f"{playerId},"
                else:
                    substitutes += f"{playerId},"

            insert_lineup(conn, match_id, 'away', awayTeamId, awayTeamShortName, awayTeamFormation, awayPlayerStats, starting_xi, substitutes)

        
        
        print(f"已存储本场分析: match_id={match_id}")
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_result_analysis.py <match_id>")
        return
    match_id = sys.argv[1]
    fetch_match_result_analysis(match_id)

if __name__ == "__main__":
    main()