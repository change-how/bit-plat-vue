# db_setup.py (最终版 - 溯源 + 混合模型)
# 这个脚本专门负责初始化和重置数据库结构，包含了所有最终功能。

from sqlalchemy import create_engine, text

# --- 配置区 ---
DB_CONFIG = {
    'type': 'mysql',
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'test_db'
}

# --- 最终的、最全的数据库表结构定义 ---
# 包含了 source_file_name 和 extra_data
TABLE_DEFINITIONS = [
    # -- 表1: 统一用户信息表 --
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255) UNIQUE,
        name VARCHAR(255),
        registration_time DATETIME,
        phone_number VARCHAR(100),
        email VARCHAR(255),
        source_file_name TEXT,
        extra_data JSON
    );
    """,
    # -- 表2: 统一交易记录表 --
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255),
        transaction_id VARCHAR(255),
        transaction_time DATETIME,
        transaction_type VARCHAR(50),
        direction VARCHAR(50),
        base_asset VARCHAR(50),
        quote_asset VARCHAR(50),
        price DECIMAL(36, 18),
        quantity DECIMAL(36, 18),
        total_amount DECIMAL(36, 18),
        fee DECIMAL(36, 18),
        fee_asset VARCHAR(50),
        source_file_name TEXT,
        extra_data JSON
    );
    """,
    # -- 表3: 统一充提记录表 --
    """
    CREATE TABLE IF NOT EXISTS asset_movements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255),
        direction VARCHAR(50),
        asset VARCHAR(50),
        quantity DECIMAL(36, 18),
        address TEXT,
        txid TEXT,
        network VARCHAR(100),
        transaction_time DATETIME,
        status VARCHAR(100),
        source_file_name TEXT,
        extra_data JSON
    );
    """,
    # -- 表4: 统一登录日志表 --
    """
    CREATE TABLE IF NOT EXISTS login_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255),
        login_time DATETIME,
        login_ip VARCHAR(100),
        device_id VARCHAR(255),
        source_file_name TEXT,
        extra_data JSON
    );
    """,
    # -- 表5: 统一设备信息表 --
    """
    CREATE TABLE IF NOT EXISTS devices (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255),
        device_id VARCHAR(255),
        client_type VARCHAR(100),
        ip_address VARCHAR(100),
        add_time DATETIME,
        source_file_name TEXT,
        extra_data JSON
    );
    """,
    # -- 表6: 统一资产流水表 --
    """
    CREATE TABLE IF NOT EXISTS asset_ledgers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        source VARCHAR(50),
        user_id VARCHAR(255),
        record_id VARCHAR(255),
        record_time DATETIME,
        asset VARCHAR(50),
        change_type VARCHAR(100),
        change_amount DECIMAL(36, 18),
        balance_after DECIMAL(36, 18),
        source_file_name TEXT,
        extra_data JSON
    );
    """
]

# --- 主执行函数 (保持不变) ---
def initialize_database():
    """连接到数据库并执行所有表的创建语句。"""
    print("--- 开始初始化数据库结构 (最终溯源版) ---")
    try:
        conn_url = (f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}")
        engine = create_engine(conn_url)

        with engine.connect() as connection:
            for table_sql in TABLE_DEFINITIONS:
                connection.execute(text(table_sql))
            connection.commit()
        
        print("✅ 数据库结构初始化成功！所有核心表都已按“最终”模式创建。")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


# --- 脚本入口 (保持不变) ---
if __name__ == '__main__':
    initialize_database()