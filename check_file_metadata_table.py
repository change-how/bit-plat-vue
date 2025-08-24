#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.utils import get_db_engine
import pandas as pd

# 连接数据库
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'crypto_db',
    'charset': 'utf8mb4'
}

try:
    engine = get_db_engine(db_config)
    
    # 检查表是否存在
    table_check_query = """
    SELECT TABLE_NAME 
    FROM information_schema.TABLES 
    WHERE TABLE_SCHEMA = 'crypto_db' 
    AND TABLE_NAME = 'file_metadata'
    """
    
    result = pd.read_sql(table_check_query, engine)
    if len(result) > 0:
        print('file_metadata表存在')
        
        # 查看表结构
        desc_query = 'DESCRIBE file_metadata'
        structure = pd.read_sql(desc_query, engine)
        print('表结构:')
        print(structure.to_string(index=False))
        
        # 查看数据示例
        sample_query = 'SELECT * FROM file_metadata LIMIT 3'
        sample_data = pd.read_sql(sample_query, engine)
        print(f'\n数据示例 ({len(sample_data)}条):')
        if len(sample_data) > 0:
            print(sample_data.to_string(index=False))
        else:
            print('表中暂无数据')
    else:
        print('file_metadata表不存在，需要创建')
        
except Exception as e:
    print(f'数据库检查失败: {e}')
