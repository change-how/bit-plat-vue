#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

try:
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        database='test_db',
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # 检查各个表的数据量
    tables = ['users', 'transactions', 'asset_movements', 'login_logs', 'devices']
    
    print("=== 数据库表数据统计 ===")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} 条记录")
        
        if count > 0:
            # 显示第一条记录的user_id
            cursor.execute(f"SELECT user_id FROM {table} LIMIT 1")
            result = cursor.fetchone()
            if result and result[0]:
                print(f"  示例user_id: {result[0]}")
    
    print("\n=== file_metadata表 ===")
    cursor.execute("SELECT COUNT(*) FROM file_metadata")
    count = cursor.fetchone()[0]
    print(f"file_metadata: {count} 条记录")
    
    if count > 0:
        cursor.execute("SELECT file_name, original_filename, file_size FROM file_metadata LIMIT 3")
        results = cursor.fetchall()
        print("示例文件:")
        for row in results:
            print(f"  {row[0]} | {row[1]} | {row[2]} bytes")
        
except Exception as e:
    print(f'数据库查询失败: {e}')
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
