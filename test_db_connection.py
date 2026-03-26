# test_db_connection.py (临时测试脚本)
import pyodbc

# 测试连接
try:
    # 尝试不同的连接方式
    server = '127.0.0.1,1433'
    database = 'Teddy'
    
    # 方式1：Windows认证
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'
    print(f"尝试连接: {conn_str}")
    conn = pyodbc.connect(conn_str)
    print("✅ Windows认证连接成功")
    conn.close()
    
except Exception as e:
    print(f"❌ Windows认证失败: {e}")
    
    # 方式2：SQL Server认证
    try:
        conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID=sa;PWD=your_password'
        print(f"尝试连接: {conn_str}")
        conn = pyodbc.connect(conn_str)
        print("✅ SQL Server认证连接成功")
        conn.close()
    except Exception as e2:
        print(f"❌ SQL Server认证失败: {e2}")
        
        # 方式3：尝试不同的驱动
        drivers = ['ODBC Driver 17 for SQL Server', 'ODBC Driver 13 for SQL Server', 'SQL Server Native Client 11.0']
        for driver in drivers:
            try:
                conn_str = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes'
                print(f"尝试驱动: {driver}")
                conn = pyodbc.connect(conn_str)
                print(f"✅ 使用驱动 {driver} 连接成功")
                conn.close()
                break
            except:
                continue