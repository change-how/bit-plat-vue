# data_extract.py - 数据处理车间 (V8 - 完整支持CSV的4种识别方法)

from pathlib import Path
import pandas as pd
import json
from decimal import Decimal

# --- 辅助函数 (保持不变) ---
def find_field_from_aliases(columns, aliases):
    for alias in aliases:
        if alias in columns:
            return alias
    return None

# --- 高级解析工具 (新增一个 + 优化一个) ---

def _find_subtable_start_row(sheet_df: pd.DataFrame, section_header_aliases: list, header_offset: int) -> int:
    """
    (V3 - "多路标"版) 
    在工作表中，根据一个"路标"别名列表，依次尝试寻找，并返回第一个匹配到的子表的表头行号。
    """
    # --- 核心升级：遍历"路标"列表 ---
    for header in section_header_aliases:
        print(f"  - 尝试定位路标: '{header}'...")
        matches = sheet_df.stack() == header
        true_matches = matches[matches].index

        if len(true_matches) > 0:
            # 只要找到了第一个，就立刻返回结果，不再继续寻找！
            header_row_index = true_matches[0][0]
            print(f"    ✅ 成功！在第 {header_row_index} 行找到了精确匹配的路标。")
            return header_row_index + header_offset
    
    # 如果把列表里所有路标都试完了，还是没找到
    print(f"  - 🟡 警告: 在工作表中未能找到任何一个指定的路标: {section_header_aliases}。")
    return None

def _parse_tabular_subtable(sheet_df: pd.DataFrame, section_header_aliases: list, header_offset: int) -> pd.DataFrame:
    """
    (V2 - 智能结束版) 
    解析一个标准的多行子表。能够通过寻找全空行来智能判断子表的结束位置。
    """
    header_row = _find_subtable_start_row(sheet_df, section_header_aliases, header_offset)
    if header_row is None:
        return pd.DataFrame()
    
    # --- 核心升级：智能判断结束位置 ---
    potential_data = sheet_df.iloc[header_row + 1:]
    
    try:
        first_empty_row_index = potential_data.isnull().all(axis=1).eq(True).idxmax()
        if potential_data.loc[first_empty_row_index].isnull().all():
             end_index = first_empty_row_index
        else:
             end_index = None
    except ValueError:
        end_index = None

    if end_index is not None:
        actual_data = potential_data.loc[:end_index-1]
    else:
        actual_data = potential_data
        
    sub_table = actual_data.copy()
    sub_table.columns = sheet_df.iloc[header_row].values
    sub_table.reset_index(drop=True, inplace=True)
    sub_table.dropna(how='all', inplace=True)
    
    return sub_table

def _parse_form_subtable(sheet_df: pd.DataFrame, section_header_aliases: list, header_offset: int) -> dict:
    header_row = _find_subtable_start_row(sheet_df, section_header_aliases, header_offset)
    if header_row is None: 
        return {}
    
    data_row_index = header_row + 1
    
    form_data = pd.Series(
        sheet_df.iloc[data_row_index].values,
        index=sheet_df.iloc[header_row].values
    ).to_dict()
    
    return form_data

def _parse_merged_key_value(sheet_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    merged_cols = config['merged_columns']
    key_col = config['key_column']
    value_col = config['value_column']
    
    sheet_df[merged_cols] = sheet_df[merged_cols].fillna(method='ffill')
    sheet_df.dropna(subset=[merged_cols[0]], inplace=True)
    
    output_records = []
    for group_keys, group_df in sheet_df.groupby(merged_cols):
        record = dict(zip(merged_cols, group_keys))
        extra_data = group_df[[key_col, value_col]].dropna(subset=[key_col]).set_index(key_col).to_dict()[value_col]
        
        # print(f"\n--- [诊断探针#1A] 解析器为设备 '{record.get('Device Name 设备名称')}' 生成的 extra_data ---")
        # print(extra_data)
        
        record['extra_data'] = extra_data
        output_records.append(record)
        
    final_df = pd.DataFrame(output_records)
    
    # print(f"\n--- [诊断探针#1B] 解析器最终生成的DataFrame预览 (应包含extra_data列) ---")
    # print(final_df.head().to_string())
    
    return final_df

# --- CSV编码检测函数 ---
def _detect_csv_encoding(file_path: Path) -> str:
    """
    检测CSV文件的编码格式
    """
    # 常见的编码列表，按优先级排序
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin1', 'cp1252']
    
    for encoding in encodings:
        try:
            # 尝试读取前几行来验证编码
            with open(file_path, 'r', encoding=encoding) as f:
                f.read(1000)  # 读取前1000个字符测试
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # 如果都失败了，返回默认编码
    return 'utf-8'

# --- CSV专用解析函数 ---

def _parse_form_subtable_csv(csv_df: pd.DataFrame, section_header_aliases: list, header_offset: int) -> dict:
    """
    CSV版本的表单解析函数
    """
    header_row = _find_subtable_start_row(csv_df, section_header_aliases, header_offset)
    if header_row is None: 
        return {}
    
    data_row_index = header_row + 1
    if data_row_index >= len(csv_df):
        return {}
    
    form_data = pd.Series(
        csv_df.iloc[data_row_index].values,
        index=csv_df.iloc[header_row].values
    ).to_dict()
    
    return form_data

def _parse_tabular_subtable_csv(csv_df: pd.DataFrame, section_header_aliases: list, header_offset: int) -> pd.DataFrame:
    """
    CSV版本的动态子表解析函数
    """
    header_row = _find_subtable_start_row(csv_df, section_header_aliases, header_offset)
    if header_row is None:
        return pd.DataFrame()
    
    potential_data = csv_df.iloc[header_row + 1:]
    
    try:
        first_empty_row_index = potential_data.isnull().all(axis=1).eq(True).idxmax()
        if potential_data.loc[first_empty_row_index].isnull().all():
             end_index = first_empty_row_index
        else:
             end_index = None
    except ValueError:
        end_index = None

    if end_index is not None:
        actual_data = potential_data.loc[:end_index-1]
    else:
        actual_data = potential_data
        
    sub_table = actual_data.copy()
    sub_table.columns = csv_df.iloc[header_row].values
    sub_table.reset_index(drop=True, inplace=True)
    sub_table.dropna(how='all', inplace=True)
    
    return sub_table

def _parse_merged_key_value_csv(csv_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    CSV版本的复杂三维表解析函数
    """
    merged_cols = config['merged_columns']
    key_col = config['key_column']
    value_col = config['value_column']
    
    # 先设置正确的列名
    if 'header_row' in config:
        header_row = config['header_row'] - 1
        csv_df.columns = csv_df.iloc[header_row].values
        csv_df = csv_df.iloc[header_row + 1:].reset_index(drop=True)
    
    csv_df[merged_cols] = csv_df[merged_cols].fillna(method='ffill')
    csv_df.dropna(subset=[merged_cols[0]], inplace=True)
    
    output_records = []
    for group_keys, group_df in csv_df.groupby(merged_cols):
        record = dict(zip(merged_cols, group_keys))
        extra_data = group_df[[key_col, value_col]].dropna(subset=[key_col]).set_index(key_col).to_dict()[value_col]
        
        # print(f"\n--- [CSV诊断探针#1A] 解析器为设备 '{record.get('Device Name 设备名称')}' 生成的 extra_data ---")
        # print(extra_data)
        
        record['extra_data'] = extra_data
        output_records.append(record)
        
    final_df = pd.DataFrame(output_records)
    
    # print(f"\n--- [CSV诊断探针#1B] 解析器最终生成的DataFrame预览 (应包含extra_data列) ---")
    # print(final_df.head().to_string())
    
    return final_df

# --- 核心"取货员"函数 (升级版) ---
def extract_data_from_sources(excel_path: Path, sources_config: list) -> dict:
    """
    (V9版 - 严格验证版)
    能够根据文件后缀名，智能选择Excel或CSV的解析策略。
    新增：严格验证所有sources都必须成功提取数据，否则抛出异常。
    """
    extracted_data = {}
    failed_sources = []  # 记录失败的数据源
    success_sources = []  # 记录成功的数据源
    available_sheets = []  # 初始化可用工作表列表，确保在整个函数中都可用
    file_extension = excel_path.suffix.lower()

    print(f"    📋 需要提取 {len(sources_config)} 个数据源")
    for source in sources_config:
        source_id = source.get('source_id', 'unknown')
        print(f"    - {source_id}: {source.get('worksheet_name', 'CSV数据')}")

    # --- ✨ 核心改造：根据文件类型选择不同的读取策略 ✨ ---
    if file_extension == '.csv':
        # --- CSV 文件处理逻辑 (支持4种识别方法和编码检测) ---
        print(f"    📄 解析CSV文件: {excel_path.name}")
        
        # 首先检测文件编码
        detected_encoding = _detect_csv_encoding(excel_path)
        print(f"    🔍 文件编码: {detected_encoding}")
        
        try:
            # 使用检测到的编码读取整个CSV文件作为原始数据
            csv_df = pd.read_csv(excel_path, header=None, encoding=detected_encoding)  # 不设置header，保持原始结构
            
            # 遍历配置中的每个数据源，根据layout类型进行处理
            for source in sources_config:
                source_id = source['source_id']
                layout = source.get('data_layout', 'tabular')
                print(f"    📋 处理数据源: '{source_id}' ({layout})")
                
                try:
                    # --- CSV调度中心：根据布局类型选择处理方法 ---
                    if layout == 'tabular':
                        # 标准表格：使用指定的header_row
                        header_row = source.get('header_row', 1) - 1  # 转换为0-based索引
                        df = csv_df.copy()
                        if header_row < len(csv_df):
                            df.columns = csv_df.iloc[header_row].values  # 设置表头
                            df = df.iloc[header_row + 1:].reset_index(drop=True)  # 去掉表头行
                            df.dropna(how='all', inplace=True)  # 清理空行
                        else:
                            df = pd.DataFrame()
                        
                    elif layout == 'form_layout':
                        # 表单布局：寻找特定标题并解析键值对
                        header_aliases = source.get('section_header_aliases', [])
                        header_offset = source.get('header_offset', 1)
                        df = _parse_form_subtable_csv(csv_df, header_aliases, header_offset)
                        
                    elif layout == 'find_subtable_by_header':
                        # 动态子表：寻找特定标题下的表格数据
                        header_aliases = source.get('section_header_aliases', [])
                        header_offset = source.get('header_offset', 1)
                        df = _parse_tabular_subtable_csv(csv_df, header_aliases, header_offset)
                        
                    elif layout == 'merged_key_value':
                        # 复杂三维表：处理合并单元格和键值对
                        df = _parse_merged_key_value_csv(csv_df, source)
                        
                    else:
                        print(f"  - 🟡 警告: 未知的CSV布局类型 '{layout}'，使用默认tabular处理。")
                        # 默认按标准表格处理
                        header_row = source.get('header_row', 1) - 1
                        df = csv_df.copy()
                        if header_row < len(csv_df):
                            df.columns = csv_df.iloc[header_row].values
                            df = df.iloc[header_row + 1:].reset_index(drop=True)
                            df.dropna(how='all', inplace=True)
                        else:
                            df = pd.DataFrame()
                    
                    # ✅ 智能验证：区分必需和可选数据源
                    is_data_empty = df is None or (isinstance(df, pd.DataFrame) and df.empty) or (isinstance(df, dict) and not df)
                    
                    # 定义可选数据源（这些数据源为空时不应该导致整个处理失败）
                    optional_sources = ['p2p_trade_raw', 'otc_trade_raw', 'margin_trade_raw', 'pay_trade_raw']
                    
                    if is_data_empty:
                        if source_id in optional_sources:
                            # 可选数据源为空时，记录警告但继续处理
                            print(f"        🟡 警告：可选数据源 '{source_id}' 无数据，跳过处理")
                            extracted_data[source_id] = pd.DataFrame()  # 存储空DataFrame，避免后续处理报错
                        else:
                            # 必需数据源为空时，记录为失败
                            failed_sources.append({
                                'source_id': source_id,
                                'reason': f"CSV数据源 '{source_id}' 未找到数据或为空",
                                'layout': layout
                            })
                            print(f"        ❌ 数据源 '{source_id}' 提取失败：无数据")
                    else:
                        extracted_data[source_id] = df
                        success_sources.append(source_id)
                        
                        # --- 📊 简化数据概览 ---
                        if isinstance(df, pd.DataFrame):
                            print(f"        ✅ 提取到 {df.shape[0]} 行 × {df.shape[1]} 列数据")
                            if not df.empty:
                                # 只显示前3个字段的示例数据，避免输出过长
                                sample_data = {}
                                for i, (k, v) in enumerate(df.iloc[0].items()):
                                    if i >= 3:  # 只显示前3个字段
                                        break
                                    sample_data[k] = str(v)[:20] + "..." if len(str(v)) > 20 else str(v)
                                print(f"        📋 表头: {list(df.columns)[:5]}...")
                        elif isinstance(df, dict):
                            print(f"        ✅ 提取到字典数据: {len(df)} 个键")
                        else:
                            print(f"        ✅ 提取到数据: {type(df)}")
                            
                except Exception as e:
                    failed_sources.append({
                        'source_id': source_id,
                        'reason': f"处理CSV数据源 '{source_id}' 时出错: {str(e)}",
                        'layout': layout
                    })
                    print(f"        ❌ 数据源 '{source_id}' 处理异常: {str(e)}")
        
        except Exception as e:
            print(f"    ❌ 读取CSV文件时出错: {e}")
            # 将所有源都标记为失败
            for source in sources_config:
                failed_sources.append({
                    'source_id': source.get('source_id', 'unknown'),
                    'reason': f"无法读取CSV文件: {str(e)}",
                    'layout': source.get('data_layout', 'unknown')
                })
            
    elif file_extension in ['.xls', '.xlsx']:
        # --- Excel 文件处理逻辑 (增强验证) ---
        print(f"    📊 解析Excel文件: {excel_path.name}")
        try:
            xls = pd.ExcelFile(excel_path)
            available_sheets = xls.sheet_names
            print(f"    📋 文件包含工作表: {available_sheets}")
        except FileNotFoundError:
            print(f"    ❌ 文件未找到: {excel_path}")
            # 将所有源都标记为失败
            for source in sources_config:
                failed_sources.append({
                    'source_id': source.get('source_id', 'unknown'),
                    'reason': f"Excel文件未找到: {excel_path}",
                    'layout': source.get('data_layout', 'unknown')
                })
            return None
        except Exception as e:
            print(f"    ❌ 无法打开Excel文件: {e}")
            # 将所有源都标记为失败
            for source in sources_config:
                failed_sources.append({
                    'source_id': source.get('source_id', 'unknown'),
                    'reason': f"无法打开Excel文件: {str(e)}",
                    'layout': source.get('data_layout', 'unknown')
                })
            return None

        for source in sources_config:
            source_id = source.get('source_id', 'unknown')
            
            # 安全获取工作表名
            if 'worksheet_name' not in source:
                failed_sources.append({
                    'source_id': source_id,
                    'reason': f"模板配置错误：数据源 '{source_id}' 缺少 worksheet_name 字段",
                    'layout': source.get('data_layout', 'unknown')
                })
                print(f"    ❌ 模板配置错误：数据源 '{source_id}' 缺少工作表名配置")
                continue
                
            sheet_name = source['worksheet_name']
            layout = source.get('data_layout', 'tabular')
            print(f"    📄 读取工作表: '{sheet_name}' ({layout})")
            
            try:
                # 首先检查工作表是否存在
                if sheet_name not in available_sheets:
                    failed_sources.append({
                        'source_id': source_id,
                        'reason': f"工作表 '{sheet_name}' 不存在",
                        'sheet_name': sheet_name,
                        'available_sheets': available_sheets,
                        'layout': layout
                    })
                    print(f"        ❌ 工作表 '{sheet_name}' 不存在！")
                    print(f"        📋 可用工作表: {available_sheets}")
                    continue
                
                # --- 调度中心 ---
                if layout == 'tabular':
                    df = pd.read_excel(xls, sheet_name=sheet_name, header=source.get('header_row', 1) - 1, nrows=source.get('nrows', None))
                
                elif layout == 'merged_key_value':
                    raw_df = pd.read_excel(xls, sheet_name=sheet_name, header=source.get('header_row', 1) - 1)
                    df = _parse_merged_key_value(raw_df, source)
                    
                else: # 处理 find_subtable_by_header 和 form_layout
                    full_sheet_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                    header_aliases = source.get('section_header_aliases', []) 
                    
                    if layout == 'find_subtable_by_header':
                        df = _parse_tabular_subtable(full_sheet_df, header_aliases, source['header_offset'])
                    elif layout == 'form_layout':
                        df = _parse_form_subtable(full_sheet_df, header_aliases, source['header_offset'])
                    else:
                        print(f"        🟡 警告: 未知布局类型 '{layout}'，跳过")
                        df = pd.DataFrame()
                
                # ✅ 智能验证：区分必需和可选数据源
                is_data_empty = df is None or (isinstance(df, pd.DataFrame) and df.empty) or (isinstance(df, dict) and not df)
                
                # 定义可选数据源（这些数据源为空时不应该导致整个处理失败）
                optional_sources = ['p2p_trade_raw', 'otc_trade_raw', 'margin_trade_raw', 'pay_trade_raw']
                
                if is_data_empty:
                    if source_id in optional_sources:
                        # 可选数据源为空时，记录警告但继续处理
                        print(f"        🟡 警告：可选数据源 '{source_id}' 无数据，跳过处理")
                        extracted_data[source_id] = pd.DataFrame()  # 存储空DataFrame，避免后续处理报错
                    else:
                        # 必需数据源为空时，记录为失败
                        failed_sources.append({
                            'source_id': source_id,
                            'reason': f"工作表 '{sheet_name}' 中未找到有效数据",
                            'sheet_name': sheet_name,
                            'layout': layout
                        })
                        print(f"        ❌ 数据源 '{source_id}' 提取失败：工作表 '{sheet_name}' 无有效数据")
                else:
                    extracted_data[source_id] = df
                    success_sources.append(source_id)
                    
                    # --- 📊 简化数据概览 ---
                    if isinstance(df, pd.DataFrame):
                        print(f"        ✅ 提取到 {df.shape[0]} 行 × {df.shape[1]} 列数据")
                        if not df.empty:
                            print(f"        📋 表头: {list(df.columns)[:5]}...")
                    elif isinstance(df, dict):
                        print(f"        ✅ 提取到字典数据: {len(df)} 个键")
                    else:
                        print(f"        ✅ 提取到数据: {type(df)}")
                        
            except Exception as e:
                failed_sources.append({
                    'source_id': source_id,
                    'reason': f"处理工作表 '{sheet_name}' 时出错: {str(e)}",
                    'sheet_name': sheet_name,
                    'layout': layout
                })
                print(f"        ❌ 数据源 '{source_id}' 处理异常: {str(e)}")
                
    else:
        print(f"    🟡 警告: 不支持的文件类型 '{file_extension}'，跳过文件")
        for source in sources_config:
            failed_sources.append({
                'source_id': source.get('source_id', 'unknown'),
                'reason': f"不支持的文件类型: {file_extension}",
                'layout': source.get('data_layout', 'unknown')
            })
        return None
    
    # ✅ 智能最终验证：只对核心必需数据源进行严格检查
    total_sources = len(sources_config)
    success_count = len(success_sources)
    failed_count = len(failed_sources)
    
    # 定义可选数据源
    optional_sources = ['p2p_trade_raw', 'otc_trade_raw', 'margin_trade_raw', 'pay_trade_raw']
    
    # 过滤出真正关键的失败（排除可选数据源的失败）
    critical_failures = [f for f in failed_sources if f['source_id'] not in optional_sources]
    
    print(f"    📊 数据源提取结果: 成功 {success_count}/{total_sources}")
    
    if failed_sources:
        print(f"    ❌ 失败的数据源 ({failed_count}):")
        for failed in failed_sources:
            source_id = failed['source_id']
            is_optional = source_id in optional_sources
            status_icon = "🟡" if is_optional else "❌"
            status_text = "(可选)" if is_optional else "(必需)"
            print(f"        {status_icon} {source_id} {status_text}: {failed['reason']}")
    
    # 只有当核心必需数据源失败时才抛出错误
    if critical_failures:
        # 抛出自定义异常，包含详细的失败信息
        from .error_handler import ETLError, ErrorType
        
        failed_details = []
        missing_sheets = []
        missing_worksheets_info = []
        
        for failed in critical_failures:
            if 'sheet_name' in failed:
                missing_sheets.append(failed['sheet_name'])
                # 收集缺失工作表的详细信息
                missing_worksheets_info.append({
                    'sheet_name': failed['sheet_name'],
                    'source_id': failed['source_id'],
                    'reason': failed['reason']
                })
            failed_details.append(f"• {failed['source_id']}: {failed['reason']}")
        
        if missing_sheets:
            # 生成用户友好的错误信息
            missing_count = len(missing_sheets)
            if missing_count == 1:
                sheet_name = missing_sheets[0]
                error_message = f"您的Excel文件中缺少【{sheet_name}】工作表"
                details = f"系统需要读取名为【{sheet_name}】的工作表，但在您上传的文件中没有找到这个工作表。"
            else:
                # 显示所有缺失的工作表，不做截断
                sheet_list = '】、【'.join(missing_sheets)
                error_message = f"您的Excel文件中缺少{missing_count}个工作表：【{sheet_list}】"
                details = f"系统需要读取以下工作表：【{sheet_list}】，但在您上传的文件中没有找到这些工作表。"
            
            # 生成详细的建议
            suggestions = [
                f"🔍 请检查您的Excel文件是否包含以下工作表：",
                f"   缺少的工作表：【{', '.join(missing_sheets)}】",
                "",
                f"📋 您的文件当前包含的工作表：",
                f"   {', '.join(available_sheets)}",
                "",
                "💡 可能的解决方案：",
                "   • 确认工作表名称拼写是否正确（注意区分大小写）",
                "   • 检查是否选择了正确的交易平台",
                "   • 重新从交易平台导出完整的数据文件",
                "   • 确认您选择的平台与文件内容是否匹配"
            ]
        else:
            error_message = "文件数据提取失败"
            details = "系统无法从您上传的文件中提取到必需的数据。这可能是因为文件格式不正确或文件内容不完整。"
            suggestions = [
                "💡 请尝试以下解决方案：",
                "   • 检查文件格式是否为Excel(.xlsx/.xls)格式",
                "   • 确认文件内容完整，没有损坏",
                "   • 重新从交易平台导出数据文件",
                "   • 确认选择的交易平台与文件内容匹配"
            ]
        
        raise ETLError(
            error_type=ErrorType.DATA_VALIDATION_ERROR,
            message=error_message,
            details=details,
            suggestions=suggestions
        )
    else:
        # 即使有可选数据源失败，只要核心数据源成功就继续处理
        if failed_sources:
            print("    🟡 注意：部分可选数据源无数据，但核心数据源完整，继续处理...")
        else:
            print("    🎯 所有数据源提取成功！")
    return extracted_data

def process_single_destination(destination_config: dict, all_extracted_data: dict, function_registry: dict, source_file_name: str) -> pd.DataFrame:
    """
    (V5版 - 智能处理版)
    能够智能地判断主数据源是多行表格(DataFrame)还是单条记录(dict)。
    """
    primary_source_name = destination_config.get('primary_source')
    primary_data = all_extracted_data.get(primary_source_name)

    if primary_data is None:
        print(f"  - ❌ 错误: 未找到主数据源 '{primary_source_name}'。")
        return None
    
    output_rows = []
    
    # --- 核心升级：判断原材料是"多行表格"还是"单条记录" ---
    if isinstance(primary_data, pd.DataFrame):
        # 如果是多行表格，我们像以前一样，逐行处理
        for index, source_row in primary_data.iterrows():
            new_row = _process_one_row(destination_config, source_row, primary_data.columns, all_extracted_data, function_registry, source_file_name)
            output_rows.append(new_row)
    elif isinstance(primary_data, dict):
        # 如果是单条记录（字典），我们只处理一次，不需要循环！
        # 我们把这个字典包装成pandas的Series，让下游函数可以统一处理
        source_row = pd.Series(primary_data)
        new_row = _process_one_row(destination_config, source_row, primary_data.keys(), all_extracted_data, function_registry, source_file_name)
        output_rows.append(new_row)
    
    return pd.DataFrame(output_rows)

def _process_one_row(destination_config, source_row, source_columns, all_extracted_data, function_registry, source_file_name):
    """
    (最终版) 负责处理单行数据的完整映射逻辑。
    """
    mappings = destination_config.get('mappings', [])
    standard_fields = {'source_file_name': source_file_name}
    
    extra_fields = source_row.get('extra_data', {})
    if not isinstance(extra_fields, dict):
        extra_fields = {}

    for rule in mappings:
        target_field = rule['target_field']
        raw_value = None
        
        if 'static_value' in rule:
            raw_value = rule['static_value']
        elif 'lookup_source' in rule:
            lookup_data = all_extracted_data.get(rule['lookup_source'])
            is_lookup_data_valid = False
            if isinstance(lookup_data, dict) and lookup_data:
                is_lookup_data_valid = True
            elif isinstance(lookup_data, pd.DataFrame) and not lookup_data.empty:
                is_lookup_data_valid = True
            if is_lookup_data_valid:
                lookup_row = pd.Series(lookup_data) if isinstance(lookup_data, dict) else lookup_data.iloc[0]
                field_name = find_field_from_aliases(lookup_row.index, rule.get('source_field_aliases', []))
                if field_name:
                    raw_value = lookup_row.get(field_name)
        else:
            field_name = find_field_from_aliases(source_columns, rule.get('source_field_aliases', []))
            if field_name:
                raw_value = source_row.get(field_name)

        transformed_value = raw_value
        for trans in rule.get('transformations', []):
            func = function_registry.get(trans['function'])
            if func:
                transformed_value = func(transformed_value)

        if rule.get('in_extra', False):
            extra_fields[target_field] = transformed_value
        else:
            standard_fields[target_field] = transformed_value
    
    if extra_fields:
        def _json_converter(o):
            if pd.isna(o):
                return None
            if isinstance(o, pd.Timestamp):
                return o.isoformat()
            if isinstance(o, Decimal):
                return str(o)
            if hasattr(o, 'item'):
                return o.item()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
        
        sanitized_extra_fields = {k: _sanitize_for_json(v) for k, v in extra_fields.items()}
        standard_fields['extra_data'] = json.dumps(sanitized_extra_fields, default=_json_converter, ensure_ascii=False)
    
    return standard_fields

def _sanitize_for_json(obj):
    """
    (全新的"深度清洁"工具)
    递归地遍历一个字典或列表，将所有Pandas的空值(nan, NaT等)都替换成None。
    """
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_for_json(elem) for elem in obj]
    elif pd.isna(obj):
        return None
    return obj
