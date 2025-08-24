#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def debug_mindmap_api():
    """详细调试思维导图API"""
    print("=== 调试思维导图API ===\n")
    
    try:
        # 测试思维导图API
        response = requests.get("http://localhost:5000/api/mindmap_data", 
                              params={'user_id': '122919803'})
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"完整响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查数据结构
            if isinstance(data, dict):
                print(f"\n数据类型: 字典")
                print(f"根节点文本: {data.get('data', {}).get('text', 'N/A')}")
                
                children = data.get('children', [])
                print(f"子节点数量: {len(children)}")
                
                for i, child in enumerate(children):
                    child_text = child.get('data', {}).get('text', 'N/A')
                    print(f"  子节点{i+1}: {child_text}")
                    
                    # 检查Excel源文件节点
                    if 'Excel源文件' in child_text:
                        print(f"    找到Excel源文件节点!")
                        file_children = child.get('children', [])
                        print(f"    文件子节点数: {len(file_children)}")
                        
                        for j, file_node in enumerate(file_children):
                            file_text = file_node.get('data', {}).get('text', 'N/A')
                            print(f"      文件{j+1}: {file_text}")
                            
                            # 检查文件详细信息
                            file_details = file_node.get('children', [])
                            print(f"      详细信息数: {len(file_details)}")
                            for detail in file_details:
                                detail_text = detail.get('data', {}).get('text', 'N/A')
                                print(f"        - {detail_text}")
            else:
                print(f"数据类型: {type(data)}")
        else:
            print(f"API错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    debug_mindmap_api()
