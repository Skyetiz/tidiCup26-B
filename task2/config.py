# task2/config.py (简化版)
"""
配置文件 - 所有配置集中管理
"""
import os
from pathlib import Path

# 项目根目录（tidiCup26-B）
PROJECT_ROOT = Path(__file__).parent.parent

# 数据库配置
DATABASE_CONFIG = {
    'server': r'127.0.0.1,1433',  # 如果是本地默认实例，用 'localhost' 或 '127.0.0.1'
    'database': 'Teddy',
    'use_windows_auth': True,  # True=Windows认证，False=SQL Server账号密码认证
    'username': 'sa',           # 仅use_windows_auth=False时需要
    'password': 'your_password'  # 仅use_windows_auth=False时需要
}

# 文件路径配置
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_CSV_DIR = PROJECT_ROOT / 'output_csv'
RESULT_DIR = PROJECT_ROOT / 'result'

# 问题文件路径
QUESTION_FILES = {
    'task2': PROJECT_ROOT / '附件4：问题汇总.xlsx',
    'task3': PROJECT_ROOT / '附件6：问题汇总.xlsx'
}

# 表名配置
TABLE_NAMES = {
    'income': 'income_sheet',
    'balance': 'balance_sheet',
    'cash_flow': 'cash_flow_sheet',
    'core_performance': 'core_performance_indicators_sheet'
}

# 创建必要的目录
for dir_path in [RESULT_DIR, DATA_DIR, OUTPUT_CSV_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 可选：打印配置（注释掉以减少输出）
# print(f"📁 项目根目录: {PROJECT_ROOT}")
# print(f"📁 结果目录: {RESULT_DIR}")