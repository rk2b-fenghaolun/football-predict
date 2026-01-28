# 伤停情况
from ..util.data_util import query_df

def extract_injury(conn, match_id):
    df = query_df(conn, """
        SELECT team_id, injury_flag, suspension_flag, startedMatchCnt
        FROM football_match_player
        WHERE match_id = :match_id
    """, {"match_id": match_id})

    if df.empty:
        return {}

    home = df[df["team_id"] == "home"]
    away = df[df["team_id"] == "away"]

    return {
        "injury_cnt_diff":
            home["injury_flag"].sum() - away["injury_flag"].sum(),
        "suspension_cnt_diff":
            home["suspension_flag"].sum() - away["suspension_flag"].sum(),
    }

def insert_player(
    conn, match_id, type, player_id, player_name, position,
    appearanceCnt, startedMatchCnt, substituteMatchCnt,
    goalCnt, goalAvgCnt, goalProbability,
    assistCnt, assistAvgCnt, assistProbability,
    goals, assists, injury_flag, suspension_flag
):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO football_match_preview_player (
            match_id, type, player_id, player_name, position,
            appearanceCnt, startedMatchCnt, substituteMatchCnt,
            goalCnt, goalAvgCnt, goalProbability,
            assistCnt, assistAvgCnt, assistProbability,
            goals, assists, injury_flag, suspension_flag
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        match_id, type, player_id, player_name, position,
        appearanceCnt, startedMatchCnt, substituteMatchCnt,
        goalCnt, goalAvgCnt, goalProbability,
        assistCnt, assistAvgCnt, assistProbability,
        goals, assists, injury_flag, suspension_flag
    ))
    conn.commit()


def parse_and_insert_players(conn, match_id, type, player_list):
    for p in player_list:
        insert_player(
            conn,
            match_id,
            type,
            p.get('personId', p.get('playerId', '')),
            p.get('personName', p.get('playerName', '')),
            p.get('playerPositionDesc', ''),
            p.get('appearanceCnt', 0),
            p.get('startedMatchCnt', 0),
            p.get('substituteMatchCnt', 0),
            p.get('goalCnt', 0),
            p.get('goalAvgCnt', 0.0),
            p.get('goalProbability', 0.0),
            p.get('assistCnt', 0),
            p.get('assistAvgCnt', 0.0),
            p.get('assistProbability', 0.0),
            p.get('goals', 0),
            p.get('assists', 0),
            p.get('injuryFlag', 0),
            p.get('suspensionFlag', 0)
        )

def parse_and_insert_players_with_injury(conn, match_id, type, player_list):
        for p in player_list:
            pid = p.get('personId', p.get('playerId', ''))
            insert_player(
                conn,
                match_id,
                type,
                pid,
                p.get('personName', p.get('playerName', '')),
                p.get('playerPositionDesc', ''),
                p.get('appearanceCnt', 0),
                p.get('startedMatchCnt', 0),
                p.get('substituteMatchCnt', 0),
                p.get('goalCnt', 0),
                p.get('goalAvgCnt', 0.0),
                p.get('goalProbability', 0.0),
                p.get('assistCnt', 0),
                p.get('assistAvgCnt', 0.0),
                p.get('assistProbability', 0.0),
                p.get('goals', 0),
                p.get('assists', 0),
                p.get('injuryFlag', 0),
                p.get('suspensionFlag', 0)
            )
