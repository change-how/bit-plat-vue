#!/usr/bin/env python
# test_error_handling.py - 测试错误处理功能

import sys
import os
sys.path.append('.')

from pathlib import Path
from scripts.main import run_etl_process_for_file
from scripts.error_handler import ETLError, format_error_for_frontend

def test_file_not_exist():
    """测试文件不存在的错误"""
    print("=== 测试1: 文件不存在 ===")
    fake_file = Path("不存在的文件.xlsx")
    success, result = run_etl_process_for_file(fake_file)
    print(f"成功: {success}")
    if isinstance(result, ETLError):
        error_dict = format_error_for_frontend(result)
        print(f"错误类型: {error_dict['error']['type']}")
        print(f"错误标题: {error_dict['error']['title']}")
        print(f"用户消息: {error_dict['error']['user_message']}")
        print(f"建议: {error_dict['error']['suggestions']}")
    print()

def test_company_not_recognized():
    """测试无法识别公司的错误"""
    print("=== 测试2: 公司识别失败 ===")
    # 创建一个临时文件
    temp_file = Path("未知公司_test.xlsx")
    temp_file.write_text("test")
    
    try:
        success, result = run_etl_process_for_file(temp_file)
        print(f"成功: {success}")
        if isinstance(result, ETLError):
            error_dict = format_error_for_frontend(result)
            print(f"错误类型: {error_dict['error']['type']}")
            print(f"错误标题: {error_dict['error']['title']}")
            print(f"用户消息: {error_dict['error']['user_message']}")
            print(f"建议: {error_dict['error']['suggestions']}")
    finally:
        if temp_file.exists():
            temp_file.unlink()
    print()

def test_huobi_template():
    """测试火币模板加载"""
    print("=== 测试3: 火币模板测试 ===")
    # 创建一个火币测试文件
    temp_file = Path("uploads/test_huobi_data.xlsx")
    temp_file.parent.mkdir(exist_ok=True)
    temp_file.write_text("test")
    
    try:
        success, result = run_etl_process_for_file(temp_file)
        print(f"成功: {success}")
        if isinstance(result, ETLError):
            error_dict = format_error_for_frontend(result)
            print(f"错误类型: {error_dict['error']['type']}")
            print(f"错误标题: {error_dict['error']['title']}")
            print(f"用户消息: {error_dict['error']['user_message']}")
            print(f"建议: {error_dict['error']['suggestions']}")
        else:
            print(f"结果: {result}")
    finally:
        if temp_file.exists():
            temp_file.unlink()
    print()

if __name__ == "__main__":
    print("开始测试错误处理功能...\n")
    
    test_file_not_exist()
    test_company_not_recognized()
    test_huobi_template()
    
    print("测试完成！")
