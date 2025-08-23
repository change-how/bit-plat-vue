#!/usr/bin/env python3
# test_csv_processing.py - ImToken CSV文件处理测试脚本

import sys
from pathlib import Path

# 添加scripts目录到路径，以便导入模块
sys.path.append(str(Path(__file__).parent / "scripts"))

from scripts.main import run_etl_process_for_file

def test_imtoken_csv():
    """测试ImToken CSV文件的ETL处理"""
    print("=== ImToken CSV文件处理测试 ===")
    
    # 测试文件路径
    test_file = Path("uploads/test_imtoken_e757744d193a390b.csv")
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"📁 测试文件: {test_file}")
    print(f"📊 文件大小: {test_file.stat().st_size} bytes")
    
    # 执行ETL处理
    try:
        success, message = run_etl_process_for_file(test_file)
        
        if success:
            print(f"✅ 处理成功: {message}")
            return True
        else:
            print(f"❌ 处理失败: {message}")
            return False
            
    except Exception as e:
        print(f"❌ 处理异常: {e}")
        return False

if __name__ == "__main__":
    success = test_imtoken_csv()
    sys.exit(0 if success else 1)
