# src/utils/config.py  全局配置
import os

# 字段名
DATE_COL = "match_date"
LABEL_COL = "label"

# 标签映射
LABEL_MAP = {"H": 0, "D": 1, "A": 2}

# 随机种子
RANDOM_STATE = 42

# 数据库配置
DB_NAME = 'E:\\VsCodeProjects\\sports-lottery-data\\sports_lottery.db'

# 模型保存路径，始终指向项目根目录下 models 文件夹

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
