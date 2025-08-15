import logging
# 从各个“办公室”把“专员”请过来
from scripts.okx_parser import process_okx_data

def process_uploaded_data(df, original_filename):
    """
    总处理函数（分拣中心），根据文件名判断数据来源，并分发给相应的解析器。
    """
    logging.info(f"开始分拣处理文件: {original_filename}")
    
    lower_filename = original_filename.lower()

    if 'okx' in lower_filename:
        # 分发给 OKX 解析器
        return process_okx_data(df, original_filename)
        
    elif '币安' in lower_filename or 'binance' in lower_filename:
        # 分发给币安解析器
        return process_binance_data(df, original_filename)
        
    else:
        # 如果没有匹配到，返回未知状态
        logging.warning(f"未找到匹配的解析器: {original_filename}")
        return {"source": "Unknown", "error": "无法识别的文件来源，请检查文件名。"}