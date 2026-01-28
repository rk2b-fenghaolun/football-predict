import lightgbm as lgb
import pandas as pd
from sklearn.metrics import log_loss, classification_report
from src.features.feature_engineering import build_training_dataset
from src.util.config import DB_NAME
from src.util.config import MODEL_DIR
import os

# ======================
# 1. 构建训练数据
# ======================
df = build_training_dataset(DB_NAME)

df["match_date"] = pd.to_datetime(df["match_date"])
df = df.sort_values("match_date")

# ======================
# 2. 时间切分
# ======================
split_date = df["match_date"].quantile(0.8)

train_df = df[df["match_date"] < split_date]
valid_df = df[df["match_date"] >= split_date]

# ======================
# 3. 特征 / 标签
# ======================
DROP_COLS = ["label", "match_date"]

X_train = train_df.drop(columns=DROP_COLS)
y_train = train_df["label"]

X_valid = valid_df.drop(columns=DROP_COLS)
y_valid = valid_df["label"]

# ======================
# 4. 权重（赔率缺失降权）
# ======================
w_train = train_df.get("odds_available", 1.0)
w_valid = valid_df.get("odds_available", 1.0)

# ======================
# 5. Dataset
# ======================
lgb_train = lgb.Dataset(X_train, label=y_train, weight=w_train)
lgb_valid = lgb.Dataset(X_valid, label=y_valid, weight=w_valid)

# ======================
# 6. 参数
# ======================
params = {
    "objective": "multiclass",
    "num_class": 3,
    "learning_rate": 0.03,
    "num_leaves": 63,
    "min_data_in_leaf": 50,
    "metric": "multi_logloss",
    "verbosity": -1,
    "seed": 42,
}

# ======================
# 7. 训练
# ======================
model = lgb.train(
    params,
    lgb_train,
    num_boost_round=3000,
    valid_sets=[lgb_valid],
    callbacks=[lgb.early_stopping(200)]
)

# ======================
# 8. 评估
# ======================
proba = model.predict(X_valid)
print("LogLoss:", log_loss(y_valid, proba))
print(classification_report(y_valid, proba.argmax(axis=1)))

# ======================
# 9. 保存
# ======================
os.makedirs(MODEL_DIR, exist_ok=True)
model.save_model(os.path.join(MODEL_DIR, "lgbm_win_draw_loss.txt"))
