import os
import sys
import pandas as pd
import numpy as np
import lightgbm as lgb

from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, classification_report

# 确保 src 可以被正确导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# =========================
# 配置区
# =========================

# 1. load data
from src.util.data_util import get_conn
from src.util.config import DB_NAME
from src.util.config import MODEL_DIR

VIEW_NAME = "vw_match_train_pre_level2"
RANDOM_STATE = 42

LABEL_NAMES = ["H", "D", "A"]

# =========================
# 特征定义
# =========================

LEVEL1_FEATURES = [
    # odds
    "odds_h_prob",
    "odds_d_prob",
    "odds_a_prob",

    # season strength
    "home_points",
    "away_points",
    "home_goal_diff",
    "away_goal_diff",

    "home_goals_for",
    "home_goals_against",
    "away_goals_for",
    "away_goals_against",

    "home_rank",
    "away_rank",

    # diffs
    "points_diff",
    "goal_diff_diff",
    "rank_diff",
    "home_goal_ratio",
]

FORM_FEATURES = [
    # recent form
    "home_win_rate_10",
    "home_draw_rate_10",
    "away_win_rate_10",
    "away_draw_rate_10",

    # goal rhythm
    "home_goal_avg",
    "home_concede_avg",
    "away_goal_avg",
    "away_concede_avg",

    # draw enhancers
    "goal_avg_diff",
    "draw_rate_diff",
]

FEATURES = LEVEL1_FEATURES + FORM_FEATURES

# =========================
# 数据加载
# =========================

def load_data():
    conn = get_conn(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM {VIEW_NAME}", conn)
    conn.close()

    # label
    label_map = {"H": 0, "D": 1, "A": 2}
    df["label"] = df["win_flag"].map(label_map)

    # 丢弃异常行
    df = df.dropna(subset=FEATURES + ["label"])

    return df


# =========================
# 训练 & 评估
# =========================

def train_and_evaluate(df):
    X = df[FEATURES]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=3,
        learning_rate=0.05,
        n_estimators=500,
        max_depth=6,
        num_leaves=31,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=RANDOM_STATE,
    )

    print("start fit ...")
    model.fit(X_train, y_train)
    print("end fit")

    y_prob = model.predict_proba(X_test)
    y_pred = np.argmax(y_prob, axis=1)

    print("\nLogLoss:", log_loss(y_test, y_prob))
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=LABEL_NAMES,
            digits=3
        )
    )

    return model


# =========================
# 主入口
# =========================

def main():
    df = load_data()
    print(f"Loaded samples: {len(df)}")
    model = train_and_evaluate(df)


if __name__ == "__main__":
    main()
