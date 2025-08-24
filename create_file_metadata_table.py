#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

# 创建file_metadata表
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    original_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    platform VARCHAR(100),
    file_path TEXT,
    record_count INT DEFAULT 0,
    processed_time TIMESTAMP NULL,
    status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_file_name (file_name),
    INDEX idx_platform (platform),
    INDEX idx_status (status),
    INDEX idx_upload_time (upload_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
"""

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
    
    # 创建表
    print("正在创建file_metadata表...")
    cursor.execute(CREATE_TABLE_SQL)
    connection.commit()
    print("file_metadata表创建成功!")
    
    # 验证表结构
    cursor.execute('DESCRIBE file_metadata')
    structure = cursor.fetchall()
    print('\n表结构:')
    print("字段名                | 类型           | 允许NULL | 键    | 默认值     | 额外")
    print("-" * 80)
    for row in structure:
        print(f"{row[0]:<20} | {row[1]:<14} | {row[2]:<8} | {row[3]:<5} | {row[4] or '':<10} | {row[5] or ''}")
    
    # 检查表是否创建成功
    cursor.execute("SHOW TABLES LIKE 'file_metadata'")
    result = cursor.fetchall()
    if result:
        print("\n✅ file_metadata表已成功创建并在数据库中!")
    else:
        print("\n❌ 表创建失败")
        
except Exception as e:
    print(f'创建表失败: {e}')
finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
