import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss, classification_report
import lightgbm as lgb

# 确保 src 可以被正确导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 1. load data
from src.util.data_util import get_conn
from src.util.config import DB_NAME
from src.util.config import MODEL_DIR
from src.util.config import LABEL_MAP

MODEL_PATH = MODEL_DIR + "/lgb_pre_level1.pkl"

conn = get_conn(DB_NAME)

def load_data():
    conn = get_conn(DB_NAME)
    df = pd.read_sql("""
        SELECT
            match_id,
            match_date,
            win_flag,

            -- ===== 赔率概率 =====
            odds_h_prob,
            odds_d_prob,
            odds_a_prob,

            -- ===== 赛季强弱差 =====
            home_points,
            away_points,
            home_goal_diff,
            away_goal_diff,

            (home_points - away_points) AS points_diff,
            (home_goal_diff - away_goal_diff) AS goal_diff_diff

        FROM vw_match_train_pre_level1
        WHERE win_flag IS NOT NULL
        """, conn)
    conn.close()
    return df

def main():
    df = load_data().fillna(0)


    df["label"] = df["win_flag"].map(LABEL_MAP)
    # 去除未映射的行，防止 y 含 NaN
    df = df.dropna(subset=["label"])

    # ===== 修正：基于时间切分验证集 (Time Series Split) =====
    # 1. 按照日期排序 (关键！必须在分离 X, y 之前排序)
    df = df.sort_values("match_date")
    
    # 2. 分离特征与标签
    X = df.drop(columns=["match_id", "win_flag", "label", "match_date"])
    y = df["label"]

    # 3. 简单按最后 20% 做验证（防止穿越）
    train_size = int(len(df) * 0.8)
    
    X_train = X.iloc[:train_size]
    y_train = y.iloc[:train_size]
    X_test = X.iloc[train_size:]
    y_test = y.iloc[train_size:]
    
    print(f"Train date range: {df.iloc[0]['match_date']} to {df.iloc[train_size-1]['match_date']}")
    print(f"Test date range: {df.iloc[train_size]['match_date']} to {df.iloc[-1]['match_date']}")

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=3,
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=1
    )

    print("start fit")
    model.fit(X_train, y_train)
    print("end fit")

    y_pred_prob = model.predict_proba(X_test)
    y_pred = np.argmax(y_pred_prob, axis=1)

    print("LogLoss:", log_loss(y_test, y_pred_prob))
    print(classification_report(
        y_test, y_pred,
        target_names=["H", "D", "A"],
        digits=3
    ))

    # le = LabelEncoder() # 移除未使用的变量

    joblib.dump(
        {"model": model, "label_map": LABEL_MAP},
        MODEL_PATH
    )
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()