def insert_event(conn, match_id, event_type, event_time, event_team, event_player, event_json):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO football_match_result_event (
            match_id, event_type, event_time, event_team, event_player, event_json
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (match_id, event_type, event_time, event_team, event_player, event_json))
    conn.commit()