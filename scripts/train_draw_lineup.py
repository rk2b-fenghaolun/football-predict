import sys
import os
import joblib
import numpy as np
import pandas as pd

# 确保 src 可以被正确导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


# 1. load data
from src.util.data_util import get_conn
from src.util.config import DB_NAME
from src.util.config import MODEL_DIR

MODEL_PATH = MODEL_DIR + "/baseline_draw_lineup.pkl"


def load_data():
    conn = get_conn(DB_NAME)
    df = pd.read_sql(
        """
        SELECT
            win_flag,
            odds_h,
            odds_d,
            odds_a,
            odds_ha_gap,
            win_rate_gap,
            total_goal_avg,
            home_unavailable_cnt,
            away_unavailable_cnt,
            home_start_ratio_avg,
            away_start_ratio_avg,
            home_appearance_avg,
            away_appearance_avg
        FROM train_baseline_draw_lineup
        """,
        conn
    )
    conn.close()
    return df


def main():
    df = load_data().fillna(0)

    X = df.drop(columns=["win_flag"])
    y = df["win_flag"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            solver="lbfgs",
            max_iter=1500,
            class_weight={"H": 1.0, "D": 1.6, "A": 1.0}
        ))
    ])

    pipeline.fit(X_train, y_train)

    proba = pipeline.predict_proba(X_test)
    pred = pipeline.predict(X_test)

    print("LogLoss:", log_loss(y_test, proba))
    print(classification_report(y_test, pred))

    # 自动创建模型目录
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
