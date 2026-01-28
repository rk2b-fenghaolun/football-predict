import sys

from util.data_util import get_conn
from data.feature import insert_feature
from data.future_matches import insert_future_matches
from data.goal_avg import insert_goal_avg
from data.rank import insert_tables
from match.foot_match_player import fetch_api

from util.config import DB_NAME

# feature 特征分析 goal_avg 场均进球 loss_goal_avg 场均失球 
def insert_future(match_id):
    # feature 特征分析
    feature_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchFeatureV1.qry?termLimits=10&sportteryMatchId={match_id}"
    feature_data = fetch_api(feature_url)
    if not feature_data:
        print(f"跳过 match_id={match_id} 的 feature 数据采集（无数据或异常）")
        return
    conn = get_conn(DB_NAME)
    try:
        insert_feature(match_id, 'eachHomeAway', feature_data.get('value', {}).get('eachHomeAway', {}))
        insert_feature(match_id, 'eachSameHomeAway', feature_data.get('value', {}).get('eachSameHomeAway', {}))
        insert_feature(match_id, 'sameHomeAway', feature_data.get('value', {}).get('sameHomeAway', {}))
        insert_feature(match_id, 'lastAway', feature_data.get('value', {}).get('last', {}))

        # goal_avg 场均进球 loss_goal_avg 场均失球 
        goal_avg = feature_data.get('value', {}).get('goalAvg', {})
        loss_goal_avg = feature_data.get('value', {}).get('lossGoalAvg', {})
        insert_goal_avg(match_id, goal_avg, loss_goal_avg)
    finally:
        conn.close()

# tables 积分榜
def insert_tables(match_id):
    # tables 积分榜
    tables_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getMatchTablesV2.qry?gmMatchId={match_id}"
    tables_data = fetch_api(tables_url)
    if not tables_data:
        print(f"跳过 match_id={match_id} 的 feature 数据采集（无数据或异常）")
        return
    conn = get_conn(DB_NAME)
    try:
        away_tables = tables_data.get('value', {}).get('awayTables', {}).get('total', {})
        if not away_tables:
            print(f"跳过 match_id={match_id} 的 tables 数据采集（无数据）")
            return
        insert_tables(conn,match_id, 'away', away_tables)

        home_tables = tables_data.get('value', {}).get('homeTables', {}).get('total', {})
        if not home_tables:
            print(f"跳过 match_id={match_id} 的 tables 数据采集（无数据）")
            return
        insert_tables(conn,match_id, 'home', home_tables)
    finally:
        conn.close()

# future 未来赛事
def insert_future_matches(match_id):
    future_url = f"https://webapi.sporttery.cn/gateway/uniform/football/getFutureMatchesV1.qry?sportteryMatchId={match_id}&termLimits=3"
    future_data = fetch_api(future_url)
    if not future_data:
        print(f"跳过 match_id={match_id} 的 未来赛事")
        return
    conn = get_conn(DB_NAME)
    try:
        away_future_list = future_data.get('value', {}).get('away', {}).get('matchList', [])
        if not away_future_list:
            print(f"跳过 match_id={match_id} 的 未来赛事")
            return
        insert_future_matches(conn,match_id, 'away', away_future_list)
        home_future_list = future_data.get('value', {}).get('home', {}).get('matchList', [])
        if not home_future_list:
            print(f"跳过 match_id={match_id} 的 未来赛事")
            return
        insert_future_matches(conn,match_id, 'home', home_future_list)
    finally:
        conn.close()
    
def main():
    if len(sys.argv) < 2:
        print("用法: python foot_match_event.py <match_id>")
        return
    match_id = sys.argv[1]
    insert_future(match_id)
    insert_tables(match_id)
    insert_future_matches(match_id)

if __name__ == "__main__":
    main()
