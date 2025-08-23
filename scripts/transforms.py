import pandas as pd
from decimal import Decimal, InvalidOperation

def string_to_decimal(value):
    if value is None or pd.isna(value): return None
    try:
        return Decimal(str(value).replace(',', ''))
    except (InvalidOperation, ValueError, TypeError):
        return None

def parse_universal_datetime(value):
    if value is None or pd.isna(value): return None
    try:
        return pd.to_datetime(value)
    except (ValueError, TypeError):
        return None

def map_buy_sell(value: str):
    if value == '买': return 'BUY'
    if value == '卖': return 'SELL'
    return 'UNKNOWN'
# transforms.py 文件末尾

def extract_base_asset(pair: str) -> str:
    """从'BTCUSDT'这样的交易对中提取基础币种'BTC'。"""
    if not isinstance(pair, str): return None
    # 这是一个简单的假设，对于USDT, BUSD等常见稳定币
    if pair.endswith('USDT'): return pair[:-4]
    if pair.endswith('BUSD'): return pair[:-4]
    if pair.endswith('USDC'): return pair[:-4]
    if pair.endswith('DAI'): return pair[:-3]
    return pair # 如果无法判断，返回原值

def extract_quote_asset(pair: str) -> str:
    """从'BTCUSDT'这样的交易对中提取计价币种'USDT'。"""
    if not isinstance(pair, str): return None
    if pair.endswith('USDT'): return 'USDT'
    if pair.endswith('BUSD'): return 'BUSD'
    if pair.endswith('USDC'): return 'USDC'
    if pair.endswith('DAI'): return 'DAI'
    return 'UNKNOWN'

def map_imtoken_direction(value: str) -> str:
    """将ImToken的操作类型映射为标准的方向字段。"""
    if not isinstance(value, str): return 'UNKNOWN'
    
    value_upper = value.upper()
    if value_upper in ['NEW_IDENTITY', 'PRIVATE']:
        return 'CREATE'  # 钱包创建
    elif value_upper in ['DELETE_WALLET']:
        return 'DELETE'  # 钱包删除
    elif value_upper in ['IMPORT_WALLET']:
        return 'IMPORT'  # 钱包导入
    else:
        return value_upper  # 保持原值