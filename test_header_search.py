#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV标题查找功能测试脚本
测试通过标题文本查找数据表格的功能
"""

import pandas as pd
import json
from pathlib import Path
import sys
import os

# 添加scripts目录到路径
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.append(scripts_dir)

# 切换到scripts目录执行导入
original_cwd = os.getcwd()
os.chdir(scripts_dir)

try:
    from data_extract import extract_data_from_sources
    from utils import get_db_engine
    
    # 直接读取配置而不导入main
    DB_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'bitcoin_investigation'
    }
finally:
    os.chdir(original_cwd)

def test_header_search():
    """测试CSV中通过标题查找数据的功能"""
    
    print("=== 测试CSV标题查找功能 ===\n")
    
    # 1. 读取配置文件
    config_path = Path("config/csv_header_search_example.jsonc")
    print(f"1. 读取配置文件: {config_path}")
    
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
    
    print(f"   ✅ 配置加载成功")
    print(f"   - 数据源数量: {len(config['sources'])}")
    print(f"   - 目标表数量: {len(config['destinations'])}")
    
    # 2. 测试CSV文件解析
    csv_path = Path("test_header_search.csv")
    print(f"\n2. 解析测试CSV文件: {csv_path}")
    
    extracted_data = extract_data_from_sources(csv_path, config['sources'])
    
    if extracted_data is None:
        print("   ❌ CSV解析失败")
        return
    
    print(f"   ✅ CSV解析成功，提取到 {len(extracted_data)} 个数据源")
    
    # 3. 展示每个数据源的内容
    for source_id, data in extracted_data.items():
        print(f"\n--- 数据源: {source_id} ---")
        if isinstance(data, pd.DataFrame):
            print(f"类型: DataFrame, 行数: {len(data)}")
            if not data.empty:
                print("前几行数据:")
                print(data.head().to_string())
            else:
                print("   (空表格)")
        elif isinstance(data, dict):
            print(f"类型: Dict, 键数量: {len(data)}")
            print("键值对:")
            for k, v in data.items():
                print(f"   {k}: {v}")
        else:
            print(f"类型: {type(data)}")
    
    # 4. 测试查找函数的内部逻辑
    print(f"\n=== 内部查找逻辑测试 ===")
    
    # 读取原始CSV文件
    raw_csv = pd.read_csv(csv_path, header=None)
    print(f"原始CSV文件形状: {raw_csv.shape}")
    print("前10行内容:")
    print(raw_csv.head(10).to_string())
    
    # 测试查找"交易记录"标题
    print(f"\n--- 测试查找'交易记录'标题 ---")
    target_aliases = ["交易记录", "Transaction Records", "交易明细", "转账记录"]
    
    for row_idx, row in raw_csv.iterrows():
        for col_idx, cell_value in enumerate(row):
            if pd.notna(cell_value):
                cell_str = str(cell_value).strip()
                for alias in target_aliases:
                    if alias in cell_str:
                        print(f"   ✅ 找到匹配: 第{row_idx+1}行, 第{col_idx+1}列, 内容='{cell_str}'")
                        print(f"   表头应在第{row_idx+2}行")
                        if row_idx + 1 < len(raw_csv):
                            header_row = raw_csv.iloc[row_idx + 1]
                            print(f"   表头内容: {list(header_row.dropna())}")
                        break
    
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    test_header_search()
