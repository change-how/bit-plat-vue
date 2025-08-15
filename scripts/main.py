# main.py
from pathlib import Path
import pandas as pd
# 导入commentjson，用于读取我们带注释的 .jsonc 配置文件
import commentjson
from sqlalchemy import create_engine 
from utils import inspect_excel_structure #excel表的透视函数，只是个小工具
from utils import test_database_connection#测试数据库连通性的函数
from utils import load_mapping_config#加载、解析.jsonc文件的函数
from utils import get_db_engine
from data_extract import extract_data_from_sources
from data_extract import extract_data_from_sources, process_single_destination
from utils import test_database_connection, load_mapping_config, get_db_engine, write_df_to_db
from utils import determine_company_from_filename
from utils import reset_database_tables
from utils import delete_data_by_filename
import transforms

# --- 1. 配置区 (MySQL版本) ---

# 数据库配置 (已为您修改为MySQL格式)
DB_CONFIG = {
    'type': 'mysql',        # 数据库类型
    'user': 'root',         # 您的MySQL用户名
    'password': '123456',     # 您的MySQL密码
    'host': '127.0.0.1',   # 数据库主机地址，如果是本机通常是 '127.0.0.1' 或 'localhost'
    'port': '3306',        # MySQL的默认端口通常是 3306
    'db_name': 'test_db'   # 想使用的数据库名，请确保这个数据库在您的MySQL中已经存在
}
FUNCTION_REGISTRY = {
    'parse_universal_datetime': transforms.parse_universal_datetime,
    'string_to_decimal': transforms.string_to_decimal,
    'map_buy_sell': transforms.map_buy_sell,
    'extract_base_asset': transforms.extract_base_asset,
    'extract_quote_asset': transforms.extract_quote_asset
}
TEMPLATE_REGISTRY = {
    'okx': Path("./config/okx_map.jsonc"),
    'binance': Path("./config/binance_map.jsonc"),
    'huobi': Path("./config/huobi_map.jsonc")
    # 未来需要支持新公司时，只需在这里新加一行即可！
}
CORE_TABLES = [
    'users',
    'transactions',
    'asset_movements',
    'login_logs',
    'devices',
    'asset_ledgers'
]
#SOURCE_EXCEL_PATH = Path("./uploads/1754532631_OKX陈兆群.xlsx")
SOURCE_EXCEL_PATH = Path("./uploads/BNB_binance.xlsx")
inspect_excel_structure(SOURCE_EXCEL_PATH)#excel文件透视镜


print("--- ETL流程开始 (多目标模式) ---")

# --- 主执行流程 (最终版，接口已对齐) ---
if __name__ == '__main__':
    
    # 将要处理的文件路径赋值给一个新变量，方便理解
    file_to_process = SOURCE_EXCEL_PATH
    
    print(f"--- 开始处理文件: {file_to_process.name} ---")

    # 步骤1：调度员上岗，判断公司名称
    company_name = determine_company_from_filename(file_to_process, TEMPLATE_REGISTRY)
    
    if not company_name:
        print(f"❌ 流程中断：无法从文件名识别公司。请检查文件名或TEMPLATE_REGISTRY配置。")
    else:
        print(f"✅ 识别到公司: {company_name}")
        
        # 步骤2：根据公司名，动态构建模板文件路径
        mapping_file_path = TEMPLATE_REGISTRY[company_name]
        
        # 步骤3：加载动态选择的“设计图”
        mapping_config = load_mapping_config(mapping_file_path)
        
        if not mapping_config:
            print(f"❌ 流程中断：未能加载 {company_name} 的映射配置。")
        else:
            # 步骤4：测试数据库连接
            test_database_connection(DB_CONFIG)

            # 步骤5：执行“精准清扫”，删除该文件相关的旧数据
            #(如果您需要这个功能，就取消下面的注释)
            delete_data_by_filename(DB_CONFIG, CORE_TABLES, file_to_process.name)
            
            # 步骤6：提取所有“原材料”
            extracted_data = extract_data_from_sources(
                file_to_process,
                mapping_config.get('sources', [])
            )
            
            if not extracted_data:
                print("❌ 流程中断：数据提取失败。")
            else:
                # 步骤7：遍历每一个“目的地/生产线”
                print("\n--- 开始遍历处理每一个目的地 ---")
                for destination in mapping_config.get('destinations', []):
                    target_table_name = destination.get('target_table')
                    print(f"\n--- 正在处理目标表: '{target_table_name}' ---")

                    # 调用最终版的“首席工匠”函数，传入文件名
                    final_df = process_single_destination(
                        destination,
                        extracted_data,
                        FUNCTION_REGISTRY,
                        file_to_process.name # <-- 已补上缺失的参数
                    )
                    
                    # 步骤8：调用“物流部门”，写入数据
                    if final_df is not None and not final_df.empty:
                        write_df_to_db(final_df, target_table_name, DB_CONFIG)
                
                print("\n--- 所有目的地处理完毕 ---")