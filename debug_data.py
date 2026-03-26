# debug_data.py (调试脚本)
"""
调试数据脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from task2.db_utils import Database

def main():
    db = Database()
    
    print("=" * 60)
    print("🔍 检查金花股份的利润总额数据")
    print("=" * 60)
    
    # 查询金花股份的所有利润总额数据
    sql = """
    SELECT report_period, report_year, total_profit 
    FROM income_sheet 
    WHERE stock_abbr = '金花股份' 
    ORDER BY report_year, report_period
    """
    
    df = db.query(sql)
    if df is not None:
        print(f"\n📊 利润总额数据:")
        print(df.to_string())
        
        # 检查重复数据
        print(f"\n📊 数据统计:")
        print(f"总记录数: {len(df)}")
        print(f"唯一报告期: {df['report_period'].unique()}")
        
        # 查看每个报告期的数据
        for period in df['report_period'].unique():
            period_data = df[df['report_period'] == period]
            print(f"\n{period}:")
            print(period_data[['report_period', 'total_profit']].to_string())
    
    print("\n" + "=" * 60)
    print("🔍 检查华润三九的利润总额数据")
    print("=" * 60)
    
    sql2 = """
    SELECT report_period, report_year, total_profit 
    FROM income_sheet 
    WHERE stock_abbr = '华润三九' 
    ORDER BY report_year, report_period
    """
    
    df2 = db.query(sql2)
    if df2 is not None:
        print(f"\n📊 利润总额数据:")
        print(df2.to_string())
    
    db.close()

if __name__ == "__main__":
    main()