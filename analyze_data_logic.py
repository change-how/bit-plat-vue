#!/usr/bin/env python3
# 检查数据提取逻辑

import sys
sys.path.append('scripts')
from db_queries import get_data_from_db
from config import DB_CONFIG
import mysql.connector

def analyze_data_extraction_logic():
    """分析后端数据提取逻辑"""
    print("🔍 分析后端数据提取逻辑")
    print("=" * 60)
    
    # 1. 查看数据库中的用户信息
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG.get('host', '127.0.0.1'),
            port=DB_CONFIG.get('port', 3306),
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['db_name'],
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 查看用户表中的数据样例
        print("📊 用户表数据样例:")
        cursor.execute("SELECT user_id, name, source_file_name FROM users LIMIT 3")
        users = cursor.fetchall()
        for user in users:
            print(f"  用户ID: {user[0]}, 姓名: {user[1]}, 文件名: {user[2]}")
        
        # 查看交易表中的数据样例
        print("\n📊 交易表数据样例:")
        cursor.execute("SELECT user_id, source_file_name FROM transactions LIMIT 3")
        transactions = cursor.fetchall()
        for tx in transactions:
            print(f"  用户ID: {tx[0]}, 文件名: {tx[1]}")
        
        # 查看文件元数据表
        print("\n📊 文件元数据表样例:")
        cursor.execute("SELECT file_name, original_filename, platform FROM file_metadata LIMIT 3")
        files = cursor.fetchall()
        for file_info in files:
            print(f"  文件名: {file_info[0]}, 原始名: {file_info[1]}, 平台: {file_info[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return
    
    # 2. 测试数据提取过程
    print("\n🔄 测试数据提取过程:")
    
    # 选择一个用户ID进行测试
    if users:
        test_user_id = users[0][0]
        print(f"测试用户ID: {test_user_id}")
        
        # 调用数据提取函数
        result = get_data_from_db(DB_CONFIG, test_user_id)
        
        if result:
            print(f"\n📋 提取结果:")
            for key, value in result.items():
                if isinstance(value, list):
                    print(f"  {key}: {len(value)}条记录")
                    if value and key != 'source_files':
                        # 显示第一条记录的source_file_name
                        first_record = value[0]
                        if 'source_file_name' in first_record:
                            print(f"    示例文件名: {first_record['source_file_name']}")
                    elif key == 'source_files' and value:
                        print(f"    文件详情:")
                        for i, file_info in enumerate(value[:2]):
                            print(f"      文件{i+1}: {file_info.get('file_name', 'N/A')}")
                            print(f"        原始名: {file_info.get('original_filename', 'N/A')}")
                            print(f"        平台: {file_info.get('platform', 'N/A')}")
        else:
            print("❌ 未获取到数据")
    
    print("\n" + "=" * 60)
    print("📝 数据关联逻辑总结:")
    print("1. 后端根据 user_id 查询各个表 (users, transactions, asset_movements, etc.)")
    print("2. 从查询结果中收集所有的 source_file_name 字段")
    print("3. 使用这些文件名去 file_metadata 表中查询详细的文件信息")
    print("4. 关联依据是: source_file_name = file_metadata.file_name")
    print("5. 最终返回包含详细文件元数据的完整数据结构")

if __name__ == '__main__':
    analyze_data_extraction_logic()
