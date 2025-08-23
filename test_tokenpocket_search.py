#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通过标题查找方式读取TokenPocket CSV
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

def test_tokenpocket_header_search():
    """测试TokenPocket通过标题查找的方式"""
    
    print("=== 测试TokenPocket通过标题查找方式 ===\n")
    
    file_path = Path("../141数据调证数据/TokenPocket/TP嘉兴市公安局南湖区分局取证 (1).csv")
    
    # 先分析文件结构
    print("1. 分析TokenPocket文件结构:")
    raw_df = pd.read_csv(file_path, header=None, encoding='gbk')
    print(f"   文件形状: {raw_df.shape}")
    
    print("\n前10行内容:")
    for i in range(min(10, len(raw_df))):
        row_content = [str(x) if pd.notna(x) else 'NaN' for x in raw_df.iloc[i]]
        print(f"   第{i+1}行: {row_content}")
    
    # 测试通过标题查找的配置
    print("\n2. 测试通过标题查找配置:")
    
    test_configs = [
        {
            "name": "查找wallet_address标题",
            "config": {
                "source_id": "tokenpocket_data",
                "data_layout": "find_subtable_by_header",
                "section_header_aliases": [
                    "wallet_address",
                    "钱包地址", 
                    "address"
                ],
                "header_offset": 0  # 找到标题后，表头就在当前行（偏移量0）
            }
        },
        {
            "name": "查找create_time标题",
            "config": {
                "source_id": "tokenpocket_data2", 
                "data_layout": "find_subtable_by_header",
                "section_header_aliases": [
                    "create_time",
                    "创建时间",
                    "时间"
                ],
                "header_offset": 0
            }
        },
        {
            "name": "查找多个关键词组合",
            "config": {
                "source_id": "tokenpocket_data3",
                "data_layout": "find_subtable_by_header", 
                "section_header_aliases": [
                    "wallet_address,create_time",  # 查找包含这些关键词的行
                    "地址,时间",
                    "address,time"
                ],
                "header_offset": 0
            }
        }
    ]
    
    for test in test_configs:
        print(f"\n--- {test['name']} ---")
        print(f"查找标题: {test['config']['section_header_aliases']}")
        print(f"表头偏移: {test['config']['header_offset']}")
        
        try:
            # 使用我们的数据提取系统
            extracted = extract_data_from_sources(file_path, [test['config']])
            
            if extracted and test['config']['source_id'] in extracted:
                result_df = extracted[test['config']['source_id']]
                
                if isinstance(result_df, pd.DataFrame) and not result_df.empty:
                    print(f"   ✅ 成功提取 {len(result_df)} 行数据")
                    print(f"   列名: {list(result_df.columns)}")
                    print(f"   第一行示例: {dict(result_df.iloc[0])}")
                else:
                    print(f"   ❌ 提取结果为空")
            else:
                print(f"   ❌ 未能提取到数据")
                
        except Exception as e:
            print(f"   ❌ 提取出错: {e}")
    
    # 手动测试查找算法
    print(f"\n3. 手动测试标题查找算法:")
    target_aliases = ["wallet_address", "create_time"]
    
    for row_idx, row in raw_df.iterrows():
        for col_idx, cell_value in enumerate(row):
            if pd.notna(cell_value):
                cell_str = str(cell_value).strip()
                for alias in target_aliases:
                    if alias in cell_str:
                        print(f"   ✅ 找到匹配 '{alias}': 第{row_idx+1}行, 第{col_idx+1}列")
                        print(f"      完整行内容: {list(row)}")
                        
                        # 这就是表头行，偏移量为0
                        header_row_idx = row_idx + 0  # offset = 0
                        print(f"      表头行索引: {header_row_idx}")
                        
                        # 尝试解析数据
                        try:
                            test_df = pd.read_csv(file_path, header=header_row_idx, encoding='gbk')
                            print(f"      解析结果: {test_df.shape}, 列名: {list(test_df.columns)}")
                        except Exception as e:
                            print(f"      解析失败: {e}")
                        
                        return  # 找到后退出

if __name__ == "__main__":
    test_tokenpocket_header_search()
