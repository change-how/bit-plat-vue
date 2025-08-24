#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试API端点
BASE_URL = "http://localhost:5000"

def test_search_api():
    """测试搜索API"""
    print("1. 测试搜索API...")
    try:
        # 尝试不同的搜索词
        search_terms = ['1754490637', 'OKX', 'test']
        for term in search_terms:
            print(f"   搜索词: {term}")
            response = requests.get(f"{BASE_URL}/api/search_uid", 
                                  params={'query': term})  # 修正参数名
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('users'):
                    users = data['users']
                    print(f"   找到 {len(users)} 条记录")
                    if users:
                        print(f"   第一条记录: {users[0]}")
                else:
                    print("   未找到匹配记录")
            else:
                print(f"   错误响应: {response.text}")
            print()
    except Exception as e:
        print(f"   请求失败: {e}")

def test_mindmap_api():
    """测试思维导图API"""
    print("\n2. 测试思维导图API...")
    try:
        response = requests.get(f"{BASE_URL}/api/mindmap_data", 
                              params={'user_id': 'test_user'})
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   返回数据结构: {type(data)}")
            if isinstance(data, dict):
                print(f"   根节点: {data.get('data', {}).get('text', 'N/A')}")
                if 'children' in data:
                    print(f"   子节点数量: {len(data['children'])}")
                    for i, child in enumerate(data['children'][:3]):  # 只显示前3个
                        child_text = child.get('data', {}).get('text', 'N/A')
                        print(f"     - 子节点{i+1}: {child_text}")
        else:
            print(f"   错误响应: {response.text}")
    except Exception as e:
        print(f"   请求失败: {e}")

def test_file_upload():
    """测试文件上传功能（模拟）"""
    print("\n3. 检查文件元数据...")
    try:
        # 检查现有上传的文件
        import os
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            files = [f for f in os.listdir(uploads_dir) if f.endswith('.xlsx')]
            print(f"   找到 {len(files)} 个Excel文件")
            if files:
                print(f"   示例文件: {files[:3]}")  # 显示前3个
        else:
            print("   uploads目录不存在")
    except Exception as e:
        print(f"   检查失败: {e}")

if __name__ == "__main__":
    print("=== API功能测试 ===")
    test_search_api()
    test_mindmap_api()
    test_file_upload()
    print("\n=== 测试完成 ===")
