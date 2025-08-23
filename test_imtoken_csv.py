# test_imtoken_csv.py - ImToken CSV处理测试脚本

import sys
import os
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.append('scripts')

def test_imtoken_csv():
    """
    测试ImToken CSV文件的处理功能
    """
    print("=== ImToken CSV处理测试 ===\n")
    
    try:
        # 导入必要的模块
        from scripts.main import run_etl_process_for_file, DB_CONFIG, TEMPLATE_REGISTRY
        from scripts.utils import determine_company_from_filename
        
        # 测试文件路径
        test_file = Path("uploads/test_imtoken_e757744d193a390b.csv")
        
        if not test_file.exists():
            print(f"❌ 测试文件不存在: {test_file}")
            return False
            
        print(f"📁 测试文件: {test_file.name}")
        print(f"📏 文件大小: {test_file.stat().st_size} 字节")
        
        # 步骤1: 测试公司识别
        print("\n🔍 步骤1: 测试公司识别")
        company_name = determine_company_from_filename(test_file, TEMPLATE_REGISTRY)
        print(f"识别结果: {company_name}")
        
        if not company_name:
            print("❌ 无法识别公司类型")
            return False
            
        # 步骤2: 检查模板文件
        print(f"\n📋 步骤2: 检查模板文件")
        if company_name in TEMPLATE_REGISTRY:
            template_path = TEMPLATE_REGISTRY[company_name]
            print(f"模板路径: {template_path}")
            if template_path.exists():
                print("✅ 模板文件存在")
            else:
                print("❌ 模板文件不存在")
                return False
        else:
            print("❌ 注册表中没有对应的模板")
            return False
            
        # 步骤3: 测试ETL处理
        print(f"\n⚙️ 步骤3: 开始ETL处理")
        success, message = run_etl_process_for_file(test_file)
        
        if success:
            print("✅ CSV文件处理成功!")
            print(f"处理结果: {message}")
            return True
        else:
            print("❌ CSV文件处理失败!")
            print(f"错误信息: {message}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖模块都已安装")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def preview_csv_structure():
    """
    预览CSV文件结构
    """
    print("=== CSV文件结构预览 ===\n")
    
    try:
        import pandas as pd
        
        csv_file = Path("uploads/test_imtoken_e757744d193a390b.csv")
        if not csv_file.exists():
            print(f"❌ CSV文件不存在: {csv_file}")
            return
            
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        print(f"📊 文件信息:")
        print(f"  - 行数: {len(df)}")
        print(f"  - 列数: {len(df.columns)}")
        print(f"  - 列名: {list(df.columns)}")
        
        print(f"\n📋 前5行数据:")
        print(df.head().to_string(index=False))
        
        print(f"\n📈 数据类型:")
        for col in df.columns:
            print(f"  - {col}: {df[col].dtype}")
            
    except Exception as e:
        print(f"❌ 预览CSV结构时出错: {e}")

if __name__ == "__main__":
    # 切换到正确的工作目录
    os.chdir(Path(__file__).parent)
    
    # 预览CSV结构
    preview_csv_structure()
    
    print("\n" + "="*50 + "\n")
    
    # 测试CSV处理
    success = test_imtoken_csv()
    
    print("\n" + "="*50 + "\n")
    
    if success:
        print("🎉 测试通过! ImToken CSV文件可以成功处理并入库")
    else:
        print("💥 测试失败! 请检查错误信息并修复问题")
        
    print("\n📖 后续操作建议:")
    print("1. 如果测试成功，您可以通过前端上传ImToken的CSV文件")
    print("2. 系统会自动识别imtoken文件并使用相应的模板处理")
    print("3. 处理后的数据会存储在数据库中，可通过查询接口访问")
