# football-predict-ai

## 项目简介

football-predict-ai 是一个用于足球比赛结果预测的机器学习项目，基于 LightGBM 多分类模型，结合丰富的比赛、赔率、排名、伤病等特征，自动化完成数据处理、特征工程、模型训练与评估。

---

## 目录结构

```
football-predict-ai/
├── main.py                  # 项目入口
├── pyproject.toml           # Python 项目依赖配置
├── README.md                # 项目说明文档
├── models/                  # 训练好的模型保存目录
├── scripts/
│   └── train_lgbm.py        # LightGBM 训练脚本
├── src/
│   ├── data/
│   │   ├── data.py          # 数据库通用操作
│   │   ├── data_loader.py   # 数据库读取接口
│   │   └── ...              # 其他数据处理模块
│   ├── features/
│   │   └── feature_engineering.py # 特征工程与训练集构建
│   └── util/
│       └── config.py        # 全局配置
```

---

## 环境依赖

- Python 3.10/3.11（推荐，3.13 可能不兼容部分依赖）
- pandas
- scikit-learn
- lightgbm

安装依赖：
```bash
uv pip install -r requirements.txt
```

---

## 数据准备

1. 准备 SQLite 数据库文件 `sports_lottery.db`，并放置于项目根目录或 config.py 配置路径下。
2. 数据库需包含如下主要表结构：
   - `football_match`：比赛基础信息
   - `football_match_result`：比赛结果
   - 其他特征相关表（赔率、排名、伤病等）

---

## 快速上手

1. 配置全局参数（如有需要可修改 src/util/config.py）：
   - 数据库文件名、模型保存路径等

2. 运行模型训练脚本：
```bash
python scripts/train_lgbm.py
```

3. 训练完成后，模型文件将保存在 models/ 目录下。

---

## 主要功能说明

- **特征工程**：自动从数据库提取比赛、赔率、排名、伤病等多维特征，构建统一训练集。
- **模型训练**：基于 LightGBM 多分类，自动完成时间切分、特征选择、样本权重、训练与早停。
- **评估与保存**：输出验证集 logloss、分类报告，并保存最佳模型。

---

## 参考命令

- 安装依赖：
  ```bash
  uv pip install -r requirements.txt
  ```
- 训练模型：
  ```bash
  python scripts/train_lgbm.py
  ```

---

## 常见问题

- pandas/scikit-learn 安装失败：请确认 Python 版本为 3.10/3.11，或更换 pip 源。
- 数据库缺表或字段：请根据 feature_engineering.py 和数据表结构补充数据。

---

## 联系方式

如有问题或建议，欢迎 issue 或联系作者。
