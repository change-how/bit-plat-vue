#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import pandas as pd

# 连接数据库 - 使用正确的配置
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
    
    # 检查表是否存在
    cursor.execute("""
    SELECT TABLE_NAME 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'test_db' 
    AND TABLE_NAME = 'file_metadata'
    """)
    
    result = cursor.fetchall()
    if result:
        print('file_metadata表存在')
        
        # 查看表结构
        cursor.execute('DESCRIBE file_metadata')
        structure = cursor.fetchall()
        print('表结构:')
        for row in structure:
            print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}")
        
        # 查看数据示例
        cursor.execute('SELECT * FROM file_metadata LIMIT 3')
        sample_data = cursor.fetchall()
        print(f'\n数据示例 ({len(sample_data)}条):')
        if sample_data:
            # 获取列名
            cursor.execute('SHOW COLUMNS FROM file_metadata')
            columns = [row[0] for row in cursor.fetchall()]
            print(f"  列名: {columns}")
            for row in sample_data:
                print(f"  {row}")
        else:
            print('表中暂无数据')
    else:
        print('file_metadata表不存在，需要创建')
        
        # 查看所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print('数据库中现有的表:')
        for table in tables:
            print(f"  {table[0]}")
        
except Exception as e:
    print(f'数据库检查失败: {e}')
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
