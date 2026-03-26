"""
✅ 适配task14完整版：导入全部财务字段到SQL Server
功能：把 output_csv 里的完整财务CSV → 写入 SQL Server（字段100%对齐）
"""
import pandas as pd
import pyodbc
import os
import numpy as np

# ===================== 数据库配置（根据自己环境修改） =====================
SERVER = r'127.0.0.1,1433'
DATABASE = 'Teddy'
USE_WINDOWS_AUTH = True  # True=Windows认证，False=SQL Server账号密码认证
SQL_ACCOUNT = 'sa'       # 仅USE_WINDOWS_AUTH=False时需要
SQL_PASSWORD = '你的密码' # 仅USE_WINDOWS_AUTH=False时需要

# ===================== 连接字符串 =====================
if USE_WINDOWS_AUTH:
    conn_str = f"DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes"
else:
    conn_str = f"DRIVER={{SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={SQL_ACCOUNT};PWD={SQL_PASSWORD}"

# ===================== 表结构配置（100%对齐task14的TABLE_CONFIG） =====================
TABLES = {
    "income_sheet": {
        "columns": [
            'serial_number', 'stock_code', 'stock_abbr', 'report_period', 'report_year',
            'net_profit', 'net_profit_yoy_growth', 'other_income', 'total_operating_revenue',
            'operating_revenue_yoy_growth', 'operating_expense_cost_of_sales', 'operating_expense_selling_expenses',
            'operating_expense_administrative_expenses', 'operating_expense_financial_expenses',
            'operating_expense_rnd_expenses', 'operating_expense_taxes_and_surcharges', 'total_operating_expenses',
            'operating_profit', 'total_profit', 'asset_impairment_loss', 'credit_impairment_loss'
        ],
        "types": [
            "INT", "NVARCHAR(50)", "NVARCHAR(50)", "NVARCHAR(20)", "INT",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)"
        ]
    },
    "balance_sheet": {
        "columns": [
            'serial_number', 'stock_code', 'stock_abbr', 'report_period', 'report_year',
            'asset_cash_and_cash_equivalents', 'asset_accounts_receivable', 'asset_inventory',
            'asset_trading_financial_assets', 'asset_construction_in_progress', 'asset_total_assets',
            'asset_total_assets_yoy_growth', 'liability_accounts_payable', 'liability_advance_from_customers',
            'liability_total_liabilities', 'liability_total_liabilities_yoy_growth', 'liability_contract_liabilities',
            'liability_short_term_loans', 'asset_liability_ratio', 'equity_unappropriated_profit', 'equity_total_equity'
        ],
        "types": [
            "INT", "NVARCHAR(50)", "NVARCHAR(50)", "NVARCHAR(20)", "INT",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)"
        ]
    },
    "cash_flow_sheet": {
        "columns": [
            'serial_number', 'stock_code', 'stock_abbr', 'report_period', 'report_year',
            'net_cash_flow', 'net_cash_flow_yoy_growth', 'operating_cf_net_amount',
            'operating_cf_ratio_of_net_cf', 'operating_cf_cash_from_sales', 'investing_cf_net_amount',
            'investing_cf_ratio_of_net_cf', 'investing_cf_cash_for_investments',
            'investing_cf_cash_from_investment_recovery', 'financing_cf_cash_from_borrowing',
            'financing_cf_cash_for_debt_repayment', 'financing_cf_net_amount', 'financing_cf_ratio_of_net_cf'
        ],
        "types": [
            "INT", "NVARCHAR(50)", "NVARCHAR(50)", "NVARCHAR(20)", "INT",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)"
        ]
    },
    "core_performance_indicators_sheet": {  # 表名和task14的CSV完全一致
        "columns": [
            'serial_number', 'stock_code', 'stock_abbr', 'report_period', 'report_year',
            'eps', 'total_operating_revenue', 'operating_revenue_yoy_growth', 'operating_revenue_qoq_growth',
            'net_profit_10k_yuan', 'net_profit_yoy_growth', 'net_profit_qoq_growth',
            'net_asset_per_share', 'roe', 'operating_cf_per_share', 'net_profit_excl_non_recurring',
            'net_profit_excl_non_recurring_yoy', 'gross_profit_margin', 'net_profit_margin',
            'roe_weighted_excl_non_recurring'
        ],
        "types": [
            "INT", "NVARCHAR(50)", "NVARCHAR(50)", "NVARCHAR(20)", "INT",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)", "DECIMAL(18,4)", "DECIMAL(18,4)",
            "DECIMAL(18,4)"
        ]
    }
}

# ===================== 工具：创建表（兼容重复执行） =====================
def create_table(cursor, table_name, cols, types):
    col_def = []
    for c, t in zip(cols, types):
        # 字段名加中括号，避免和SQL关键字冲突
        col_def.append(f"[{c}] {t}")

    # 先删后建（测试环境用，生产环境可改为ALTER）
    sql = f"""
    IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};
    CREATE TABLE {table_name} ({', '.join(col_def)});
    """
    try:
        cursor.execute(sql)
        print(f"✅ 表 {table_name} 创建/重建成功")
    except Exception as e:
        print(f"❌ 表 {table_name} 创建失败：{e}")
        raise

# ===================== 工具：插入数据（处理空值+大批量插入优化） =====================
def insert_data(cursor, table_name, df):
    # 只取配置的字段（避免CSV多余字段导致报错）
    cols = TABLES[table_name]["columns"]
    df = df[cols].copy()

    # 关键修复：空值/NaN替换为None（SQL Server识别的空值）
    df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

    # 批量插入（比逐行插快10倍+）
    batch_size = 100  # 可根据数据量调整
    total_rows = len(df)
    inserted = 0

    while inserted < total_rows:
        batch_df = df.iloc[inserted:inserted+batch_size]
        batch_vals = [tuple(row.values) for _, row in batch_df.iterrows()]

        # 生成占位符
        placeholders = ",".join(["?"] * len(cols))
        sql = f"INSERT INTO {table_name} ({', '.join([f'[{c}]' for c in cols])}) VALUES ({placeholders})"

        try:
            cursor.executemany(sql, batch_vals)
            inserted += len(batch_df)
            print(f"📥 已插入 {inserted}/{total_rows} 行")
        except Exception as e:
            print(f"❌ 批量插入失败（行{inserted}~{inserted+batch_size}）：{e}")
            # 兜底逐行插入（定位错误行）
            for idx, row in batch_df.iterrows():
                try:
                    cursor.execute(sql, tuple(row.values))
                    inserted += 1
                except Exception as e2:
                    print(f"❌ 单行插入失败（行{idx}）：{e2} | 数据：{tuple(row.values)}")
                    continue

# ===================== 主程序 =====================
if __name__ == "__main__":
    print("="*60)
    print("✅ 开始导入完整财务CSV → SQL Server（适配task14）")
    print("="*60)

    conn = None
    cursor = None
    try:
        # 建立数据库连接（设置自动提交=False，手动commit）
        conn = pyodbc.connect(conn_str, autocommit=False)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")

        # 遍历output_csv文件夹下的所有CSV
        csv_dir = "output_csv"
        if not os.path.exists(csv_dir):
            print(f"❌ 未找到CSV文件夹：{csv_dir}（请先运行task14生成CSV）")
            exit(1)

        for fname in os.listdir(csv_dir):
            if not fname.endswith(".csv"):
                continue

            # 匹配表名（CSV文件名=表名）
            table_name = fname.replace(".csv", "")
            if table_name not in TABLES:
                print(f"⚠️ 跳过未配置的表：{table_name}（请在TABLES中添加配置）")
                continue

            csv_path = os.path.join(csv_dir, fname)
            print(f"\n📄 处理文件：{fname} → 表：{table_name}")

            # 读取CSV（兼容UTF-8/GBK编码）
            try:
                df = pd.read_csv(csv_path, encoding="utf-8-sig")
            except:
                df = pd.read_csv(csv_path, encoding="gbk")
            print(f"📊 读取到 {len(df)} 行，{len(df.columns)} 列")

            # 创建表 + 插入数据
            create_table(cursor, table_name, TABLES[table_name]["columns"], TABLES[table_name]["types"])
            insert_data(cursor, table_name, df)

            # 提交事务
            conn.commit()
            print(f"✅ {table_name} 导入完成，已提交事务")

        print("\n🎉 全部财务数据导入成功！")
        print(f"👉 数据库：{DATABASE} | 包含表：{list(TABLES.keys())}")

    except Exception as e:
        print(f"\n❌ 程序执行失败：{e}")
        if conn:
            conn.rollback()  # 出错回滚
        exit(1)
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("\n🔌 数据库连接已关闭")