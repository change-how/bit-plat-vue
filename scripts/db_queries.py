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

def search_users_by_fuzzy_term(db_config: dict, search_term: str):
    """
    通过模糊查找在多个表中搜索用户信息
    返回匹配的用户ID列表及相关信息
    """
    print(f"开始模糊查找用户信息，搜索词: '{search_term}'")
    engine = get_db_engine(db_config)
    
    # 构建模糊查找的SQL语句，在多个表的多个字段中搜索
    # 使用LIKE进行模糊匹配，%通配符表示任意字符
    search_pattern = f"%{search_term}%"
    
    query = f"""
    SELECT DISTINCT 
        u.user_id,
        u.name,
        u.phone_number,
        u.email,
        u.source,
        '用户信息' as match_type,
        CONCAT_WS(' | ', 
            CASE WHEN u.name LIKE '{search_pattern}' THEN CONCAT('姓名: ', u.name) END,
            CASE WHEN u.phone_number LIKE '{search_pattern}' THEN CONCAT('手机: ', u.phone_number) END,
            CASE WHEN u.email LIKE '{search_pattern}' THEN CONCAT('邮箱: ', u.email) END,
            CASE WHEN u.source LIKE '{search_pattern}' THEN CONCAT('平台: ', u.source) END
        ) as match_details
    FROM users u
    WHERE u.name LIKE '{search_pattern}' 
       OR u.phone_number LIKE '{search_pattern}'
       OR u.email LIKE '{search_pattern}'
       OR u.source LIKE '{search_pattern}'
    
    UNION ALL
    
    SELECT DISTINCT
        l.user_id,
        u.name,
        u.phone_number,
        u.email,
        l.source,
        '登录日志' as match_type,
        CONCAT_WS(' | ',
            CASE WHEN l.login_ip LIKE '{search_pattern}' THEN CONCAT('登录IP: ', l.login_ip) END,
            CASE WHEN l.device_id LIKE '{search_pattern}' THEN CONCAT('设备ID: ', l.device_id) END
        ) as match_details
    FROM login_logs l
    LEFT JOIN users u ON l.user_id = u.user_id
    WHERE l.login_ip LIKE '{search_pattern}'
       OR l.device_id LIKE '{search_pattern}'
    
    UNION ALL
    
    SELECT DISTINCT
        d.user_id,
        u.name,
        u.phone_number, 
        u.email,
        d.source,
        '设备信息' as match_type,
        CONCAT_WS(' | ',
            CASE WHEN d.device_id LIKE '{search_pattern}' THEN CONCAT('设备ID: ', d.device_id) END,
            CASE WHEN d.client_type LIKE '{search_pattern}' THEN CONCAT('客户端: ', d.client_type) END,
            CASE WHEN d.ip_address LIKE '{search_pattern}' THEN CONCAT('IP地址: ', d.ip_address) END
        ) as match_details
    FROM devices d
    LEFT JOIN users u ON d.user_id = u.user_id
    WHERE d.device_id LIKE '{search_pattern}'
       OR d.client_type LIKE '{search_pattern}'
       OR d.ip_address LIKE '{search_pattern}'
    
    UNION ALL
    
    SELECT DISTINCT
        am.user_id,
        u.name,
        u.phone_number,
        u.email,
        am.source,
        '资产流水' as match_type,
        CONCAT_WS(' | ',
            CASE WHEN am.address LIKE '{search_pattern}' THEN CONCAT('地址: ', am.address) END,
            CASE WHEN am.txid LIKE '{search_pattern}' THEN CONCAT('交易ID: ', am.txid) END,
            CASE WHEN am.network LIKE '{search_pattern}' THEN CONCAT('网络: ', am.network) END
        ) as match_details
    FROM asset_movements am
    LEFT JOIN users u ON am.user_id = u.user_id
    WHERE am.address LIKE '{search_pattern}'
       OR am.txid LIKE '{search_pattern}'
       OR am.network LIKE '{search_pattern}'
    
    ORDER BY user_id, match_type
    """
    
    try:
        results_df = pd.read_sql(query, engine)
        print(f"模糊查找完成，找到 {len(results_df)} 条匹配记录")
        
        if len(results_df) == 0:
            return []
        
        # 转换为字典列表，便于JSON序列化
        results = []
        for _, row in results_df.iterrows():
            result = {
                'user_id': row['user_id'],
                'name': row['name'] if pd.notna(row['name']) else '',
                'phone_number': row['phone_number'] if pd.notna(row['phone_number']) else '',
                'email': row['email'] if pd.notna(row['email']) else '',
                'source': row['source'] if pd.notna(row['source']) else '',
                'match_type': row['match_type'],
                'match_details': row['match_details'] if pd.notna(row['match_details']) else ''
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"模糊查找失败: {e}")
        return None