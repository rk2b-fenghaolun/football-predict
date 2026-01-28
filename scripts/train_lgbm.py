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

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

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
        num_leaves=31,
        min_child_samples=40,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.5,
        reg_lambda=0.8,
        class_weight={
            0: 1.0,  # A
            1: 1.6,  # D
            2: 1.0   # H
        },
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)
    pred = model.predict(X_test)

    print("LogLoss:", log_loss(y_test, proba))
    print(
        classification_report(
            y_test,
            pred,
            target_names=le.classes_
        )
    )

    joblib.dump(
        {"model": model, "label_encoder": le},
        MODEL_PATH
    )
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
