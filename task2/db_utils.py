# task2/db_utils.py (最终修复版)
"""
数据库工具类
"""
import pyodbc
import pandas as pd
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from task2.config import DATABASE_CONFIG

class Database:
    def __init__(self):
        self.conn = None
        self.table_exists_cache = {}
        self.connect()
    
    def _build_connection_string(self):
        """构建数据库连接字符串"""
        server = DATABASE_CONFIG['server']
        database = DATABASE_CONFIG['database']
        
        if DATABASE_CONFIG['use_windows_auth']:
            # Windows认证
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'
        else:
            # SQL Server认证
            username = DATABASE_CONFIG['username']
            password = DATABASE_CONFIG['password']
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        
        return conn_str
    
    def connect(self):
        """建立数据库连接"""
        try:
            conn_str = self._build_connection_string()
            self.conn = pyodbc.connect(conn_str, autocommit=False)
            print(f"✅ 数据库连接成功: {DATABASE_CONFIG['database']}")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def query(self, sql):
        """执行查询并返回DataFrame"""
        try:
            return pd.read_sql(sql, self.conn)
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            print(f"SQL: {sql}")
            return None
    
    def execute(self, sql):
        """执行非查询SQL"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            cursor.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            print(f"SQL: {sql}")
            return False
    
    def table_exists(self, table_name):
        """检查表是否存在"""
        if table_name in self.table_exists_cache:
            return self.table_exists_cache[table_name]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = ?
            """, (table_name,))
            count = cursor.fetchone()[0]
            exists = count > 0
            self.table_exists_cache[table_name] = exists
            cursor.close()
            return exists
        except Exception as e:
            print(f"❌ 检查表存在失败: {e}")
            return False
    
    def get_table_columns(self, table_name):
        """获取表的所有列名"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            columns = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return columns
        except Exception as e:
            print(f"❌ 获取表字段失败: {e}")
            return []
    
    def get_companies(self):
        """获取所有公司列表"""
        from task2.config import TABLE_NAMES
        
        for table_name in TABLE_NAMES.values():
            if self.table_exists(table_name):
                sql = f"SELECT DISTINCT stock_abbr FROM {table_name} WHERE stock_abbr IS NOT NULL"
                df = self.query(sql)
                if df is not None and not df.empty:
                    companies = df['stock_abbr'].tolist()
                    print(f"✅ 从表 {table_name} 找到 {len(companies)} 家公司")
                    return companies
        print("⚠️ 未找到公司列表")
        return []
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print("🔌 数据库连接已关闭")