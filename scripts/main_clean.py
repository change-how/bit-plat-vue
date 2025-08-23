# main.py - 虚拟币平台数据处理引擎
from pathlib import Path
import pandas as pd
import commentjson
from sqlalchemy import create_engine 
from .utils import test_database_connection, load_mapping_config, get_db_engine, write_df_to_db
from .utils import determine_company_from_filename, delete_data_by_filename
from .data_extract import extract_data_from_sources, process_single_destination
from . import transforms

# --- 数据库配置 ---
DB_CONFIG = {
    'type': 'mysql',        
    'user': 'root',         
    'password': '123456',     
    'host': '127.0.0.1',   
    'port': '3306',        
    'db_name': 'test_db'   
}

# --- 数据转换函数注册表 ---
FUNCTION_REGISTRY = {
    'parse_universal_datetime': transforms.parse_universal_datetime,
    'string_to_decimal': transforms.string_to_decimal,
    'map_buy_sell': transforms.map_buy_sell,
    'extract_base_asset': transforms.extract_base_asset,
    'extract_quote_asset': transforms.extract_quote_asset,
    'map_imtoken_direction': transforms.map_imtoken_direction
}

# --- 模板文件注册表 ---
TEMPLATE_REGISTRY = {
    'okx': Path("./config/okx_map.jsonc"),
    'binance': Path("./config/binance_map.jsonc"),
    'huobi': Path("./config/huobi_map.jsonc"),
    'imtoken': Path("./config/imtoken_map.jsonc"),
    'tokenpocket': Path("./config/tokenpocket_map.jsonc"),
    'csv': Path("./config/csv_universal_map.jsonc")
}

# --- 核心数据表列表 ---
CORE_TABLES = [
    'users',
    'transactions',
    'asset_movements',
    'login_logs',
    'devices'
]

def run_etl_process_for_file(file_path: Path):
    """
    执行单个文件的完整ETL流程
    
    Args:
        file_path: 待处理文件的路径
    
    Returns:
        tuple: (是否成功, 消息)
    """
    try:
        print("--- ETL流程开始 (单文件模式) ---")
        print(f"--- 开始处理文件: {file_path.name} ---")

        # 步骤1：识别公司类型
        company_name = determine_company_from_filename(file_path, TEMPLATE_REGISTRY)
        
        if not company_name:
            error_msg = f"无法从文件名 {file_path.name} 识别公司类型"
            print(f"❌ 流程中断：{error_msg}")
            return False, error_msg
        else:
            print(f"✅ 识别到公司: {company_name}")
            
            # 步骤2：加载配置模板
            mapping_file_path = TEMPLATE_REGISTRY[company_name]
            mapping_config = load_mapping_config(mapping_file_path)
            
            if not mapping_config:
                error_msg = f"无法加载 {company_name} 的映射配置"
                print(f"❌ 流程中断：{error_msg}")
                return False, error_msg
            else:
                # 步骤3：测试数据库连接
                test_database_connection(DB_CONFIG)

                # 步骤4：清理旧数据
                delete_data_by_filename(DB_CONFIG, CORE_TABLES, file_path.name)
                
                # 步骤5：提取数据
                extracted_data = extract_data_from_sources(
                    file_path,
                    mapping_config.get('sources', [])
                )
                
                if not extracted_data:
                    error_msg = "数据提取失败"
                    print(f"❌ 流程中断：{error_msg}")
                    return False, error_msg
                else:
                    # 步骤6：处理每个目标表
                    print("\n--- 开始遍历处理每一个目的地 ---")
                    for destination in mapping_config.get('destinations', []):
                        target_table_name = destination.get('target_table')
                        print(f"\n--- 正在处理目标表: '{target_table_name}' ---")

                        # 处理数据并转换
                        final_df = process_single_destination(
                            destination,
                            extracted_data,
                            FUNCTION_REGISTRY,
                            file_path.name
                        )
                        
                        # 写入数据库
                        if final_df is not None and not final_df.empty:
                            write_df_to_db(final_df, target_table_name, DB_CONFIG)
                    
                    print("\n--- 所有目的地处理完毕 ---")
                    success_msg = f"文件 {file_path.name} 已成功处理并入库"
                    return True, success_msg
                    
    except Exception as e:
        error_msg = f"处理文件 {file_path.name} 时发生严重错误: {e}"
        print(error_msg)
        return False, str(e)

# --- 开发测试入口 ---
if __name__ == '__main__':
    print("main.py: 此文件现在主要提供 run_etl_process_for_file() 函数供 Flask 应用调用。")
    print("如需测试处理流程，请通过 web 界面上传文件或直接调用 run_etl_process_for_file() 函数。")
