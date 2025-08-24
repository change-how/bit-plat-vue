#!/usr/bin/env python3
# test_db_connection.py - 测试数据库连接和查看数据
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.main import DB_CONFIG
from scripts.db_queries import search_users_by_fuzzy_term, get_data_from_db
from scripts.utils import get_db_engine
import pandas as pd

def test_db_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        engine = get_db_engine(DB_CONFIG)
        # 测试连接
        result = pd.read_sql("SELECT 1 as test", engine)
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_tables():
    """检查数据库表和数据"""
    print("\n=== 检查数据库表 ===")
    try:
        engine = get_db_engine(DB_CONFIG)
        
        tables = ['users', 'transactions', 'asset_movements', 'login_logs', 'devices']
        
        for table in tables:
            try:
                count_query = f"SELECT COUNT(*) as count FROM {table}"
                result = pd.read_sql(count_query, engine)
                count = result.iloc[0]['count']
                print(f"📊 {table} 表: {count} 条记录")
                
                if count > 0:
                    # 显示前几条记录的用户ID
                    sample_query = f"SELECT user_id FROM {table} LIMIT 3"
                    sample_result = pd.read_sql(sample_query, engine)
                    user_ids = sample_result['user_id'].tolist()
                    print(f"   样本用户ID: {user_ids}")
                    
            except Exception as e:
                print(f"❌ 查询 {table} 表失败: {e}")
                
    except Exception as e:
        print(f"❌ 检查表时出错: {e}")

def test_search_function():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    try:
        # 先获取一个存在的用户ID进行测试
        engine = get_db_engine(DB_CONFIG)
        result = pd.read_sql("SELECT user_id FROM users LIMIT 1", engine)
        
        if len(result) > 0:
            test_user_id = result.iloc[0]['user_id']
            print(f"🔍 测试搜索用户ID: {test_user_id}")
            
            # 测试搜索
            search_results = search_users_by_fuzzy_term(DB_CONFIG, str(test_user_id))
            if search_results:
                print(f"✅ 搜索成功，找到 {len(search_results)} 个结果")
                for result in search_results[:3]:  # 显示前3个结果
                    print(f"   - 用户ID: {result['user_id']}, 姓名: {result['name']}, 匹配类型: {result['match_type']}")
            else:
                print("❌ 搜索没有返回结果")
        else:
            print("❌ users表中没有数据")
            
    except Exception as e:
        print(f"❌ 测试搜索功能失败: {e}")

if __name__ == "__main__":
    print("开始数据库测试...")
    
    # 测试连接
    if test_db_connection():
        # 检查表
        check_tables()
        # 测试搜索
        test_search_function()
    
    print("\n测试完成!")
