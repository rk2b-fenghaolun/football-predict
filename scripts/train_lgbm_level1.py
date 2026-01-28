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

MODEL_PATH = MODEL_DIR + "/lgb_pre_level1.pkl"

conn = get_conn(DB_NAME)

def load_data():
    conn = get_conn(DB_NAME)
    df = pd.read_sql("""
        SELECT
            match_id,
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


    label_map = {"H": 0, "D": 1, "A": 2}
    df["label"] = df["win_flag"].map(label_map)
    # 去除未映射的行，防止 y 含 NaN
    df = df.dropna(subset=["label"])

    le = LabelEncoder()

    X = df.drop(columns=["match_id", "win_flag", "label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
)


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

    joblib.dump(
        {"model": model, "label_encoder": le},
        MODEL_PATH
    )
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()