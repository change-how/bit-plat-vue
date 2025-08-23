#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实调证CSV文件的读取功能
验证不同格式的CSV文件是否能够正确识别和解析
"""

import pandas as pd
import json
from pathlib import Path
import sys
import os

# 设置工作目录到scripts
scripts_dir = Path(__file__).parent / 'scripts'
os.chdir(scripts_dir)
sys.path.append('.')

from data_extract import extract_data_from_sources

def test_csv_files():
    """测试真实的调证CSV文件"""
    
    print("=== 测试真实调证CSV文件读取功能 ===\n")
    
    # 定义测试文件
    test_files = [
        {
            "name": "ImToken",
            "path": "../141数据调证数据/Imtoken/e757744d193a390b.csv",
            "description": "标准表格格式，第1行为表头"
        },
        {
            "name": "TokenPocket", 
            "path": "../141数据调证数据/TokenPocket/TP嘉兴市公安局南湖区分局取证 (1).csv",
            "description": "复杂格式，需要查找表头位置"
        }
    ]
    
    for test_file in test_files:
        print(f"=== 测试 {test_file['name']} ===")
        print(f"文件路径: {test_file['path']}")
        print(f"描述: {test_file['description']}")
        
        file_path = Path(test_file['path'])
        
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        try:
            # 方法1: 直接读取CSV文件查看原始结构
            print(f"\n--- 原始文件结构分析 ---")
            raw_df = pd.read_csv(file_path, header=None, encoding='utf-8')
            print(f"文件形状: {raw_df.shape}")
            print(f"前10行内容:")
            for i in range(min(10, len(raw_df))):
                row_content = [str(x) if pd.notna(x) and str(x).strip() else 'EMPTY' for x in raw_df.iloc[i]]
                print(f"  第{i+1}行: {row_content}")
            
            # 方法2: 寻找可能的表头位置
            print(f"\n--- 表头位置识别 ---")
            potential_headers = []
            
            for row_idx in range(min(15, len(raw_df))):
                row = raw_df.iloc[row_idx]
                non_empty_count = sum(1 for x in row if pd.notna(x) and str(x).strip())
                if non_empty_count >= 3:  # 至少有3个非空字段
                    potential_headers.append((row_idx, non_empty_count, list(row)))
                    print(f"  候选表头第{row_idx+1}行 ({non_empty_count}字段): {[str(x) if pd.notna(x) else 'NaN' for x in row]}")
            
            # 方法3: 测试不同的表头位置
            print(f"\n--- 不同表头位置的解析测试 ---")
            for header_row_idx, field_count, header_content in potential_headers[:3]:  # 只测试前3个候选
                try:
                    print(f"  使用第{header_row_idx+1}行作为表头:")
                    test_df = pd.read_csv(file_path, header=header_row_idx, encoding='utf-8')
                    print(f"    解析后形状: {test_df.shape}")
                    print(f"    列名: {list(test_df.columns)}")
                    
                    # 检查数据质量
                    non_empty_rows = test_df.dropna(how='all')
                    print(f"    有效数据行数: {len(non_empty_rows)}")
                    if len(non_empty_rows) > 0:
                        print(f"    第一行数据示例: {dict(non_empty_rows.iloc[0])}")
                except Exception as e:
                    print(f"    ❌ 解析失败: {e}")
            
            # 方法4: 使用我们的4种识别方法测试
            print(f"\n--- 使用系统4种识别方法测试 ---")
            
            # 测试标准表格方式
            test_configs = [
                {
                    "source_id": "test_tabular",
                    "data_layout": "tabular", 
                    "header_row": 1
                },
                {
                    "source_id": "test_tabular_row6",
                    "data_layout": "tabular",
                    "header_row": 6  # TokenPocket可能在第6行
                }
            ]
            
            # 如果是TokenPocket，添加通过标题查找的测试
            if test_file['name'] == 'TokenPocket':
                test_configs.append({
                    "source_id": "test_header_search",
                    "data_layout": "find_subtable_by_header",
                    "section_header_aliases": ["wallet_address", "create_time", "user-agent"],
                    "header_offset": 0
                })
            
            for config in test_configs:
                try:
                    print(f"    测试配置: {config['data_layout']} (header_row: {config.get('header_row', 'N/A')})")
                    extracted = extract_data_from_sources(file_path, [config])
                    
                    if extracted and config['source_id'] in extracted:
                        result_df = extracted[config['source_id']]
                        if isinstance(result_df, pd.DataFrame):
                            print(f"      ✅ 成功提取 {len(result_df)} 行数据")
                            if not result_df.empty:
                                print(f"      列名: {list(result_df.columns)}")
                                print(f"      第一行示例: {dict(result_df.iloc[0])}")
                        else:
                            print(f"      ✅ 提取到字典数据: {result_df}")
                    else:
                        print(f"      ❌ 提取失败")
                        
                except Exception as e:
                    print(f"      ❌ 测试出错: {e}")
                    
        except Exception as e:
            print(f"❌ 读取文件出错: {e}")
        
        print(f"\n{'='*60}\n")

if __name__ == "__main__":
    test_csv_files()
