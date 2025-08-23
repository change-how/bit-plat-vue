#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据概览测试工具
用于快速查看上传文件的数据结构和内容概览
"""

import pandas as pd
import json
from pathlib import Path
import sys
import os

# 设置工作目录
scripts_dir = Path(__file__).parent / 'scripts'
os.chdir(scripts_dir)
sys.path.append('.')

from data_extract import extract_data_from_sources

def show_data_overview(file_path: str, config_file: str = None):
    """
    显示文件的数据概览
    
    Args:
        file_path: 要分析的文件路径
        config_file: 可选的配置文件路径
    """
    print("="*80)
    print(f"📂 数据文件概览工具")
    print("="*80)
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    print(f"📄 分析文件: {file_path.name}")
    print(f"📁 文件路径: {file_path}")
    print(f"📏 文件大小: {file_path.stat().st_size / 1024:.2f} KB")
    
    # 如果没有指定配置文件，使用默认配置
    if config_file is None:
        print(f"🔧 使用默认配置进行数据探索...")
        
        # 为不同文件类型创建默认配置
        if file_path.suffix.lower() == '.csv':
            # CSV默认配置：尝试多种识别方式
            default_configs = [
                {
                    "source_id": "standard_table",
                    "data_layout": "tabular",
                    "header_row": 1
                },
                {
                    "source_id": "search_by_header",
                    "data_layout": "find_subtable_by_header",
                    "section_header_aliases": [
                        "address", "time", "ip", "user", "wallet", "create", "login",
                        "地址", "时间", "用户", "钱包", "创建", "登录"
                    ],
                    "header_offset": 0
                }
            ]
        else:
            # Excel默认配置
            default_configs = [
                {
                    "source_id": "sheet1_data",
                    "worksheet_name": "Sheet1", 
                    "data_layout": "tabular",
                    "header_row": 1
                }
            ]
        
        configs_to_test = default_configs
    else:
        # 读取指定的配置文件
        print(f"🔧 读取配置文件: {config_file}")
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 移除JSON注释
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                if '//' in line:
                    line = line[:line.index('//')]
                clean_lines.append(line)
            clean_content = '\n'.join(clean_lines)
            config = json.loads(clean_content)
        
        configs_to_test = config.get('sources', [])
    
    print("\n" + "="*80)
    print("🔍 开始数据分析...")
    print("="*80)
    
    # 执行数据提取
    extracted_data = extract_data_from_sources(file_path, configs_to_test)
    
    if extracted_data:
        print("\n" + "="*80)
        print("📊 数据概览总结")
        print("="*80)
        
        total_sources = len(extracted_data)
        total_records = 0
        
        for source_id, data in extracted_data.items():
            if isinstance(data, pd.DataFrame):
                total_records += len(data)
        
        print(f"📈 总计: {total_sources} 个数据源，{total_records} 条记录")
        
        # 简化概览
        for i, (source_id, data) in enumerate(extracted_data.items(), 1):
            print(f"\n--- 数据源 {i}: {source_id} ---")
            if isinstance(data, pd.DataFrame):
                print(f"   类型: 表格数据")
                print(f"   大小: {data.shape[0]} 行 × {data.shape[1]} 列") 
                print(f"   字段: {', '.join(data.columns)}")
            elif isinstance(data, dict):
                print(f"   类型: 键值对数据")
                print(f"   大小: {len(data)} 个字段")
                print(f"   键名: {', '.join(list(data.keys())[:10])}...")
            else:
                print(f"   类型: {type(data)}")
    else:
        print("❌ 数据提取失败")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据文件概览工具')
    parser.add_argument('file_path', help='要分析的文件路径')
    parser.add_argument('--config', help='配置文件路径（可选）')
    
    args = parser.parse_args()
    
    show_data_overview(args.file_path, args.config)
