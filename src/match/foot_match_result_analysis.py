import sys

from util.data_util import get_conn
from data.result_analysis import insert_analysis
from util.match_api import fetch_api
from util.config import DB_NAME

def fetch_match_result_analysis(match_id):
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/matchlive/getTeamStatisV1.qry?gmMatchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print("未获取到本场分析数据")
        return
    conn = get_conn(DB_NAME)
    try:
        # 获取主客队ID
        team_row = conn.execute('SELECT home_team_id, away_team_id FROM football_match WHERE match_id=?', (match_id,)).fetchone()
        if not team_row:
            print("未找到比赛主客队ID")
            return
        home_team_id, away_team_id = team_row
        analysis_list = feature_data.get('value', {}).get('stats', [])
        if not analysis_list:
            print("本场分析数据为空")
            return
        for analysis in analysis_list:
            # 客队
            insert_analysis(conn, match_id, 'away', away_team_id, analysis.get('awayStatsData'), analysis.get('statsTc'), analysis.get('statsTcDesc'))
            # 主队
            insert_analysis(conn, match_id, 'home', home_team_id, analysis.get('homeStatsData'), analysis.get('statsTc'), analysis.get('statsTcDesc'))
        conn.commit()
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