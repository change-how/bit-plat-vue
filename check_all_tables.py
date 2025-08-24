#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine, text
import pandas as pd

# 使用与db_setup.py相同的配置
DB_CONFIG = {
    'type': 'mysql',
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'test_db'
}

try:
    conn_url = (f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}")
    engine = create_engine(conn_url)
    
    # 检查所有表
    print("=== 检查数据库中的所有表 ===")
    show_tables_query = "SHOW TABLES"
    tables_df = pd.read_sql(show_tables_query, engine)
    print(f"数据库中共有 {len(tables_df)} 个表:")
    for idx, row in tables_df.iterrows():
        table_name = row.iloc[0]
        print(f"  - {table_name}")
    
    # 专门检查file_metadata表
    if 'file_metadata' in tables_df.iloc[:, 0].values:
        print(f"\n=== file_metadata表结构 ===")
        desc_query = 'DESCRIBE file_metadata'
        structure = pd.read_sql(desc_query, engine)
        print(structure.to_string(index=False))
        
        # 查看数据示例
        sample_query = 'SELECT COUNT(*) as count FROM file_metadata'
        count_data = pd.read_sql(sample_query, engine)
        print(f"\nfile_metadata表中当前有 {count_data.iloc[0]['count']} 条记录")
    else:
        print(f"\n❌ file_metadata表不存在")
        
except Exception as e:
    print(f'数据库检查失败: {e}')
    import traceback
    traceback.print_exc()
