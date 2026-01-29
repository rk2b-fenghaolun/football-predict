def insert_event(conn, match_id, event_type, event_time, event_team, event_player, event_json, team_id=None):
    cursor = conn.cursor()
    # 动态构建 SQL，兼容可能没有 team_id 列的情况（虽然此时应已迁移）
    # 但为了简化，假设此时已有 team_id 列
    try:
        cursor.execute('''
            INSERT INTO football_match_result_event (
                match_id, event_type, event_time, event_team, event_player, event_json, team_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, event_type, event_time, event_team, event_player, event_json, team_id))
        conn.commit()
    except Exception as e:
        # 如果出错，可能是没有 team_id 列，降级尝试旧的插入方式?
        # 或者直接报错。为了稳健性，这里可以捕获并重试旧格式，
        # 但既然我们正在进行 schema 变更，应该强制 schema 匹配。
        print(f"插入事件失败: {e}")
        # 也可以选择 raise 抛出
