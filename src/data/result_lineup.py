# 插入最近战绩分析结果到 recent_form_analysis 表
def insert_lineup(conn, match_id, team_type, team_id, team_name, formation, player_positions_json, starting_xi, substitutes):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO football_match_result_lineup (
            match_id, team_type, team_id, team_name, formation, player_positions_json, starting_xi, substitutes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        match_id,
        team_type,
        team_id,
        team_name,
        formation,
        player_positions_json,
        starting_xi,
        substitutes
    ))
    conn.commit()
