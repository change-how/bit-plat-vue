#!/usr/bin/env python3
# test_search_function.py - 测试搜索函数
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.main import DB_CONFIG
from scripts.db_queries import search_users_by_fuzzy_term

print("测试搜索函数...")

# 测试已知存在的用户ID
test_user_ids = ['10111198', '122919803', '127132518']

for user_id in test_user_ids:
    print(f"\n🔍 搜索用户ID: {user_id}")
    try:
        results = search_users_by_fuzzy_term(DB_CONFIG, user_id)
        if results:
            print(f"✅ 找到 {len(results)} 个结果:")
            for result in results:
                print(f"   - 用户ID: {result['user_id']}")
                print(f"   - 姓名: {result.get('name', '无')}")
                print(f"   - 匹配类型: {result.get('match_type', '无')}")
        else:
            print(f"❌ 没有找到结果")
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()

print("\n测试完成!")
