# data_extract.py - 数据处理车间 (V2 - 表单处理升级版)

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

def _find_subtable_start_row(sheet_df: pd.DataFrame, section_header: str, header_offset: int) -> int:
    """(内部工具) 在工作表中，根据分块标题，只返回子表的表头行号。"""
    # 查找所有包含标题的单元格
    # a.stack()将DataFrame变成一个Series, .str.contains()进行查找, .dropna()去掉不匹配的
    matches = sheet_df.stack().str.contains(section_header, na=False).dropna()
    if matches.any():
        # matches.index[0][0]可以获取第一个匹配项的行号
        header_row_index = matches.index[0][0]
        return header_row_index + header_offset
    
    print(f"  - 🟡 警告: 在工作表中未找到标题为 '{section_header}' 的子表。")
    return None

def _parse_tabular_subtable(sheet_df: pd.DataFrame, section_header: str, header_offset: int) -> pd.DataFrame:
    """(旧工具的优化版) 解析一个标准的多行子表。"""
    header_row = _find_subtable_start_row(sheet_df, section_header, header_offset)
    if header_row is None: return pd.DataFrame()
    
    sub_table = sheet_df.iloc[header_row+1:].copy()
    sub_table.columns = sheet_df.iloc[header_row].values
    sub_table.reset_index(drop=True, inplace=True)
    sub_table.dropna(how='all', inplace=True)
    return sub_table

def _parse_form_subtable(sheet_df: pd.DataFrame, section_header: str, header_offset: int) -> dict:
    """(全新的“表单处理”工具) 解析一个“表单式”的子表，并将其转换为一个单行的字典。"""
    header_row = _find_subtable_start_row(sheet_df, section_header, header_offset)
    if header_row is None: return {}
    
    # 在表单中，我们假设表头在 header_row，而数据就在它的下一行
    data_row_index = header_row + 1
    
    # 将表头行和数据行，打包成一个字典 {表头: 数据}
    form_data = pd.Series(
        sheet_df.iloc[data_row_index].values,
        index=sheet_df.iloc[header_row].values
    ).to_dict()
    
    return form_data

# --- 核心“取货员”函数 (升级版) ---

def extract_data_from_sources(excel_path: Path, sources_config: list) -> dict:
    """
    (V4版 - 智能调度版)
    能够根据'data_layout'调用不同的、专门的解析器。
    """
    print(f"\n--- 正在从Excel提取数据块 ---")
    extracted_data = {}
    try:
        xls = pd.ExcelFile(excel_path)
    except FileNotFoundError:
        print(f"❌ Excel文件未找到: {excel_path}")
        return None

    for source in sources_config:
        sheet_name = source['worksheet_name']
        layout = source.get('data_layout', 'tabular')
        print(f"  - 正在读取工作表: '{sheet_name}' (ID: '{source['source_id']}', 布局: {layout})")
        
        if layout == 'tabular':
            df = pd.read_excel(xls, sheet_name=sheet_name, header=source.get('header_row', 1) - 1, nrows=source.get('nrows', None))
            extracted_data[source['source_id']] = df
        else:
            full_sheet_df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            if layout == 'find_subtable_by_header':
                data = _parse_tabular_subtable(full_sheet_df, source['section_header'], source['header_offset'])
            elif layout == 'form_layout':
                data = _parse_form_subtable(full_sheet_df, source['section_header'], source['header_offset'])
            else:
                print(f"  - 🟡 警告: 未知的 data_layout 类型 '{layout}'，跳过。")
                data = None
            
            extracted_data[source['source_id']] = data
            
    print("✅ 所有数据块提取完成。")
    return extracted_data

# --- “首席工匠”函数 (升级版) ---

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
    
    # --- 核心升级：判断原材料是“多行表格”还是“单条记录” ---
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
    (这是一个全新的内部工具) 专门负责处理单行数据的完整映射逻辑。
    """
    mappings = destination_config.get('mappings', [])
    standard_fields = {'source_file_name': source_file_name}
    extra_fields = {}

    for rule in mappings:
        target_field = rule['target_field']
        raw_value = None
        if 'static_value' in rule:
            raw_value = rule['static_value']
        elif 'lookup_source' in rule:
            lookup_data = all_extracted_data.get(rule['lookup_source'])
            if lookup_data is not None:
                # 假设lookup总是单条记录(dict)或单行表(DataFrame)
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
            if func: transformed_value = func(transformed_value)

        if rule.get('in_extra', False):
            extra_fields[target_field] = transformed_value
        else:
            standard_fields[target_field] = transformed_value
    
    if extra_fields:
        def json_converter(o):
            if isinstance(o, (pd.Timestamp, pd.NaT.__class__)): return o.isoformat() if pd.notna(o) else None
            if isinstance(o, Decimal): return str(o)
            if hasattr(o, 'item'): return o.item()
            raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
        standard_fields['extra_data'] = json.dumps(extra_fields, default=json_converter, ensure_ascii=False)
    
    return standard_fields