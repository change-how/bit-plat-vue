# scripts/utils.py
import json
import pandas as pd
from pathlib import Path
from .error_handler import ETLError, ErrorType, create_user_friendly_error
def inspect_excel_structure(file_path):
    """
    一个调试辅助函数，用来读取一个Excel文件并打印出其所有工作表及其列名的结构。
    """
    print("\n--- 开始检查Excel文件结构 ---")
    try:
        # 使用 pandas 读取所有工作表
        all_sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')
        
        # 创建一个字典来存储结构信息
        structure = {}
        
        # 遍历所有读取到的工作表
        for sheet_name, df in all_sheets.items():
            # 将每个工作表的列名列表存入结构字典
            structure[sheet_name] = list(df.columns)
            
        # 使用 json.dumps 来格式化输出，方便阅读
        print(json.dumps(structure, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"检查文件时出错: {e}")
    print("--- 文件结构检查完毕 ---\n")

#用来识别文件名名来对应使用哪个模板
#逻辑很简单，是读取文件前缀

def determine_company_from_filename(file_path: Path, registry: dict) -> str:
    """
    根据文件名和注册表，判断文件属于哪个公司。
    优先匹配具体公司名，如果是CSV文件且没有匹配到具体公司，则使用通用CSV模板。
    :param file_path: 文件的Path对象。
    :param registry: 公司模板注册字典。
    :return: 公司名称的小写字符串 (e.g., 'okx', 'csv')，如果无法判断则返回None。
    """
    filename_lower = file_path.name.lower()
    file_extension = file_path.suffix.lower()
    
    # 首先尝试匹配具体的公司名（排除通用的csv模板）
    for company_key in registry.keys():
        if company_key != 'csv' and company_key in filename_lower:
            return company_key
    
    # 如果没有匹配到具体公司，但是是CSV文件，则使用通用CSV模板
    if file_extension == '.csv' and 'csv' in registry:
        print(f"  - 未识别到具体公司，但检测到CSV文件，将使用通用CSV模板处理")
        return 'csv'
            
    return None # 如果找了一圈都没找到，就返回None
#数据库连接功能测试


# 导入sqlalchemy库的create_engine，用于创建数据库连接引擎
from sqlalchemy import create_engine

def get_db_engine(db_config: dict):
    """
    根据传入的数据库配置字典，创建并返回一个SQLAlchemy数据库引擎。
    :param db_config: 一个包含数据库连接信息的字典
    """
    db_type = db_config['type']

    if db_type == 'mysql':
        # 使用 f-string 构建标准的MySQL连接URL
        conn_url = (
            f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
        )
        return create_engine(conn_url, echo=False)  # 关闭SQL语句输出
    else:
        raise ValueError(f"当前配置只支持 'mysql'，但收到了 '{db_type}'")


def test_database_connection(db_config: dict):
    """
    接收一个数据库配置字典，尝试连接数据库，并打印连接结果。
    如果连接失败，会抛出ETLError异常。
    :param db_config: 一个包含数据库连接信息的字典
    """
    try:
        # 尝试通过传入的配置获取数据库引擎
        engine = get_db_engine(db_config)
        
        # 尝试建立一个真实的连接
        connection = engine.connect()
        
        print("  ✅ 数据库连接成功！")
        print(f"  📡 服务器版本: {engine.dialect.server_version_info}")
        
        connection.close()
        
    except Exception as e:
        print("  ❌ 数据库连接失败。请检查您的 DB_CONFIG 配置。")
        print(f"  🔥 错误详情: {e}")
        # 重新抛出为ETL错误，供上层捕获
        raise e


#加载.jsonc文件的工具
# (文件的顶部应该已经有 from sqlalchemy import create_engine)
# 新增的 import 语句，因为这个新函数需要它们
from pathlib import Path
import commentjson


def load_mapping_config(path: Path) -> dict:
    """
    加载并解析 .jsonc 映射文件。
    :param path: 指向 .jsonc 文件的 Path 对象。
    :return: 一个包含配置信息的字典，如果失败则抛出异常。
    """
    try:
        if not path.exists():
            raise FileNotFoundError(f"模板文件不存在: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            config_data = commentjson.load(f)
            print(f"  ✅ 配置模板加载成功: {path.name}")
            return config_data
    except Exception as e:
        print(f"  ❌ 加载模板文件失败: {str(e)}")
        # 重新抛出原始异常，供上层处理
        raise e

#接收处理好的数据(df)、目标表名(table_name)和数据库配置(db_config)，然后执行写入操作
def write_df_to_db(df, table_name: str, db_config: dict):
    """
    将一个DataFrame写入到指定的数据库表中。
    :param df: 要写入的Pandas DataFrame。
    :param table_name: 目标数据库表的名称。
    :param db_config: 数据库连接配置字典。
    """
    if df is None or df.empty:
        print(f"    🟡 '{table_name}' 表无数据，跳过写入")
        return

    try:
        # 从我们已有的函数中获取数据库引擎
        engine = get_db_engine(db_config)
        
        print(f"    📝 写入 {len(df)} 条记录到 '{table_name}' 表...")
        
        # 使用pandas强大的to_sql功能，将整个DataFrame一次性写入数据库
        df.to_sql(
            name=table_name,       # 目标表名
            con=engine,            # 数据库连接引擎
            if_exists='append',    # 如果表已存在，就追加数据。'replace'会替换整个表。
            index=False,           # 不要将DataFrame的行号索引作为一列写入数据库
            chunksize=1000         # 可选：一次写入1000行，对于大数据量可以提高效率
        )
        print(f"    ✅ '{table_name}' 表写入成功！")
        
    except Exception as e:
        print(f"    ❌ '{table_name}' 表写入失败: {e}")
        # 重新抛出原始异常，供上层处理
        raise e
# (文件上方是您已有的其他函数)
# ...
from sqlalchemy import text # <-- 在文件顶部，请确保从sqlalchemy导入text

# ↓↓↓ 将下面的新函数添加到文件末尾 ↓↓↓

def reset_database_tables(db_config: dict, table_names: list):
    """
    根据配置，删除数据库中指定的一系列表。
    :param db_config: 数据库连接配置字典。
    :param table_names: 一个包含所有要删除的表名的列表。
    """
    if not table_names:
        print("🟡 没有指定要删除的表，跳过重置操作。")
        return

    print("\n--- 开始重置数据库表 ---")
    try:
        engine = get_db_engine(db_config)
        with engine.connect() as connection:
            # 1. 关闭外键检查（安全操作，防止因表关联导致删除失败）
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # 2. 遍历列表，为每一张表执行删除命令
            for table in table_names:
                # 使用 f-string 构建SQL命令，并用text()包装
                # IF EXISTS 确保了即使表不存在，命令也不会报错
                drop_command = text(f"DROP TABLE IF EXISTS `{table}`;")
                connection.execute(drop_command)
                print(f"  - ✅ 表 '{table}' 已成功删除（或不存在）。")
            
            # 3. 重新开启外键检查
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            
            # 4. 提交事务，让操作生效
            connection.commit()

        print("--- 数据库表重置完毕 ---")

    except Exception as e:
        print(f"❌ 重置数据库时发生错误: {e}")
# utils.py 中

def delete_data_by_filename(db_config: dict, table_names: list, source_file_name: str):
    """
    根据源文件名，精准删除所有核心表中的现有数据。
    """
    try:
        engine = get_db_engine(db_config)
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                for table in table_names:
                    # SQL命令现在WHERE条件更精准了
                    delete_sql = text(f"DELETE FROM `{table}` WHERE source_file_name = :file_name")
                    connection.execute(delete_sql, {"file_name": source_file_name})
                    print(f"    ✅ 已清理表 '{table}' 中的旧数据")
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"    ❌ 清理旧数据时发生错误: {e}")