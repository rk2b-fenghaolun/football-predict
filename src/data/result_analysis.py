# 插入最近战绩分析结果到 recent_form_analysis 表
def insert_analysis(conn, match_id, type_, team_id, stats_data, stats_tc, stats_tc_desc):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO football_match_result_analysis (
            match_id, type, team_id, stats_data, stats_tc, stats_tc_desc
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        match_id,
        type_,
        team_id,
        stats_data,
        stats_tc,
        stats_tc_desc
    ))
    conn.commit()
