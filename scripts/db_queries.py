# scripts/db_queries.py

from .utils import get_db_engine
import pandas as pd

def get_data_from_db(db_config: dict, user_id: str):
    """
    根据用户ID从数据库获取所有相关数据。
    """
    print(f"准备从数据库中为用户 '{user_id}' 查询数据...")
    engine = get_db_engine(db_config)
    
    # 定义我们要执行的SQL查询语句
    query = f"""
    SELECT * FROM transactions 
    WHERE user_id = '{user_id}';
    """
    print(query)
    # 使用pandas执行查询
    try:
        transactions_df = pd.read_sql(query, engine)
        print(f"成功查询到 {len(transactions_df)} 条交易记录。")
        return transactions_df
    except Exception as e:
        print(f"数据库查询失败: {e}")
        return None