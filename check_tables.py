# check_tables.py (放在项目根目录，修复版)
"""
检查数据库表结构的脚本
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from task2.db_utils import Database
from task2.config import TABLE_NAMES

def main():
    print("=" * 60)
    print("🔍 检查数据库表结构")
    print("=" * 60)
    
    try:
        db = Database()
        
        print("\n📊 数据库表检查:")
        for table_key, table_name in TABLE_NAMES.items():
            print(f"\n检查表: {table_name} ({table_key})")
            if db.table_exists(table_name):
                columns = db.get_table_columns(table_name)
                print(f"   ✅ 表存在")
                print(f"   📝 字段数: {len(columns)}")
                print(f"   📋 前10个字段: {columns[:10] if len(columns) > 10 else columns}")
                
                # 查看数据行数
                try:
                    sql = f"SELECT COUNT(*) as cnt FROM {table_name}"
                    df = db.query(sql)
                    if df is not None:
                        count = df.iloc[0, 0]
                        print(f"   📊 数据行数: {count}")
                except Exception as e:
                    print(f"   ⚠️ 无法获取行数: {e}")
            else:
                print(f"   ❌ 表不存在")
        
        # 获取公司列表
        print("\n🏢 公司列表:")
        companies = db.get_companies()
        if companies:
            for comp in companies:
                print(f"   📌 {comp}")
        else:
            print("   ⚠️ 未找到公司数据")
        
        db.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()