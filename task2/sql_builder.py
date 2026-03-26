# task2/sql_builder.py (修复版 - 去重和正确排序)
"""
SQL构建器 - 修复数据重复问题
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from task2.db_utils import Database

class SQLBuilder:
    def __init__(self, db):
        self.db = db
        self.last_sql = None
    
    def build_query(self, parsed):
        """构建SQL查询语句"""
        if not parsed['company'] or not parsed['field'] or not parsed['table']:
            self.last_sql = None
            return None
        
        company = parsed['company']
        field = parsed['field']
        table = parsed['table']
        time_cond = parsed.get('time')
        
        # 基础SELECT - 使用DISTINCT去重
        sql = f"SELECT DISTINCT [report_period], [report_year], [{field}] FROM {table} WHERE [stock_abbr] = '{company}'"
        
        # 时间条件
        if time_cond:
            if time_cond == 'recent_years':
                # 获取最近3年的年度数据
                sql += " AND [report_period] LIKE '%FY'"
                sql += " ORDER BY [report_year] DESC"
                sql = f"SELECT TOP 3 [report_period], [report_year], [{field}] FROM ({sql}) AS t"
            elif time_cond.startswith('last_') and time_cond.endswith('_years'):
                n = int(time_cond.split('_')[1])
                sql += f" AND [report_period] LIKE '%FY'"
                sql += f" ORDER BY [report_year] DESC"
                sql = f"SELECT TOP {n} [report_period], [report_year], [{field}] FROM ({sql}) AS t"
            elif 'Q' in time_cond:
                # 季度数据
                sql += f" AND [report_period] = '{time_cond}'"
                sql += " ORDER BY [report_year] DESC"
            elif 'FY' in time_cond:
                # 年度数据
                sql += f" AND [report_period] = '{time_cond}'"
            else:
                # 年份模糊匹配
                sql += f" AND [report_period] LIKE '{time_cond}%'"
                sql += " ORDER BY [report_year] DESC, [report_period] DESC"
        else:
            # 无时间，默认取最新一条
            sql += " ORDER BY [report_year] DESC, [report_period] DESC"
            sql = f"SELECT TOP 1 [report_period], [report_year], [{field}] FROM ({sql}) AS t"
        
        # 确保按照年份排序
        if 'ORDER BY' not in sql and 'TOP' not in sql:
            sql += " ORDER BY [report_year] ASC, [report_period] ASC"
        
        self.last_sql = sql
        return sql
    
    def get_last_sql(self):
        """获取最后生成的SQL语句"""
        return self.last_sql