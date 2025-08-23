import mysql.connector

# --- 请修改这里的数据库连接信息 ---
DB_CONFIG = {
    'host': 'localhost',      # 数据库主机地址
    'user': 'root',      # 您的用户名
    'password': '123456',# 您的密码
    'database': 'test_db' # 要连接的数据库名
}
# ------------------------------------

def get_mysql_field_names_formatted():
    """连接MySQL并打印每个表的字段名，每个字段名占一行。"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        if not tables:
            print(f"在数据库 '{DB_CONFIG['database']}' 中没有找到任何表。")
            return

        print(f"--- 数据库 '{DB_CONFIG['database']}' 的字段信息 ---")
        
        for table_name in tables:
            print(f"\n[+] 表名: {table_name}")
            print("-" * (len(table_name) + 12))
            
            # 使用 DESCRIBE 命令更直接
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            
            for col in columns:
                print(col[0]) # 字段名在结果的第一列

    except mysql.connector.Error as e:
        print(f"数据库连接或查询时发生错误: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    get_mysql_field_names_formatted()