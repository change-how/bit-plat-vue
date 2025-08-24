#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import requests
import json

def check_complete_workflow():
    """检查完整的工作流程"""
    print("=== 完整工作流程验证 ===\n")
    
    # 1. 检查数据库表数据
    print("1. 检查数据库数据...")
    check_database_data()
    
    # 2. 测试搜索API
    print("\n2. 测试搜索API...")
    test_search_api()
    
    # 3. 测试思维导图API
    print("\n3. 测试思维导图API...")
    test_mindmap_api()

def check_database_data():
    """检查数据库中的数据"""
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
        
        # 检查各表数据量
        tables = ['users', 'transactions', 'asset_movements', 'login_logs', 'devices', 'file_metadata']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} 条记录")
            
            # 显示示例数据
            if count > 0 and table == 'file_metadata':
                cursor.execute("""
                SELECT file_name, original_filename, file_size, platform, 
                       record_count, status, upload_time 
                FROM file_metadata LIMIT 2
                """)
                results = cursor.fetchall()
                print("   file_metadata 示例:")
                for row in results:
                    print(f"     文件: {row[1]} | 大小: {row[2]} | 平台: {row[3]} | 记录: {row[4]} | 状态: {row[5]}")
            
            elif count > 0 and table == 'users':
                cursor.execute("SELECT user_id, name FROM users LIMIT 2")
                results = cursor.fetchall()
                print(f"   {table} 示例:")
                for row in results:
                    print(f"     用户ID: {row[0]} | 姓名: {row[1] or 'N/A'}")
                    
    except Exception as e:
        print(f"   数据库查询失败: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def test_search_api():
    """测试搜索API"""
    try:
        # 首先获取数据库中的实际用户ID
        connection = mysql.connector.connect(
            host='127.0.0.1', port=3306, user='root', password='123456',
            database='test_db', charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM users LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            test_user_id = result[0]
            print(f"   测试用户ID: {test_user_id}")
            
            # 测试搜索API
            response = requests.get("http://localhost:5000/api/search_uid", 
                                  params={'query': test_user_id})
            print(f"   搜索响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                print(f"   找到用户数: {len(users)}")
                if users:
                    print(f"   第一个用户: {users[0].get('user_id')} - {users[0].get('name', 'N/A')}")
            else:
                print(f"   搜索失败: {response.text}")
        else:
            print("   数据库中没有用户数据，跳过搜索测试")
            
        connection.close()
    except Exception as e:
        print(f"   搜索API测试失败: {e}")

def test_mindmap_api():
    """测试思维导图API"""
    try:
        # 获取数据库中的实际用户ID
        connection = mysql.connector.connect(
            host='127.0.0.1', port=3306, user='root', password='123456',
            database='test_db', charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT user_id FROM users LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            test_user_id = result[0]
            print(f"   测试用户ID: {test_user_id}")
            
            # 测试思维导图API
            response = requests.get("http://localhost:5000/api/mindmap_data", 
                                  params={'user_id': test_user_id})
            print(f"   思维导图响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   根节点: {data.get('data', {}).get('text', 'N/A')}")
                
                children = data.get('children', [])
                print(f"   子节点数: {len(children)}")
                
                # 查找Excel源文件节点
                for child in children:
                    child_text = child.get('data', {}).get('text', '')
                    if 'Excel源文件' in child_text:
                        print(f"   Excel源文件节点: {child_text}")
                        
                        file_children = child.get('children', [])
                        print(f"   文件数量: {len(file_children)}")
                        
                        # 显示前2个文件的详情
                        for i, file_node in enumerate(file_children[:2]):
                            file_text = file_node.get('data', {}).get('text', '')
                            print(f"     文件{i+1}: {file_text}")
                            
                            # 显示文件详细信息
                            file_details = file_node.get('children', [])
                            for detail in file_details[:3]:  # 前3个详情
                                detail_text = detail.get('data', {}).get('text', '')
                                print(f"       - {detail_text}")
                        break
                else:
                    print("   未找到Excel源文件节点")
            else:
                print(f"   思维导图失败: {response.text}")
        else:
            print("   数据库中没有用户数据，跳过思维导图测试")
            
        connection.close()
    except Exception as e:
        print(f"   思维导图API测试失败: {e}")

if __name__ == "__main__":
    check_complete_workflow()
