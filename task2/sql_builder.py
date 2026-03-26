# task2/sql_builder.py (修改版 - 添加获取SQL的方法)
"""
SQL构建器
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from task2.db_utils import Database

class SQLBuilder:
    def __init__(self, db):
        self.db = db
        self.last_sql = None  # 存储最后生成的SQL
    
    def build_query(self, parsed):
        """构建SQL查询语句"""
        if not parsed['company'] or not parsed['field'] or not parsed['table']:
            self.last_sql = None
            return None
        
        company = parsed['company']
        field = parsed['field']
        table = parsed['table']
        time_cond = parsed.get('time')
        
        # 基础SELECT
        sql = f"SELECT [report_period], [{field}] FROM {table} WHERE [stock_abbr] = '{company}'"
        
        # 时间条件
        if time_cond:
            if time_cond == 'recent_years':
                sql += " AND [report_period] LIKE '%FY' ORDER BY [report_year] DESC"
                # 使用TOP限制（SQL Server语法）
                sql = sql.replace("SELECT", "SELECT TOP 3")
            elif time_cond.startswith('last_') and time_cond.endswith('_years'):
                n = int(time_cond.split('_')[1])
                sql += f" AND [report_period] LIKE '%FY' ORDER BY [report_year] DESC"
                sql = sql.replace("SELECT", f"SELECT TOP {n}")
            elif 'Q' in time_cond or 'FY' in time_cond:
                sql += f" AND [report_period] = '{time_cond}'"
            else:
                sql += f" AND [report_period] LIKE '{time_cond}%'"
        else:
            # 无时间，默认取最新一条
            sql += " ORDER BY [report_year] DESC, [report_period] DESC"
            sql = sql.replace("SELECT", "SELECT TOP 1")
        
        self.last_sql = sql
        return sql
    
    def get_last_sql(self):
        """获取最后生成的SQL语句"""
        return self.last_sql