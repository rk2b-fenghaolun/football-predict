# 数据库连接 & 通用工具（基础）
import sqlite3
import pandas as pd

# 建立数据库连接
def get_conn(db_path: str):
    return sqlite3.connect(db_path)

# 取多行记录
def query_df(conn, sql, params=None):
    return pd.read_sql_query(sql, conn, params=params or {})

# 取单行记录（自动为 SQL 添加 LIMIT 1，直接用 cursor 查询返回 dict）
def query_one(conn, sql, params=None):
    sql_strip = sql.strip().lower()
    # 如果没有 limit 关键字则自动加 limit 1
    if 'limit' not in sql_strip:
        if sql_strip.endswith(';'):
            sql = sql.rstrip(';') + ' limit 1;'
        else:
            sql = sql + ' limit 1'
    cursor = conn.cursor()
    cursor.execute(sql, params or {})
    row = cursor.fetchone()
    if row is None:
        return None
    # 如果是 sqlite3.Row 或 tuple，转 dict
    if hasattr(row, 'keys'):
        return dict(row)
    desc = [d[0] for d in cursor.description]
    return dict(zip(desc, row))

# 取多行记录(返回list[dict])
def query_list(conn, sql, params=None):
    cursor = conn.cursor()
    cursor.execute(sql, params or {})
    rows = cursor.fetchall()
    if not rows:
        return []
    
    # Check if row factory is used or just tuples
    if hasattr(rows[0], 'keys'):
        return [dict(row) for row in rows]
        
    desc = [d[0] for d in cursor.description]
    return [dict(zip(desc, row)) for row in rows]