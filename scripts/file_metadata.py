# scripts/file_metadata.py - 文件元信息管理
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from sqlalchemy import text
from .utils import get_db_engine

def insert_file_metadata(db_config: dict, file_path: str, original_filename: str = None, platform: str = None):
    """
    插入文件元信息到数据库
    """
    try:
        file_path = Path(file_path)
        
        # 获取文件信息
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        file_type = file_path.suffix.lower()
        
        # 如果没有提供原始文件名，使用当前文件名
        if original_filename is None:
            original_filename = file_path.name
            
        # 推断平台信息
        if platform is None:
            platform = infer_platform_from_filename(file_path.name)
        
        engine = get_db_engine(db_config)
        
        # 检查文件是否已存在
        import mysql.connector
        conn = mysql.connector.connect(
            host=db_config.get('host', '127.0.0.1'),
            port=db_config.get('port', 3306),
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db_name'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        check_query = "SELECT id FROM file_metadata WHERE file_name = %s"
        cursor.execute(check_query, (file_path.name,))
        existing = cursor.fetchall()
        
        if existing:
            # 更新现有记录
            update_query = """
            UPDATE file_metadata 
            SET original_filename = %s, file_size = %s, file_type = %s, 
                platform = %s, file_path = %s, updated_at = CURRENT_TIMESTAMP
            WHERE file_name = %s
            """
            cursor.execute(update_query, (
                original_filename, file_size, file_type, 
                platform, str(file_path), file_path.name
            ))
            conn.commit()
            print(f"更新文件元信息: {file_path.name}")
        else:
            # 插入新记录
            insert_query = """
            INSERT INTO file_metadata 
            (file_name, original_filename, file_size, file_type, platform, file_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                file_path.name, original_filename, file_size, 
                file_type, platform, str(file_path)
            ))
            conn.commit()
            print(f"插入文件元信息: {file_path.name}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"插入文件元信息失败: {e}")
        return False

def get_file_metadata_by_names(db_config: dict, file_names: list):
    """
    根据文件名列表获取文件元信息
    """
    try:
        if not file_names:
            return []
        
        # 使用原始mysql连接
        import mysql.connector
        conn = mysql.connector.connect(
            host=db_config.get('host', '127.0.0.1'),
            port=db_config.get('port', 3306),
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db_name'],
            charset='utf8mb4'
        )
        
        # 构建IN查询
        placeholders = ','.join(['%s'] * len(file_names))
        query = f"""
        SELECT 
            file_name,
            original_filename,
            file_size,
            file_type,
            upload_time,
            platform,
            record_count,
            status,
            CASE 
                WHEN file_size < 1024 THEN CONCAT(file_size, ' B')
                WHEN file_size < 1048576 THEN CONCAT(ROUND(file_size/1024, 1), ' KB')
                WHEN file_size < 1073741824 THEN CONCAT(ROUND(file_size/1048576, 1), ' MB')
                ELSE CONCAT(ROUND(file_size/1073741824, 1), ' GB')
            END as file_size_formatted
        FROM file_metadata 
        WHERE file_name IN ({placeholders})
        ORDER BY upload_time DESC
        """
        
        cursor = conn.cursor()
        cursor.execute(query, tuple(file_names))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 转换为字典列表
        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            result = {
                'file_name': row_dict['file_name'],
                'original_filename': row_dict['original_filename'] or row_dict['file_name'],
                'file_size': row_dict['file_size_formatted'],
                'file_type': row_dict['file_type'],
                'upload_time': row_dict['upload_time'].strftime('%Y-%m-%d %H:%M:%S') if row_dict['upload_time'] else '',
                'platform': row_dict['platform'] or '未知',
                'record_count': int(row_dict['record_count']) if row_dict['record_count'] is not None else 0,
                'status': row_dict['status']
            }
            results.append(result)
            
        print(f"获取到 {len(results)} 个文件的元信息")
        return results
        
    except Exception as e:
        print(f"获取文件元信息失败: {e}")
        return []

def update_file_record_count(db_config: dict, file_name: str, record_count: int):
    """
    更新文件的记录数量
    """
    try:
        engine = get_db_engine(db_config)
        
        update_query = """
        UPDATE file_metadata 
        SET record_count = %s, status = 'processed', processed_time = CURRENT_TIMESTAMP
        WHERE file_name = %s
        """
        
        # 使用原始连接执行
        import mysql.connector
        conn = mysql.connector.connect(
            host=db_config.get('host', '127.0.0.1'),
            port=db_config.get('port', 3306),
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db_name'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute(update_query, (record_count, file_name))
        conn.commit()
        cursor.close()
        conn.close()
            
        print(f"更新文件 {file_name} 的记录数: {record_count}")
        return True
        
    except Exception as e:
        print(f"更新文件记录数失败: {e}")
        return False

def infer_platform_from_filename(filename: str):
    """
    从文件名推断平台
    """
    filename_lower = filename.lower()
    
    if 'okx' in filename_lower:
        return 'OKX'
    elif 'binance' in filename_lower or '币安' in filename_lower:
        return 'Binance'
    elif 'huobi' in filename_lower or '火币' in filename_lower:
        return 'Huobi'
    elif 'imtoken' in filename_lower:
        return 'ImToken'
    elif 'tokenpocket' in filename_lower:
        return 'TokenPocket'
    else:
        return '通用'

def create_file_metadata_table(db_config: dict):
    """
    创建文件元信息表
    """
    try:
        engine = get_db_engine(db_config)
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS file_metadata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL UNIQUE,
            original_filename VARCHAR(255),
            file_size BIGINT,
            file_type VARCHAR(50),
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            platform VARCHAR(50),
            file_path VARCHAR(500),
            processed_time TIMESTAMP NULL,
            record_count INT DEFAULT 0,
            status ENUM('uploaded', 'processing', 'processed', 'error') DEFAULT 'uploaded',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        
        with engine.connect() as conn:
            conn.execute(create_table_sql)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_name ON file_metadata(file_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_upload_time ON file_metadata(upload_time)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_platform ON file_metadata(platform)")
            
            conn.commit()
            
        print("文件元信息表创建成功")
        return True
        
    except Exception as e:
        print(f"创建文件元信息表失败: {e}")
        return False
