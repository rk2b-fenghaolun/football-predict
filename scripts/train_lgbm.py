import os
import sys
import sqlite3
import joblib
import pandas as pd
import lightgbm as lgb

# 确保 src 可以被正确导入
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss, classification_report


# 1. load data
from src.util.data_util import get_conn
from src.util.config import DB_NAME
from src.util.config import MODEL_DIR
from src.util.config import LABEL_MAP

MODEL_PATH = MODEL_DIR + "/lgb_pre.pkl"



def load_data():
    conn = get_conn(DB_NAME)
    df = pd.read_sql("SELECT * FROM train_lgb_pre", conn)
    conn.close()
    return df


def main():
    df = load_data().fillna(0)

    X = df.drop(columns=["match_id", "win_flag"])
    y = df["win_flag"]

    # 使用统一配置的映射
    y_enc = y.map(LABEL_MAP)
    # 确保没有无法映射的值
    if y_enc.isnull().any():
        print(f"Warning: dropping {y_enc.isnull().sum()} rows with unknown labels")
        mask = y_enc.notnull()
        X = X[mask]
        y_enc = y_enc[mask]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc,
        test_size=0.25,
        random_state=42,
        stratify=y_enc
    )

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=3,
        learning_rate=0.03,
        n_estimators=800,
        max_depth=6,
        # Config LABEL_MAP: H:0, D:1, A:2
        class_weight={
            0: 1.0,  # H
            1: 1.6,  # D
            2: 1.0   # A
        },
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)
    pred = model.predict(X_test)

    print("LogLoss:", log_loss(y_test, proba))
    target_names = [k for k, v in sorted(LABEL_MAP.items(), key=lambda item: item[1])]
    print(
        classification_report(
            y_test,
            pred,
            target_names=target_names
        )
    )

    joblib.dump({"model": model, "label_map": LABEL_MAP}, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


    joblib.dump(
        {"model": model, "label_encoder": le},
        MODEL_PATH
    )
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
