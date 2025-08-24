#!/usr/bin/env python3
# 测试API端点和数据库连接

from scripts.db_queries import search_users_by_fuzzy_term, get_data_from_db, DB_CONFIG
import requests
import json

def test_database_queries():
    """测试数据库查询功能"""
    print("=== 测试数据库查询功能 ===")
    
    # 测试搜索功能
    test_queries = [
        "TDanb2Mq68NFki4xBgDMH9ST14ozkzasQ8",
        "1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw",
        "陈兆群",
        "13"
    ]
    
    for query in test_queries:
        print(f"\n测试搜索: '{query}'")
        result = search_users_by_fuzzy_term(DB_CONFIG, query)
        if result:
            print(f"找到 {len(result)} 个用户:")
            for user in result:
                print(f"  - {user.get('name', 'N/A')} (ID: {user.get('user_id', 'N/A')})")
        else:
            print("  未找到匹配用户")

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    base_url = "http://127.0.0.1:5000"
    
    # 测试搜索API
    print("\n1. 测试搜索API:")
    search_url = f"{base_url}/api/search_uid"
    test_queries = ["陈兆群", "13"]
    
    for query in test_queries:
        try:
            response = requests.get(search_url, params={"query": query})
            print(f"搜索 '{query}': {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  状态: {data.get('status')}")
                if data.get('users'):
                    print(f"  找到 {len(data['users'])} 个用户")
                    for user in data['users']:
                        print(f"    - {user.get('name', 'N/A')} (ID: {user.get('user_id', 'N/A')})")
            else:
                print(f"  错误: {response.text}")
        except Exception as e:
            print(f"  请求失败: {e}")

    # 测试思维导图数据API
    print("\n2. 测试思维导图数据API:")
    # 先获取一个用户ID
    try:
        response = requests.get(search_url, params={"query": "陈兆群"})
        if response.status_code == 200:
            data = response.json()
            if data.get('users'):
                user_id = data['users'][0]['user_id']
                print(f"使用用户ID: {user_id}")
                
                mindmap_url = f"{base_url}/api/mindmap_data"
                response = requests.get(mindmap_url, params={"user_id": user_id})
                print(f"思维导图数据: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"  状态: {data.get('status')}")
                    if data.get('data'):
                        print("  数据结构:")
                        for table_name, records in data['data'].items():
                            if isinstance(records, list):
                                print(f"    {table_name}: {len(records)} 条记录")
                            else:
                                print(f"    {table_name}: {records}")
                else:
                    print(f"  错误: {response.text}")
    except Exception as e:
        print(f"  请求失败: {e}")

if __name__ == "__main__":
    test_database_queries()
    test_api_endpoints()
