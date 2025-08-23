#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试TokenPocket通过标题查找功能
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

def test_tokenpocket_final():
    """最终测试TokenPocket通过标题查找"""
    
    print("=== TokenPocket通过标题查找最终测试 ===\n")
    
    # 1. 读取TokenPocket配置
    config_path = Path("../config/tokenpocket_map.jsonc")
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
    print(f"   - 数据源配置: {config['sources'][0]}")
    
    # 2. 测试TokenPocket文件
    csv_path = Path("../141数据调证数据/TokenPocket/TP嘉兴市公安局南湖区分局取证 (1).csv")
    print(f"\n2. 解析TokenPocket CSV: {csv_path}")
    
    # 使用我们的系统提取数据
    extracted_data = extract_data_from_sources(csv_path, config['sources'])
    
    if extracted_data is None:
        print("   ❌ 数据提取失败")
        return
    
    print(f"   ✅ 数据提取成功，得到 {len(extracted_data)} 个数据源")
    
    # 3. 展示提取结果
    for source_id, data in extracted_data.items():
        print(f"\n--- 数据源: {source_id} ---")
        if isinstance(data, pd.DataFrame):
            print(f"类型: DataFrame, 形状: {data.shape}")
            if not data.empty:
                print(f"列名: {list(data.columns)}")
                print("前3行数据:")
                for i in range(min(3, len(data))):
                    print(f"  第{i+1}行: {dict(data.iloc[i])}")
            else:
                print("   (空表格)")
        else:
            print(f"类型: {type(data)}")
    
    # 4. 验证关键信息
    if 'tokenpocket_login_logs' in extracted_data:
        df = extracted_data['tokenpocket_login_logs']
        if isinstance(df, pd.DataFrame) and not df.empty:
            print(f"\n=== 数据质量验证 ===")
            print(f"总记录数: {len(df)}")
            
            # 检查关键字段
            key_fields = ['wallet_address', 'create_time', 'ip', 'user-agent']
            for field in key_fields:
                if field in df.columns:
                    non_null_count = df[field].notna().sum()
                    print(f"{field}: {non_null_count}/{len(df)} 条有效记录")
                else:
                    print(f"{field}: ❌ 字段不存在")
            
            # 显示数据分布
            if 'wallet_address' in df.columns:
                unique_wallets = df['wallet_address'].nunique()
                print(f"唯一钱包地址数: {unique_wallets}")
            
            if 'ip' in df.columns:
                unique_ips = df['ip'].nunique()
                print(f"唯一IP地址数: {unique_ips}")

if __name__ == "__main__":
    test_tokenpocket_final()
