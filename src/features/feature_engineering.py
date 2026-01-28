# feature_engineering/build_features.py
from util.data_util import get_conn, query_one, query_df
from data.base import extract_base
from data.odds import extract_odds
from data.rank import extract_rank_table
from data.recent import extract_recent_form
from data.h2h import extract_h2h
from data.goal_avg import extract_goal_avg
from data.injury import extract_injury
from .schema import FEATURE_SCHEMA

from ..util.config import LABEL_MAP
import pandas as pd

# 将特征对齐到统一的 schema
def align_features(raw: dict):
    return {k: raw.get(k, 0) for k in FEATURE_SCHEMA}

# 构建指定比赛的特征
def build_features(db_path, match_id):
    conn = get_conn(db_path)

    match_date = query_one(
        conn,
        "SELECT match_date FROM football_match WHERE match_id = :match_id",
        {"match_id": match_id}
    )["match_date"]

    row = {}
    row.update(extract_base(conn, match_id, match_date))
    row.update(extract_odds(conn, match_id, match_date))
    row.update(extract_rank_table(conn, match_id, match_date))
    row.update(extract_recent_form(conn, match_id, match_date))
    row.update(extract_h2h(conn, match_id))
    row.update(extract_goal_avg(conn, match_id))
    row.update(extract_injury(conn, match_id))

    conn.close()
    return align_features(row)

# 构建整个训练数据集
def build_training_dataset(db_path):
    conn = get_conn(db_path)

    # 1. 取所有有结果的比赛
    matches = query_df(conn, """
        SELECT
            m.match_id,
            m.match_date,
            r.win_flag
        FROM football_match m
        JOIN football_match_result r
          ON m.match_id = r.match_id
        ORDER BY m.match_date
    """)

    conn.close()

    rows = []
    failed = 0

    for _, row in matches.iterrows():
        match_id = row["match_id"]

        try:
            feats = build_features(db_path, match_id)
            feats["label"] = LABEL_MAP[row["win_flag"]]
            feats["match_date"] = row["match_date"]
            rows.append(feats)
        except Exception as e:
            failed += 1
            continue

    df = pd.DataFrame(rows)

    print(f"成功生成样本: {len(df)}")
    print(f"失败样本数: {failed}")

    return df
