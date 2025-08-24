#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json

BASE_URL = "http://localhost:5000"

def test_file_upload():
    """测试文件上传功能"""
    print("=== 测试文件上传功能 ===")
    
    # 查找一个测试文件
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("uploads目录不存在")
        return
    
    excel_files = [f for f in os.listdir(uploads_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print("未找到Excel文件")
        return
    
    # 选择第一个文件进行测试
    test_file = excel_files[0]
    file_path = os.path.join(uploads_dir, test_file)
    
    print(f"选择测试文件: {test_file}")
    print(f"文件大小: {os.path.getsize(file_path)} bytes")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (test_file, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print("正在上传文件...")
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
            
            print(f"上传响应状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print("上传成功!")
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 如果返回了处理结果，检查数据库
                if data.get('status') == 'success':
                    print("\n检查数据库中的数据...")
                    check_database_after_upload()
            else:
                print(f"上传失败: {response.text}")
                
    except Exception as e:
        print(f"上传过程出错: {e}")

def check_database_after_upload():
    """检查上传后数据库中的数据"""
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
        tables = ['users', 'transactions', 'asset_movements', 'login_logs', 'devices', 'file_metadata']
        
        print("数据库表数据统计:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")
            
        # 如果有file_metadata数据，显示详情
        cursor.execute("SELECT COUNT(*) FROM file_metadata")
        file_count = cursor.fetchone()[0]
        if file_count > 0:
            cursor.execute("SELECT file_name, original_filename, file_size, platform, record_count, status FROM file_metadata")
            results = cursor.fetchall()
            print("\nfile_metadata表内容:")
            for row in results:
                print(f"  文件: {row[1]} | 平台: {row[3]} | 记录数: {row[4]} | 状态: {row[5]}")
                
    except Exception as e:
        print(f'数据库查询失败: {e}')
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    test_file_upload()
