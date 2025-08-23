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
        
        print(f"\n--- [诊断探针#1A] 解析器为设备 '{record.get('Device Name 设备名称')}' 生成的 extra_data ---")
        print(extra_data)
        
        record['extra_data'] = extra_data
        output_records.append(record)
        
    final_df = pd.DataFrame(output_records)
    
    print(f"\n--- [诊断探针#1B] 解析器最终生成的DataFrame预览 (应包含extra_data列) ---")
    print(final_df.head().to_string())
    
    return final_df

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
        
        print(f"\n--- [CSV诊断探针#1A] 解析器为设备 '{record.get('Device Name 设备名称')}' 生成的 extra_data ---")
        print(extra_data)
        
        record['extra_data'] = extra_data
        output_records.append(record)
        
    final_df = pd.DataFrame(output_records)
    
    print(f"\n--- [CSV诊断探针#1B] 解析器最终生成的DataFrame预览 (应包含extra_data列) ---")
    print(final_df.head().to_string())
    
    return final_df

# --- 核心"取货员"函数 (升级版) ---
def extract_data_from_sources(excel_path: Path, sources_config: list) -> dict:
    """
    (V8版 - 完整支持CSV的4种识别方法)
    能够根据文件后缀名，智能选择Excel或CSV的解析策略。
    """
    print(f"\n--- 正在从 {excel_path.name} 提取数据块 ---")
    extracted_data = {}
    file_extension = excel_path.suffix.lower()

    # --- ✨ 核心改造：根据文件类型选择不同的读取策略 ✨ ---
    if file_extension == '.csv':
        # --- CSV 文件处理逻辑 (支持4种识别方法) ---
        print(f"  - 检测到CSV文件，正在解析...")
        try:
            # 首先读取整个CSV文件作为原始数据
            csv_df = pd.read_csv(excel_path, header=None)  # 不设置header，保持原始结构
            
            # 遍历配置中的每个数据源，根据layout类型进行处理
            for source in sources_config:
                source_id = source['source_id']
                layout = source.get('data_layout', 'tabular')
                print(f"  - 正在处理CSV数据源: '{source_id}' (布局类型: {layout})")
                
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
                
                extracted_data[source_id] = df
                print(f"    - ✅ CSV数据源 '{source_id}' 处理完成，获得 {len(df)} 行数据")
        
        except Exception as e:
            print(f"  - ❌ 读取CSV文件 '{excel_path.name}' 时出错: {e}")
            return None
            
    elif file_extension in ['.xls', '.xlsx']:
        # --- Excel 文件处理逻辑 (保持不变) ---
        try:
            xls = pd.ExcelFile(excel_path)
        except FileNotFoundError:
            print(f"  - ❌ 文件未找到: {excel_path}")
            return None

        for source in sources_config:
            sheet_name = source['worksheet_name']
            layout = source.get('data_layout', 'tabular')
            print(f"  - 正在读取工作表: '{sheet_name}' (ID: '{source['source_id']}', 布局: {layout})")
            
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
                    print(f"  - 🟡 警告: 未知的 data_layout 类型 '{layout}'，跳过。")
                    df = pd.DataFrame()
                
            extracted_data[source['source_id']] = df
    else:
        print(f"  - 🟡 警告: 不支持的文件类型 '{file_extension}'，跳过文件。")
        return None
            
    print("✅ 所有数据块提取完成。")
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
