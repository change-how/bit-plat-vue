#!/usr/bin/env python3
# 测试修复后的API

import requests
import json

def test_mindmap_api():
    """测试修复后的mindmap_data API"""
    # 首先找一个真实的用户ID
    import sys
    sys.path.append('scripts')
    from db_queries import search_users_by_fuzzy_term
    from config import DB_CONFIG
    
    # 搜索真实用户
    test_user_id = None
    search_terms = ['陈兆群', 'OKX', 'Bitget', 'ImToken']
    
    for term in search_terms:
        try:
            results = search_users_by_fuzzy_term(DB_CONFIG, term)
            if results and len(results) > 0:
                test_user_id = results[0]['user_id']
                print(f"🔍 找到测试用户: {results[0]['name']} (ID: {test_user_id})")
                break
        except:
            continue
    
    if not test_user_id:
        test_user_id = '12345'  # 使用默认ID
        print(f"⚠️ 未找到真实用户，使用默认ID: {test_user_id}")
    
    try:
        url = f'http://127.0.0.1:5000/api/mindmap_data?user_id={test_user_id}'
        print(f"正在测试API: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print('✅ API调用成功!')
            print(f'状态: {data.get("status")}')
            
            if data.get('status') == 'success' and 'data' in data:
                api_data = data['data']
                print(f'\n📊 数据结构:')
                for key, value in api_data.items():
                    if isinstance(value, list):
                        print(f'  {key}: {len(value)}条记录')
                    else:
                        print(f'  {key}: {type(value)}')
                
                # 检查Excel文件元数据
                if 'source_files' in api_data:
                    source_files = api_data['source_files']
                    print(f'\n📁 Excel源文件信息:')
                    print(f'  文件数量: {len(source_files)}')
                    if source_files:
                        print('  前2个文件详情:')
                        for i, file_info in enumerate(source_files[:2]):
                            print(f'  文件{i+1}: {type(file_info).__name__}')
                            if isinstance(file_info, dict):
                                for k, v in file_info.items():
                                    print(f'    {k}: {v}')
                            else:
                                print(f'    内容: {file_info}')
                    else:
                        print('  ⚠️ 源文件列表为空')
                
                return True
            else:
                print(f'❌ API返回错误: {data}')
                return False
        else:
            print(f'❌ HTTP错误: {response.status_code}')
            try:
                error_data = response.json()
                print(f'错误详情: {error_data}')
            except:
                print(f'响应内容: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        return False

if __name__ == '__main__':
    print("🔧 测试修复后的mindmap_data API")
    print("=" * 50)
    success = test_mindmap_api()
    print("=" * 50)
    if success:
        print("✅ API修复成功，现在应该能正常显示Excel文件元数据了！")
    else:
        print("❌ API仍有问题，需要进一步调试")
