#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.file_metadata import insert_file_metadata, get_file_metadata_by_names
from scripts.main import DB_CONFIG

def test_file_metadata_functions():
    """测试文件元信息功能"""
    print("=== 测试文件元信息功能 ===\n")
    
    # 1. 测试插入文件元信息
    print("1. 测试插入文件元信息...")
    
    # 选择一个已上传的文件进行测试
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.startswith('175604')]
        if files:
            test_file = files[0]
            file_path = os.path.join(uploads_dir, test_file)
            
            print(f"   测试文件: {test_file}")
            
            # 手动插入文件元信息
            result = insert_file_metadata(
                DB_CONFIG, 
                file_path, 
                original_filename="测试文件.xlsx",
                platform="Binance"
            )
            
            if result:
                print("   ✅ 文件元信息插入成功")
            else:
                print("   ❌ 文件元信息插入失败")
            
            # 2. 测试获取文件元信息
            print("\n2. 测试获取文件元信息...")
            metadata_list = get_file_metadata_by_names(DB_CONFIG, [test_file])
            
            if metadata_list:
                print(f"   ✅ 获取到 {len(metadata_list)} 条文件元信息")
                for metadata in metadata_list:
                    print(f"   文件: {metadata['original_filename']}")
                    print(f"   大小: {metadata['file_size']}")
                    print(f"   平台: {metadata['platform']}")
                    print(f"   上传时间: {metadata['upload_time']}")
                    print(f"   状态: {metadata['status']}")
            else:
                print("   ❌ 未获取到文件元信息")
        else:
            print("   未找到最近上传的文件")
    else:
        print("   uploads目录不存在")
    
    # 3. 检查数据库中的file_metadata表
    print("\n3. 检查数据库中的file_metadata表...")
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
        cursor.execute("SELECT COUNT(*) FROM file_metadata")
        count = cursor.fetchone()[0]
        print(f"   file_metadata表记录数: {count}")
        
        if count > 0:
            cursor.execute("""
            SELECT file_name, original_filename, file_size, platform, 
                   record_count, status, upload_time 
            FROM file_metadata 
            ORDER BY upload_time DESC 
            LIMIT 3
            """)
            results = cursor.fetchall()
            print("   最新记录:")
            for row in results:
                print(f"     {row[1]} | {row[2]} bytes | {row[3]} | {row[4]} records | {row[5]}")
        
        connection.close()
        
    except Exception as e:
        print(f"   数据库查询失败: {e}")

if __name__ == "__main__":
    test_file_metadata_functions()
