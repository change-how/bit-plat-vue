import logging
import pandas as pd
# scripts/okx_parser.py
# scripts/okx_parser.py
import json # 确保导入 json 模块

# scripts/okx_parser.py

# scripts/okx_parser.py

# ===================================================================
#  =============== 单个工作表的具体解析函数 ("工匠") ===============
# ===================================================================

def _parse_okx_user_info(df):
    """解析用户信息 (单行)"""
    logging.info("...正在使用OKX用户信息解析器...")
    try:
        if df.empty: return None
        row = df.iloc[0]
        branch = {"id": "基本信息", "data": {"title": "基本信息"}, "children": []}
        
        items = {
            "姓名": row.get('姓名'),
            "身份证号": str(row.get('身份证号或护照号', '')).strip("'"),
            "手机号": row.get('手机号'),
            "邮箱": row.get('邮箱'),
            "注册时间": row.get('注册时间'),
            "用户ID": row.get('uuid')
        }
        for title, value in items.items():
            if pd.notna(value) and value != '':
                branch["children"].append({"id": title, "data": {"title": title, "value": str(value)}})
        
        return branch
    except Exception as e:
        logging.error(f"解析OKX用户信息时出错: {e}")
        return None

def _create_multi_row_branch(df, branch_title, row_title_col, items_map):
    """一个通用的、用于处理多行数据的辅助函数"""
    logging.info(f"...正在使用通用解析器处理: {branch_title}...")
    try:
        if df.empty: return None
        
        branch = {"id": branch_title, "data": {"title": branch_title}, "children": []}
        
        for index, row in df.iterrows():
            row_title = str(row.get(row_title_col, f"记录 {index + 1}"))
            
            sub_node = {
                "id": f"{branch_title}-{row_title}-{index}",
                "data": {"title": row_title},
                "children": []
            }
            
            for display_title, actual_col in items_map.items():
                value = row.get(actual_col)
                if pd.notna(value) and value != '':
                    sub_node["children"].append({
                        "id": f"{display_title}-{row_title}-{index}",
                        "data": {"title": display_title, "value": str(value)}
                    })
            
            branch["children"].append(sub_node)
            
        return branch
    except Exception as e:
        logging.error(f"解析 {branch_title} 时出错: {e}")
        return None

def _find_core_address_from_deposits(df_deposit):
    """从充币记录的DataFrame中，寻找一个最合适的链上地址作为核心ID。"""
    logging.info("...开始在充币记录中寻找核心地址...")
    try:
        if df_deposit is None or df_deposit.empty or 'address' not in df_deposit.columns:
            return None
        for address in df_deposit['address']:
            addr_str = str(address)
            if len(addr_str) > 25 and not addr_str.startswith('INNER_'):
                logging.info(f"    成功找到一个有效地址: {addr_str}")
                return addr_str
        logging.warning("    在充币记录中未找到符合条件的外部地址。")
        return None
    except Exception as e:
        logging.error(f"寻找核心地址时出错: {e}")
        return None

# ===================================================================
#  ================== 总处理函数 ("分拣中心") ======================
# ===================================================================

def process_okx_data(all_sheets_dict, filename):
    """
    处理OKX文件，组装数据，并从充币记录中提取核心地址作为ID。
    """
    logging.info(f"使用 OKX 解析器处理文件: {filename}")

    # --- 1. 正常解析所有工作表，生成数据分支 ---
    all_branches = []
    for sheet_name, df in all_sheets_dict.items():
        logging.info(f"---> 正在处理工作表: {sheet_name}")
        branch = None
        
        if '用户信息' in sheet_name:
            branch = _parse_okx_user_info(df)
        elif '登录信息' in sheet_name:
            branch = _create_multi_row_branch(df, "登录信息", '登陆时间', {"IP": "登陆ip", "设备ID": "设备id", "客户端": "ua"})
        elif '充币记录' in sheet_name:
            branch = _create_multi_row_branch(df, "充币记录", '创建时间', {"币种": "币种", "地址": "address", "数量": "数量", "TXID": "txid"})
        elif '提币记录' in sheet_name:
            branch = _create_multi_row_branch(df, "提币记录", '创建时间', {"币种": "币种", "地址": "address", "数量": "数量", "TXID": "txid"})
        elif '用户余额' in sheet_name:
            branch = _create_multi_row_branch(df, "用户余额", 'Date', {"币种": "currency_symbol", "总额": "total_balance"})
        elif '法币交易记录' in sheet_name:
            branch = _create_multi_row_branch(df, "法币交易记录", '订单创建时间', {"订单号": "订单号", "买卖": "买卖", "币种": "交易币种", "总金额": "总金额", "单价": "单价", "数量": "数量"})
        elif '用户设备信息' in sheet_name:
            branch = _create_multi_row_branch(df, "用户设备信息", '设备id', {"WIFI信息": "wifi信息"})
        elif 'okx充值提现账单' in sheet_name:
            branch = _create_multi_row_branch(df, "充值提现账单", '账单时间', {"类型": "类型", "币种": "币种", "数量": "币的数量", "手续费": "手续费"})
        else:
            logging.warning(f"    在 '{filename}' 文件中, 未找到匹配 '{sheet_name}' 工作表的解析器。")
        
        if branch:
            all_branches.append(branch)
            
    # --- 2. 寻找并确定最终的核心ID ---
    final_core_id = _find_core_address_from_deposits(all_sheets_dict.get('充币记录'))
    if not final_core_id:
        if '用户信息' in all_sheets_dict:
            df_user = all_sheets_dict['用户信息']
            if not df_user.empty and 'uuid' in df_user.columns:
                final_core_id = str(df_user.iloc[0].get('uuid', '')).strip()
    if not final_core_id:
        final_core_id = filename.split('.')[0].lower()

    # --- 3. 组装最终的JSON对象 ---
    structured_data = {
        "id": final_core_id,
        "data": {
            "title": f"OKX账户",
            "value": final_core_id
        },
        "children": all_branches
    }
            
    # --- 4. 返回最终数据和最终ID ---
    return structured_data, final_core_id