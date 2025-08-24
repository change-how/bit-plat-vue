#!/usr/bin/env python3
# 简化版数据逻辑分析

import mysql.connector

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'db_name': 'test_db'
}

def analyze_data_extraction_logic():
    """分析后端数据提取逻辑"""
    print("🔍 分析后端数据提取逻辑")
    print("=" * 60)
    
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['db_name'],
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 1. 查看用户表中的数据样例
        print("📊 用户表数据样例:")
        cursor.execute("SELECT user_id, name, source_file_name FROM users LIMIT 3")
        users = cursor.fetchall()
        for user in users:
            print(f"  用户ID: {user[0]}, 姓名: {user[1]}, 文件名: {user[2]}")
        
        # 2. 查看交易表中的数据样例  
        print("\n📊 交易表数据样例:")
        cursor.execute("SELECT user_id, source_file_name FROM transactions LIMIT 3")
        transactions = cursor.fetchall()
        for tx in transactions:
            print(f"  用户ID: {tx[0]}, 文件名: {tx[1]}")
        
        # 3. 查看文件元数据表
        print("\n📊 文件元数据表样例:")
        cursor.execute("SELECT file_name, original_filename, platform FROM file_metadata LIMIT 3")
        files = cursor.fetchall()
        for file_info in files:
            print(f"  file_name: {file_info[0]}, 原始名: {file_info[1]}, 平台: {file_info[2]}")
        
        # 4. 模拟数据提取过程
        if users:
            test_user_id = users[0][0]
            print(f"\n🔄 模拟提取用户 {test_user_id} 的数据:")
            
            # 查询该用户的所有表数据，收集source_file_name
            tables = ['users', 'transactions', 'asset_movements', 'login_logs', 'devices']
            source_files_set = set()
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT source_file_name FROM {table} WHERE user_id = %s", (test_user_id,))
                    results = cursor.fetchall()
                    for row in results:
                        if row[0]:  # 如果source_file_name不为空
                            source_files_set.add(row[0])
                    print(f"  {table} 表: {len(results)}条记录")
                except Exception as e:
                    print(f"  {table} 表: 查询失败 - {e}")
            
            print(f"\n📋 收集到的源文件名: {list(source_files_set)}")
            
            # 查询这些文件的详细信息
            if source_files_set:
                placeholders = ','.join(['%s'] * len(source_files_set))
                query = f"SELECT file_name, original_filename, platform FROM file_metadata WHERE file_name IN ({placeholders})"
                cursor.execute(query, tuple(source_files_set))
                file_details = cursor.fetchall()
                
                print(f"\n📁 对应的文件详细信息:")
                for file_detail in file_details:
                    print(f"  {file_detail[0]} -> 原始名: {file_detail[1]}, 平台: {file_detail[2]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("📝 数据关联逻辑总结:")
    print("✅ 关联依据: 根据 source_file_name 字段关联")
    print("✅ 提取步骤:")
    print("   1. 根据 user_id 查询各表数据")
    print("   2. 收集所有 source_file_name 字段值")
    print("   3. 用文件名在 file_metadata 表中查询详细信息")
    print("   4. 返回包含完整文件元数据的数据结构")
    print("❌ 不是根据 user_id 直接关联文件")
    print("❌ 是通过 source_file_name 间接关联的")

if __name__ == '__main__':
    analyze_data_extraction_logic()
