# db_setup.py (最终版 - 溯源 + 混合模型)
# 这个脚本专门负责初始化和重置数据库结构，包含了所有最终功能。
# 新增功能：在创建表之前，先彻底删除已存在的旧表，以确保环境干净。

from sqlalchemy import create_engine, text

# --- 配置区 (保持不变) ---
DB_CONFIG = {
    'type': 'mysql',
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'test_db'
}

# --- 定义表名列表 (新增) ---
# 将所有表名集中管理，方便删除操作
TABLE_NAMES = [
    'users',
    'transactions',
    'asset_movements',
    'login_logs',
    'devices',
    'file_metadata'
]


# --- 最终的、最全的数据库表结构定义 (保持不变) ---
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
    # -- 表6: 文件元信息表 --
    """
    CREATE TABLE IF NOT EXISTS file_metadata (
        id INT AUTO_INCREMENT PRIMARY KEY,
        file_name VARCHAR(255) UNIQUE NOT NULL COMMENT '存储文件名（唯一标识）',
        original_filename VARCHAR(255) COMMENT '用户上传时的原始文件名',
        file_size BIGINT COMMENT '文件大小（字节）',
        file_type VARCHAR(20) COMMENT '文件类型（扩展名）',
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
        platform VARCHAR(50) COMMENT '平台名称（如OKX、Binance等）',
        file_path TEXT COMMENT '文件存储路径',
        record_count INT DEFAULT 0 COMMENT '处理后的记录数量',
        status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded' COMMENT '处理状态',
        processed_time TIMESTAMP NULL COMMENT '处理完成时间',
        error_message TEXT COMMENT '错误信息（如果有）',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_platform (platform),
        INDEX idx_status (status),
        INDEX idx_upload_time (upload_time)
    ) COMMENT='文件元信息表，记录上传文件的详细信息';
    """
]

# --- 主执行函数 (已修改) ---
def initialize_database():
    """
    连接到数据库，先删除所有已知的旧表，然后重新创建它们。
    这是一个重置(Reset)操作。
    """
    print("--- 开始重置数据库结构 (清空并重建) ---")
    try:
        conn_url = (f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
                    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}")
        engine = create_engine(conn_url)

        with engine.connect() as connection:
            # 步骤 1: 循环删除所有已知的表
            print("1. 正在清空旧表...")
            # 从后往前删除，这是一个好习惯，可以避免未来可能因外键约束导致的问题
            for table_name in reversed(TABLE_NAMES):
                print(f"   - 正在删除表: {table_name}")
                connection.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
            print("   ✅ 所有旧表已成功删除。")

            # 步骤 2: 循环创建所有新表
            print("\n2. 正在创建新表...")
            for table_sql in TABLE_DEFINITIONS:
                connection.execute(text(table_sql))
            print("   ✅ 所有新表结构已成功创建。")
            
            # 提交事务
            connection.commit()
        
        print("\n✅ 数据库重置成功！所有核心表都已被清空并重新创建。")

    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")


# --- 脚本入口 (保持不变) ---
if __name__ == '__main__':
    initialize_database()