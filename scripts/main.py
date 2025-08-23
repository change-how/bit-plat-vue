# main.py - 虚拟币平台数据处理引擎
from pathlib import Path
import pandas as pd
import commentjson
from sqlalchemy import create_engine 
from .utils import test_database_connection, load_mapping_config, get_db_engine, write_df_to_db
from .utils import determine_company_from_filename, delete_data_by_filename
from .data_extract import extract_data_from_sources, process_single_destination
from . import transforms
from .error_handler import ETLError, ErrorType, create_user_friendly_error, handle_exception, format_error_for_frontend

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

# --- 模板文件注册表（支持多模板） ---
TEMPLATE_REGISTRY = {
    'okx': [
        Path("./config/okx_map.jsonc"),
        Path("./config/okx_map_lite.jsonc")
    ],
    'binance': [
        Path("./config/binance_map.jsonc")
    ],
    'huobi': [
        Path("./config/huobi_map.jsonc")
    ],
    'imtoken': [
        Path("./config/imtoken_map.jsonc"),
        Path("./config/imtoken_map_v2.jsonc")
    ],
    'tokenpocket': [
        Path("./config/tokenpocket_map.jsonc")
    ],
    'csv': [
        Path("./config/csv_universal_map.jsonc")
    ]
}

# --- 核心数据表列表 ---
CORE_TABLES = [
    'users',
    'transactions',
    'asset_movements',
    'login_logs',
    'devices'
]

def validate_platform_match(extracted_data: dict, platform: str, file_path: Path) -> dict:
    """
    验证提取的数据是否与选择的平台匹配
    
    Args:
        extracted_data: 提取到的数据字典
        platform: 识别的平台名称
        file_path: 文件路径
    
    Returns:
        dict: 包含验证结果的字典 {'is_match': bool, 'reason': str, 'suggestions': list}
    """
    # 检查是否有核心必需数据源被成功提取
    platform_signatures = {
        'binance': ['user_basic_info_raw', 'spot_trade_raw', 'deposit_raw', 'withdrawal_raw'],
        'okx': ['user_basic_info_raw', 'spot_trade_raw', 'funding_raw'],
        'huobi': ['user_basic_info_raw', 'spot_trade_raw', 'deposit_raw'],
        'imtoken': ['transaction_raw'],
        'tokenpocket': ['transaction_raw']
    }
    
    required_sources = platform_signatures.get(platform, [])
    found_sources = [key for key in required_sources if key in extracted_data and not (
        isinstance(extracted_data[key], pd.DataFrame) and extracted_data[key].empty
    )]
    
    # 如果找到的核心数据源太少，可能是平台不匹配
    match_ratio = len(found_sources) / len(required_sources) if required_sources else 0
    
    if match_ratio < 0.5:  # 少于50%的核心数据源匹配
        return {
            'is_match': False,
            'reason': f"文件内容与{platform}平台模板匹配度过低 ({match_ratio:.1%})",
            'suggestions': [
                f"当前模板期望找到: {', '.join(required_sources)}",
                f"实际找到: {', '.join(found_sources) if found_sources else '无'}",
                "请检查是否选择了正确的平台",
                "或确认文件是否为该平台的标准导出格式"
            ]
        }
    
    return {
        'is_match': True,
        'reason': f"匹配度: {match_ratio:.1%}",
        'suggestions': []
    }

def run_etl_process_for_file(file_path: Path, selected_company: str = None):
    """
    执行单个文件的完整ETL流程，带有详细的错误处理
    
    Args:
        file_path: 待处理文件的路径
        selected_company: 用户在前端选择的公司名称（如：'币安', '火币'等），用于验证匹配
    
    Returns:
        tuple: (是否成功, 成功消息/ETLError对象)
    """
    try:
        print("\n" + "="*80)
        print("🚀 ETL流程开始 - 新文件处理")
        print("="*80)
        print(f"📁 处理文件: {file_path.name}")
        print("="*80)

        # 步骤1：文件存在性检查
        if not file_path.exists():
            raise create_user_friendly_error(
                ErrorType.FILE_NOT_FOUND,
                details=f"文件 {file_path} 不存在"
            )

        # 步骤2：文件格式检查
        supported_extensions = ['.xlsx', '.xls', '.csv']
        if file_path.suffix.lower() not in supported_extensions:
            raise create_user_friendly_error(
                ErrorType.FILE_FORMAT_ERROR,
                details=f"文件扩展名 {file_path.suffix} 不受支持",
                custom_suggestions=[f"支持的格式: {', '.join(supported_extensions)}", "请转换文件格式后重试"]
            )

        # 步骤3：确定数据平台
        print("🔍 正在识别数据平台...")
        
        # 首先检查用户是否选择了公司
        if selected_company:
            print(f"� 用户选择的平台: {selected_company}")
            # 将前端选择映射到内部标识符
            company_mapping = {
                '欧意': 'okx',
                '币安': 'binance', 
                '火币': 'huobi',
                'ImToken': 'imtoken',
                'TokenPocket': 'tokenpocket'
            }
            user_selected_platform = company_mapping.get(selected_company)
            
            if user_selected_platform and user_selected_platform in TEMPLATE_REGISTRY:
                # 验证用户选择的平台与文件内容是否匹配
                print(f"🔧 尝试使用用户选择的平台: {user_selected_platform}")
                
                # 先检查文件名是否包含不同平台的标识
                filename_lower = file_path.name.lower()
                conflicting_platforms = []
                for platform_key in TEMPLATE_REGISTRY.keys():
                    if platform_key != user_selected_platform and platform_key != 'csv' and platform_key in filename_lower:
                        conflicting_platforms.append(platform_key)
                
                if conflicting_platforms:
                    # 文件名包含其他平台标识，提示用户可能选择错误
                    detected_platform = conflicting_platforms[0]
                    raise create_user_friendly_error(
                        ErrorType.TEMPLATE_MISMATCH,
                        details=f"您选择了'{selected_company}'，但文件名包含'{detected_platform}'平台标识",
                        custom_suggestions=[
                            f"请检查是否应该选择对应'{detected_platform}'的平台",
                            "或确认文件确实是" + selected_company + "平台的数据",
                            "文件名和平台选择应该保持一致"
                        ]
                    )
                
                company_name = user_selected_platform
                print(f"✅ 使用用户选择的平台: {company_name}")
            else:
                raise create_user_friendly_error(
                    ErrorType.COMPANY_NOT_RECOGNIZED,
                    details=f"不支持的平台选择: {selected_company}",
                    custom_suggestions=[
                        "支持的平台: 欧意、币安、火币、ImToken、TokenPocket",
                        "请选择正确的平台"
                    ]
                )
        else:
            # 用户没有选择公司，回退到文件名识别
            print("📋 用户未选择平台，尝试从文件名识别...")
            company_name = determine_company_from_filename(file_path, TEMPLATE_REGISTRY)
            
            if not company_name:
                raise create_user_friendly_error(
                    ErrorType.COMPANY_NOT_RECOGNIZED,
                    details=f"无法从文件名 '{file_path.name}' 识别数据平台",
                    custom_suggestions=[
                        "请在文件名中包含平台标识，如: okx_data.xlsx, binance_交易记录.csv",
                        "支持的平台关键词: okx, binance, huobi, imtoken, tokenpocket",
                        "或直接使用 .csv 格式让系统自动处理"
                    ]
                )
            else:
                print(f"✅ 从文件名识别到数据平台: {company_name}")
            
        # 步骤4：多模板扫描和匹配
        print("📋 正在扫描数据模板...")
        template_paths = TEMPLATE_REGISTRY[company_name]
        
        if not template_paths:
            raise create_user_friendly_error(
                ErrorType.TEMPLATE_NOT_FOUND,
                details=f"平台 '{company_name}' 没有配置模板文件",
                custom_suggestions=["联系管理员添加模板配置", "检查系统配置文件完整性"]
            )
        
        # 尝试每个模板，找到第一个匹配的
        successful_template = None
        successful_config = None
        successful_data = None
        template_errors = []
        
        print(f"    🔍 找到 {len(template_paths)} 个 {company_name} 模板，开始逐个尝试...")
        
        for i, template_path in enumerate(template_paths, 1):
            print(f"    📋 尝试模板 {i}/{len(template_paths)}: {template_path.name}")
            
            if not template_path.exists():
                error_msg = f"模板文件 {template_path} 不存在"
                template_errors.append(error_msg)
                print(f"        ❌ {error_msg}")
                continue
            
            try:
                # 加载模板配置
                mapping_config = load_mapping_config(template_path)
                if not mapping_config:
                    error_msg = f"模板文件 {template_path.name} 内容为空"
                    template_errors.append(error_msg)
                    print(f"        ❌ {error_msg}")
                    continue
                
                print(f"        ✅ 模板配置加载成功")
                
                # 尝试使用这个模板提取数据
                print(f"        🔍 测试模板匹配度...")
                extracted_data = extract_data_from_sources(
                    file_path,
                    mapping_config.get('sources', [])
                )
                
                # 验证平台匹配度
                if selected_company:
                    validation_result = validate_platform_match(extracted_data, company_name, file_path)
                    if not validation_result['is_match']:
                        error_msg = f"模板 {template_path.name}: {validation_result['reason']}"
                        template_errors.append(error_msg)
                        print(f"        ❌ {error_msg}")
                        continue
                
                # 如果到这里，说明模板匹配成功
                successful_template = template_path
                successful_config = mapping_config
                successful_data = extracted_data
                print(f"        🎯 模板 {template_path.name} 匹配成功！")
                break
                
            except ETLError as e:
                # 记录详细的错误信息
                error_msg = f"模板 {template_path.name}: {e.message}"
                if e.details:
                    error_msg += f" ({e.details})"
                template_errors.append(error_msg)
                print(f"        ❌ {error_msg}")
                continue
            except Exception as e:
                error_msg = f"模板 {template_path.name}: 处理异常 - {str(e)}"
                template_errors.append(error_msg)
                print(f"        ❌ {error_msg}")
                continue
        
        # 检查是否找到了匹配的模板
        if not successful_template:
            # 所有模板都失败了，生成结构化错误报告
            print(f"    ❌ 所有 {len(template_paths)} 个模板都不匹配")
            
            # 生成简洁的主要错误信息
            main_error = f"尝试了 {len(template_paths)} 个 {company_name.upper()} 平台模板，均无法匹配您的文件"
            
            # 构建结构化的错误详情（为前端优化格式）
            structured_details = {
                "summary": main_error,
                "template_count": len(template_paths),
                "platform": company_name.upper(),
                "template_errors": []
            }
            
            # 处理每个模板的错误信息
            for i, (template_path, error) in enumerate(zip(template_paths, template_errors), 1):
                template_name = template_path.name.replace('.jsonc', '').replace('_map', '').replace(f'{company_name}_', '')
                
                # 尝试从模板文件中读取自定义显示名称
                display_name = None
                try:
                    if template_path.exists():
                        mapping_config = load_mapping_config(template_path)
                        if mapping_config and 'metadata' in mapping_config:
                            metadata = mapping_config['metadata']
                            # 优先使用 display_name，然后是 description，最后是 version
                            display_name = metadata.get('display_name') or metadata.get('description')
                            if display_name:
                                # 如果有版本信息，添加到显示名称中
                                version = metadata.get('version')
                                if version:
                                    display_name = f"{display_name} (v{version})"
                except Exception:
                    # 如果读取模板失败，使用默认逻辑
                    pass
                
                # 如果没有自定义名称，使用文件名推断
                if not display_name:
                    if template_name.endswith('_lite'):
                        display_name = f"{company_name.upper()} 简化版"
                    elif template_name.endswith('_v2'):
                        display_name = f"{company_name.upper()} V2版"
                    elif template_name.endswith('_full'):
                        display_name = f"{company_name.upper()} 完整版"
                    else:
                        display_name = f"{company_name.upper()} 标准版"
                
                # 提取错误的核心信息
                if "缺少" in error and "工作表" in error:
                    # 工作表缺失错误 - 提取数字和工作表名称
                    import re
                    match = re.search(r'缺少(\d+)个工作表[:：]?(.*)?\(', error)
                    if match:
                        count = match.group(1)
                        sheets_part = match.group(2) if match.group(2) else ""
                        if sheets_part and "【" in sheets_part:
                            # 提取具体的工作表名称
                            sheet_names = re.findall(r'【([^】]+)】', sheets_part)
                            if sheet_names:
                                # 显示所有工作表名称，不做截断
                                sheets_text = "、".join(sheet_names)
                                error_summary = f"缺少工作表：{sheets_text}"
                            else:
                                error_summary = f"缺少 {count} 个必需工作表"
                        else:
                            error_summary = f"缺少 {count} 个必需工作表"
                    else:
                        error_summary = "工作表结构不匹配"
                else:
                    # 其他类型错误
                    if ":" in error:
                        error_summary = error.split(":", 1)[1].strip()
                    else:
                        error_summary = "模板格式不匹配"
                
                structured_details["template_errors"].append({
                    "template_name": display_name,
                    "error_summary": error_summary,
                    "original_file": template_path.name
                })
            
            # 生成简化的建议
            suggestions = [
                "🔍 模板匹配结果：",
                f"已尝试 {company_name.upper()} 平台的所有 {len(template_paths)} 个模板版本",
                "",
                "💡 解决方案：",
                "• 确认选择的交易平台是否正确",
                "• 检查文件是否为官方标准导出格式", 
                "• 确保文件包含所有必需的工作表",
                "• 重新从交易平台导出完整数据"
            ]
            
            # 将结构化信息转换为字符串（供details字段使用）
            import json
            details_json = json.dumps(structured_details, ensure_ascii=False, indent=2)
            
            raise create_user_friendly_error(
                ErrorType.TEMPLATE_MISMATCH,
                details=details_json,
                custom_suggestions=suggestions
            )
        
        # 使用成功匹配的模板继续处理
        mapping_config = successful_config
        extracted_data = successful_data
        print(f"✅ 使用模板: {successful_template.name}")
        print(f"✅ 成功加载 {company_name} 平台的数据模板")
            
        print("\n" + "-"*60)
        print("🔗 步骤1: 数据库连接测试")
        print("-"*60)
        # 步骤5：测试数据库连接
        try:
            test_database_connection(DB_CONFIG)
        except Exception as e:
            raise create_user_friendly_error(
                ErrorType.DB_CONNECTION_ERROR,
                details=f"数据库连接失败: {str(e)}",
                custom_suggestions=[
                    "检查数据库服务是否正在运行",
                    "确认数据库连接配置是否正确",
                    "检查网络连接状态",
                    "联系管理员检查数据库状态"
                ]
            )

        print("\n" + "-"*60)
        print("🗑️ 步骤2: 清理旧数据")
        print("-"*60)
        # 步骤6：清理旧数据
        try:
            delete_data_by_filename(DB_CONFIG, CORE_TABLES, file_path.name)
        except Exception as e:
            print(f"⚠️ 清理旧数据时出现问题: {str(e)}")
            print("继续处理新数据...")
        
        print("\n" + "-"*60)
        print("📊 步骤3: 数据验证完成")
        print("-"*60)
        # 数据已经在模板匹配过程中提取和验证了
        print(f"✅ 数据提取完成，使用模板: {successful_template.name}")
        
        if not extracted_data:
            raise create_user_friendly_error(
                ErrorType.FILE_EMPTY,
                details="从文件中未提取到任何有效数据",
                custom_suggestions=["检查文件是否包含数据", "确认文件格式是否正确", "检查工作表是否为空"]
            )
        else:
            total_records = sum(len(df) for df in extracted_data.values() if isinstance(df, pd.DataFrame))
            print(f"✅ 成功提取数据，共 {total_records} 条记录")
            
        print("\n" + "-"*60)
        print("💾 步骤4: 数据转换和写入数据库")
        print("-"*60)
        # 步骤8：处理每个目标表
        processed_tables = []
        for destination in mapping_config.get('destinations', []):
            target_table_name = destination.get('target_table')
            print(f"  📝 正在处理目标表: '{target_table_name}'")

            try:
                # 处理数据并转换
                final_df = process_single_destination(
                    destination,
                    extracted_data,
                    FUNCTION_REGISTRY,
                    file_path.name
                )
                
                if final_df is not None and not final_df.empty:
                    # 写入数据库
                    write_df_to_db(final_df, target_table_name, DB_CONFIG)
                    processed_tables.append(target_table_name)
                    print(f"  ✅ 表 '{target_table_name}' 处理完成，写入 {len(final_df)} 条记录")
                else:
                    print(f"  ⚠️ 表 '{target_table_name}' 没有数据需要写入")
                    
            except KeyError as e:
                raise create_user_friendly_error(
                    ErrorType.COLUMN_MISSING,
                    details=f"处理表 '{target_table_name}' 时缺少必需字段: {str(e)}",
                    custom_suggestions=[
                        f"检查文件中是否包含字段: {str(e)}",
                        "确认列名拼写是否正确",
                        "检查数据模板配置是否匹配文件格式"
                    ]
                )
            except Exception as e:
                error_msg = str(e).lower()
                if 'database' in error_msg or 'connection' in error_msg:
                    raise create_user_friendly_error(
                        ErrorType.DB_WRITE_ERROR,
                        details=f"写入表 '{target_table_name}' 失败: {str(e)}",
                        custom_suggestions=["检查数据库连接", "确认数据库有足够空间", "检查数据格式是否正确"]
                    )
                else:
                    raise create_user_friendly_error(
                        ErrorType.DATA_TRANSFORMATION_ERROR,
                        details=f"数据转换失败: {str(e)}",
                        custom_suggestions=["检查数据格式是否正确", "确认数据类型匹配", "删除异常数据行"]
                    )
        
        print("\n" + "="*80)
        print("🎉 ETL流程完成！")
        print("="*80)
        success_msg = f"文件 '{file_path.name}' 成功处理，共更新 {len(processed_tables)} 个数据表: {', '.join(processed_tables)}"
        print(success_msg)
        return True, success_msg
                
    except ETLError as e:
        # 返回ETL错误对象，而不是重新抛出
        print(f"\n❌ ETL处理错误: {e.message}")
        if e.details:
            print(f"详细信息: {e.details}")
        return False, e
    except Exception as e:
        # 捕获所有未预期的错误
        error_obj = create_user_friendly_error(
            ErrorType.UNKNOWN_ERROR,
            details=f"处理文件 {file_path.name} 时发生未知错误: {str(e)}",
            custom_suggestions=["请联系技术支持", "提供完整的错误信息以便排查"]
        )
        print(f"\n❌ 未知错误: {error_obj.message}")
        print(f"详细信息: {error_obj.details}")
        return False, error_obj

# --- 开发测试入口 ---
if __name__ == '__main__':
    print("main.py: 此文件现在主要提供 run_etl_process_for_file() 函数供 Flask 应用调用。")
    print("如需测试处理流程，请通过 web 界面上传文件或直接调用 run_etl_process_for_file() 函数。")
