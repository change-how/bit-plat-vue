"""
简化的前端上传工作流测试
"""
import sys
import os
import time
import json
from pathlib import Path

def company_shortname(company_name):
    """前端公司名称到短名称的映射"""
    company_map = {
        '欧意': 'okx',
        '币安': 'binance', 
        '火币': 'huobi',
        'ImToken': 'imtoken',
        'TokenPocket': 'tokenpocket'
    }
    return company_map.get(company_name, company_name.lower())

def determine_company_from_filename(file_path, registry):
    """从文件名检测公司类型"""
    filename_lower = file_path.name.lower()
    file_extension = file_path.suffix.lower()
    
    for company_key in registry.keys():
        if company_key != 'csv' and company_key in filename_lower:
            return company_key
    
    if file_extension == '.csv' and 'csv' in registry:
        return 'csv'
            
    return None

def generate_upload_filename(original_filename, selected_company):
    """生成上传文件名（模拟后端app.py逻辑）"""
    timestamp = int(time.time())
    shortname = company_shortname(selected_company)
    filename_root = Path(original_filename).stem
    filename_ext = Path(original_filename).suffix
    
    new_filename = f"{timestamp}_{shortname}_{filename_root}{filename_ext}"
    return new_filename

def load_template(template_path):
    """加载JSON模板文件"""
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 移除注释
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            if '//' in line:
                line = line.split('//')[0].rstrip()
            clean_lines.append(line)
        clean_content = '\n'.join(clean_lines)
        return json.loads(clean_content)

def test_upload_workflow():
    """测试完整的上传工作流"""
    print("=" * 60)
    print("测试前端上传工作流")
    print("=" * 60)
    
    current_dir = Path.cwd()
    
    # 模板注册表
    TEMPLATE_REGISTRY = {
        'okx': current_dir / 'config/okx_map.jsonc',
        'binance': current_dir / 'config/binance_map.jsonc',
        'huobi': current_dir / 'config/huobi_map.jsonc',
        'imtoken': current_dir / 'config/imtoken_map.jsonc',
        'tokenpocket': current_dir / 'config/tokenpocket_map.jsonc',
        'csv': current_dir / 'config/csv_universal_map.jsonc'
    }
    
    # 测试用例：模拟前端上传
    test_cases = [
        {
            'original_file': 'ImToken_e757744d193a390b.csv',
            'selected_company': 'ImToken',
            'actual_file_path': current_dir / 'uploads' / 'test_imtoken_e757744d193a390b.csv'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'-' * 40}")
        print(f"测试用例 {i}: {test_case['selected_company']}")
        print(f"{'-' * 40}")
        
        # 步骤1: 用户在前端选择公司和文件
        original_filename = test_case['original_file']
        selected_company = test_case['selected_company']
        print(f"📁 原始文件名: {original_filename}")
        print(f"🏢 用户选择公司: {selected_company}")
        
        # 步骤2: 后端生成新文件名
        upload_filename = generate_upload_filename(original_filename, selected_company)
        print(f"🔄 生成上传文件名: {upload_filename}")
        
        # 步骤3: 从文件名检测公司
        upload_path = Path(upload_filename)
        detected_company = determine_company_from_filename(upload_path, TEMPLATE_REGISTRY)
        print(f"🔍 从文件名检测到: {detected_company}")
        
        # 步骤4: 获取模板路径
        if detected_company and detected_company in TEMPLATE_REGISTRY:
            template_path = TEMPLATE_REGISTRY[detected_company]
            template_exists = template_path.exists()
            print(f"📋 模板路径: {template_path}")
            print(f"✅ 模板存在: {template_exists}")
            
            if template_exists:
                # 步骤5: 加载模板
                try:
                    template = load_template(str(template_path))
                    print(f"📊 模板加载成功")
                    print(f"   处理方法: {template.get('processing_method', '未指定')}")
                    print(f"   字段映射数量: {len(template.get('field_mapping', {}))}")
                    
                    # 步骤6: 检查测试文件
                    test_file_path = test_case['actual_file_path']
                    print(f"📂 测试文件路径: {test_file_path}")
                    
                    if test_file_path.exists():
                        print(f"✅ 测试文件存在")
                        
                        # 简单读取CSV文件的前几行
                        try:
                            import pandas as pd
                            df = pd.read_csv(test_file_path, encoding='utf-8')
                            print(f"📊 CSV文件读取成功:")
                            print(f"   数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
                            print(f"   列名: {list(df.columns)[:5]}...")
                            if len(df) > 0:
                                print(f"   第一行数据: {df.iloc[0].to_dict()}")
                                
                        except Exception as e:
                            print(f"❌ CSV文件读取失败: {str(e)}")
                            # 尝试GBK编码
                            try:
                                df = pd.read_csv(test_file_path, encoding='gbk')
                                print(f"📊 CSV文件读取成功 (GBK编码):")
                                print(f"   数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
                                print(f"   列名: {list(df.columns)[:5]}...")
                            except Exception as e2:
                                print(f"❌ GBK编码也失败: {str(e2)}")
                    else:
                        print(f"❌ 测试文件不存在: {test_file_path}")
                        
                except Exception as e:
                    print(f"❌ 模板加载失败: {str(e)}")
            else:
                print(f"❌ 模板文件不存在")
        else:
            print(f"❌ 无法识别公司类型")
    
    print(f"\n{'=' * 60}")
    print("工作流测试完成")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    test_upload_workflow()
