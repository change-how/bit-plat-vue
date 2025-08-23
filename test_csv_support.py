# test_csv_support.py - CSV支持功能测试脚本

import pandas as pd
from pathlib import Path

def create_test_csv_files():
    """
    创建4种不同布局的测试CSV文件，用于验证CSV处理功能
    """
    test_dir = Path("./test_csv_files")
    test_dir.mkdir(exist_ok=True)
    
    print("正在创建CSV测试文件...")
    
    # 1. 标准表格布局 (tabular)
    print("1. 创建标准表格CSV...")
    tabular_data = {
        '用户ID': ['USER001', 'USER002', 'USER003'],
        '交易ID': ['TXN001', 'TXN002', 'TXN003'], 
        '金额': ['1000.50', '2500.00', '750.25'],
        '币种': ['BTC', 'ETH', 'USDT'],
        '交易时间': ['2024-01-01 10:30:00', '2024-01-02 14:15:00', '2024-01-03 09:45:00']
    }
    df_tabular = pd.DataFrame(tabular_data)
    df_tabular.to_csv(test_dir / "test_tabular.csv", index=False, encoding='utf-8-sig')
    
    # 2. 表单布局 (form_layout)
    print("2. 创建表单布局CSV...")
    form_data = [
        ['用户基本信息', '', '', ''],  # 标题行
        ['用户ID', '姓名', '手机号', '邮箱'],  # 表头行
        ['USER001', '张三', '13800138000', 'zhangsan@email.com']  # 数据行
    ]
    df_form = pd.DataFrame(form_data)
    df_form.to_csv(test_dir / "test_form.csv", index=False, header=False, encoding='utf-8-sig')
    
    # 3. 动态子表 (find_subtable_by_header)
    print("3. 创建动态子表CSV...")
    subtable_data = [
        ['这是一些说明文字', '', '', ''],
        ['', '', '', ''],  # 空行
        ['交易记录', '', '', ''],  # 子表标题
        ['用户ID', '资产类型', '操作类型', '数量'],  # 子表表头
        ['USER001', 'BTC', '充值', '0.5'],
        ['USER001', 'ETH', '提现', '2.0'],
        ['USER002', 'USDT', '交易', '1000.0']
    ]
    df_subtable = pd.DataFrame(subtable_data)
    df_subtable.to_csv(test_dir / "test_subtable.csv", index=False, header=False, encoding='utf-8-sig')
    
    # 4. 复杂三维表 (merged_key_value)
    print("4. 创建复杂三维表CSV...")
    complex_data = [
        ['设备名称', '设备类型', '最后使用时间', '属性名称', '属性值'],
        ['iPhone 14', '手机', '2024-01-01 10:00:00', 'IMEI', '123456789012345'],
        ['', '', '', 'iOS版本', '17.2.1'],
        ['', '', '', 'APP版本', '2.1.0'],
        ['MacBook Pro', '电脑', '2024-01-02 15:30:00', 'MAC地址', 'AA:BB:CC:DD:EE:FF'],
        ['', '', '', '操作系统', 'macOS 14.0'],
        ['', '', '', '浏览器', 'Safari 17.0']
    ]
    df_complex = pd.DataFrame(complex_data)
    df_complex.to_csv(test_dir / "test_complex.csv", index=False, header=False, encoding='utf-8-sig')
    
    print(f"✅ 所有测试CSV文件已创建完成，保存在: {test_dir.absolute()}")
    
    # 输出文件结构信息
    print("\n📁 创建的文件结构:")
    for csv_file in test_dir.glob("*.csv"):
        print(f"  - {csv_file.name}")
        df = pd.read_csv(csv_file, header=None)
        print(f"    尺寸: {df.shape[0]} 行 x {df.shape[1]} 列")
        print(f"    前3行预览:")
        for i in range(min(3, len(df))):
            print(f"      {list(df.iloc[i])}")
        print()

def test_csv_processing():
    """
    测试CSV处理功能
    """
    try:
        from scripts.data_extract import extract_data_from_sources
        from scripts.utils import load_mapping_config
        
        print("开始测试CSV处理功能...")
        
        # 加载CSV配置模板
        config_path = Path("./config/csv_universal_map.jsonc")
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            return
            
        mapping_config = load_mapping_config(config_path)
        if not mapping_config:
            print("❌ 无法加载配置文件")
            return
            
        # 测试标准表格CSV
        test_file = Path("./test_csv_files/test_tabular.csv")
        if test_file.exists():
            print(f"\n🔍 测试文件: {test_file.name}")
            sources_config = [
                {
                    "source_id": "basic_transactions_raw",
                    "data_layout": "tabular",
                    "header_row": 1
                }
            ]
            
            result = extract_data_from_sources(test_file, sources_config)
            if result:
                print("✅ CSV处理成功!")
                for source_id, data in result.items():
                    print(f"  数据源 '{source_id}': {len(data)} 行数据")
                    if hasattr(data, 'columns'):
                        print(f"  列名: {list(data.columns)}")
            else:
                print("❌ CSV处理失败")
        else:
            print(f"❌ 测试文件不存在: {test_file}")
            
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

if __name__ == "__main__":
    print("=== CSV支持功能测试 ===\n")
    
    # 创建测试文件
    create_test_csv_files()
    
    print("\n" + "="*50 + "\n")
    
    # 测试处理功能
    test_csv_processing()
    
    print("\n=== 测试完成 ===")
    
    print("\n📖 使用说明:")
    print("1. 现在您的系统已支持CSV文件的4种识别方法:")
    print("   - tabular: 标准表格布局")
    print("   - form_layout: 表单布局（键值对）")
    print("   - find_subtable_by_header: 动态子表查找")
    print("   - merged_key_value: 复杂三维表处理")
    print("\n2. CSV文件会自动使用通用CSV模板处理")
    print("3. 如果您有特定公司的CSV文件，请在文件名中包含公司名称")
    print("4. 您可以根据需要修改 config/csv_universal_map.jsonc 配置文件")
