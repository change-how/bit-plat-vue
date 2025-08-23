# 测试错误信息生成
import pandas as pd
from pathlib import Path
import sys
import os

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.data_extract import extract_data_from_sources
from scripts.error_handler import ETLError, format_error_for_frontend
import commentjson

def test_error_message():
    # 创建一个测试Excel文件，只包含错误的工作表
    test_file = Path("test_wrong_sheets.xlsx")
    
    # 创建一个包含错误工作表的Excel文件
    with pd.ExcelWriter(test_file, engine='openpyxl') as writer:
        pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}).to_excel(writer, sheet_name='Sheet1', index=False)
        pd.DataFrame({'X': [7, 8, 9], 'Y': [10, 11, 12]}).to_excel(writer, sheet_name='Data', index=False)
    
    # 加载OKX配置
    with open('config/okx_map.jsonc', 'r', encoding='utf-8') as f:
        config = commentjson.load(f)
    
    sources = config.get('sources', [])
    
    try:
        # 尝试提取数据，应该会失败并显示具体的工作表错误
        extracted_data = extract_data_from_sources(test_file, sources)
        print("错误：应该抛出异常但没有抛出")
    except ETLError as e:
        print("捕获到 ETLError:")
        print(f"Message: {e.message}")
        print(f"Details: {e.details}")
        print(f"Suggestions: {e.suggestions}")
        
        # 格式化为前端格式
        frontend_error = format_error_for_frontend(e)
        print("\n前端格式化结果:")
        print(frontend_error)
    except Exception as e:
        print(f"其他异常: {type(e).__name__}: {e}")
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    test_error_message()
