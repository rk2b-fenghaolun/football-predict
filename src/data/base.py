import json

# 比赛基础信息（时间锚点来源）
from src.util.data_util import query_one

def extract_base(conn, match_id, match_date):
    sql = """
    SELECT
        match_date,
        league_id,
        home_team_id,
        away_team_id
    FROM football_match
    WHERE match_id = :match_id
    """
    row = query_one(conn, sql, {"match_id": match_id})
    if row is None:
        return {}

    return {
        "league_id": row["league_id"],
        "home_team_id": row["home_team_id"],
        "away_team_id": row["away_team_id"],
    }

def insert_match(conn, match_data):
    cursor = conn.cursor()
    # 先查找是否存在
    cursor.execute('SELECT 1 FROM football_match WHERE match_id=?', (match_data.get('matchId'),))
    exists = cursor.fetchone()
    if exists:
        # 存在则更新
        cursor.execute('''
            UPDATE football_match SET
                match_num=?, match_num_str=?, match_date=?, league_id=?, league_name=?, league_name_abbr=?, league_back_color=?,
                home_team=?, home_team_id=?, away_team=?, away_team_id=?, all_home_team=?, all_away_team=?, goal_line=?
            WHERE match_id=?
        ''', (
            match_data.get('matchNum'),
            match_data.get('matchNumStr', ''),
            match_data.get('matchDate', ''),
            match_data.get('leagueId'),
            match_data.get('leagueName'),
            match_data.get('leagueNameAbbr', ''),
            match_data.get('leagueBackColor', ''),
            match_data.get('homeTeam'),
            match_data.get('homeTeamId'),
            match_data.get('awayTeam'),
            match_data.get('awayTeamId'),
            match_data.get('allHomeTeam', match_data.get('homeTeam')),
            match_data.get('allAwayTeam', match_data.get('awayTeam')),
            match_data.get('goalLine', ''),
            match_data.get('matchId')
        ))
    else:
        # 不存在则插入
        cursor.execute('''
            INSERT INTO football_match (
                match_id, match_num, match_num_str, match_date, league_id, league_name, league_name_abbr, league_back_color,
                home_team, home_team_id, away_team, away_team_id, all_home_team, all_away_team, goal_line
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            match_data.get('matchId'),
            match_data.get('matchNum'),
            match_data.get('matchNumStr', ''),
            match_data.get('matchDate', ''),
            match_data.get('leagueId'),
            match_data.get('leagueName'),
            match_data.get('leagueNameAbbr', ''),
            match_data.get('leagueBackColor', ''),
            match_data.get('homeTeam'),
            match_data.get('homeTeamId'),
            match_data.get('awayTeam'),
            match_data.get('awayTeamId'),
            match_data.get('allHomeTeam', match_data.get('homeTeam')),
            match_data.get('allAwayTeam', match_data.get('awayTeam')),
            match_data.get('goalLine', '')
        ))
    conn.commit()

def insert_match_result(conn, match_id, sections_nos):
    home_score = away_score = None
    sections_no1 = sections_no999 = win_flag = ''
    if sections_nos:
        for sec in sections_nos:
            if sec.get('sectionNo') == 2:
                scores = sec.get('score', '').split(':')
                home_score = int(scores[0]) if len(scores) > 0 else None
                away_score = int(scores[1]) if len(scores) > 1 else None
                sections_no999 = sec.get('score', '')
            elif sec.get('sectionNo') == 1:
                sections_no1 = sec.get('score', '')
    if home_score is not None and away_score is not None:
        if home_score > away_score:
            win_flag = 'H'
        elif home_score == away_score:
            win_flag = 'D'
        else:
            win_flag = 'A'
    else:
        win_flag = ''
    cursor = conn.cursor()
    # 先查找是否存在
    cursor.execute('SELECT 1 FROM football_match_result WHERE match_id=?', (match_id,))
    exists = cursor.fetchone()
    if exists:
        # 存在则更新
        cursor.execute('''
            UPDATE football_match_result SET
                home_score=?, away_score=?, sections_no1=?, sections_no999=?, win_flag=?
            WHERE match_id=?
        ''', (
            home_score, away_score, sections_no1, sections_no999, win_flag, match_id
        ))
    else:
        # 不存在则插入
        cursor.execute('''
            INSERT INTO football_match_result (
                match_id, home_score, away_score, sections_no1, sections_no999, win_flag
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            match_id, home_score, away_score, sections_no1, sections_no999, win_flag
        ))
    conn.commit()
