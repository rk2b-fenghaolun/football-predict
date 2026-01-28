# 特征分析
from ..util.data_util import query_df

def insert_future_matches(conn, match_id, type, future_list):
    cursor = conn.cursor()
    for item in future_list:
        cursor.execute('''
            INSERT INTO football_match_preview_future_matches (
                match_id, type, matchDateTime, tournamentId, tournamentShortName, seasonId, gameweek,
                awayTeamId, awayTeamShortName, homeTeamId, homeTeamShortName
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_id,
            type,
            item.get('matchDateTime', ''),
            item.get('tournamentId', 0),
            item.get('tournamentShortName', ''),
            item.get('seasonId', 0),
            item.get('gameweek', 0),
            item.get('awayTeamId', 0),
            item.get('awayTeamShortName', ''),
            item.get('homeTeamId', 0),
            item.get('homeTeamShortName', '')
        ))
    conn.commit()
