#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试上传流程和文件名识别
验证前端上传到后端处理的完整流程
"""

import sys
from pathlib import Path
sys.path.append('scripts')

from main import TEMPLATE_REGISTRY, run_etl_process_for_file
from utils import determine_company_from_filename

def test_upload_workflow():
    """测试完整的上传工作流程"""
    
    print("=== 上传工作流程测试 ===\n")
    
    # 模拟前端上传后的文件名格式
    test_files = [
        {
            "original": "e757744d193a390b.csv",
            "company_selected": "ImToken", 
            "backend_filename": "1724312345_imtoken_e757744d193a390b.csv",
            "description": "用户选择ImToken，后端生成文件名"
        },
        {
            "original": "TP嘉兴市公安局南湖区分局取证 (1).csv",
            "company_selected": "TokenPocket",
            "backend_filename": "1724312400_tokenpocket_TP嘉兴市公安局南湖区分局取证 (1).csv", 
            "description": "用户选择TokenPocket，后端生成文件名"
        },
        {
            "original": "OKX陈兆群.xlsx",
            "company_selected": "欧意",
            "backend_filename": "1724312450_okx_OKX陈兆群.xlsx",
            "description": "用户选择欧意，后端生成文件名"
        }
    ]
    
    print("1. 测试文件名识别逻辑")
    print("-" * 50)
    
    for test_case in test_files:
        print(f"📄 测试文件: {test_case['backend_filename']}")
        print(f"   描述: {test_case['description']}")
        
        # 测试公司识别
        file_path = Path(test_case['backend_filename'])
        detected_company = determine_company_from_filename(file_path, TEMPLATE_REGISTRY)
        
        if detected_company:
            print(f"   ✅ 识别到公司: {detected_company}")
            
            # 检查模板文件是否存在
            if detected_company in TEMPLATE_REGISTRY:
                template_path = TEMPLATE_REGISTRY[detected_company]
                print(f"   📋 使用模板: {template_path}")
                
                if template_path.exists():
                    print(f"   ✅ 模板文件存在")
                else:
                    print(f"   ❌ 模板文件不存在: {template_path}")
            else:
                print(f"   ❌ 未找到对应模板")
        else:
            print(f"   ❌ 无法识别公司")
        
        print()
    
    print("2. 测试模板注册表完整性")
    print("-" * 50)
    
    print(f"📋 当前注册的模板:")
    for company, template_path in TEMPLATE_REGISTRY.items():
        exists = "✅" if template_path.exists() else "❌"
        print(f"   {company}: {template_path} {exists}")
    
    print("\n3. 测试真实文件处理")
    print("-" * 50)
    
    # 测试真实的ImToken文件
    real_imtoken_file = Path("141数据调证数据/Imtoken/e757744d193a390b.csv")
    if real_imtoken_file.exists():
        print(f"📂 测试真实ImToken文件: {real_imtoken_file}")
        
        # 模拟后端重命名后的文件
        simulated_filename = "1724312345_imtoken_e757744d193a390b.csv"
        print(f"   模拟后端文件名: {simulated_filename}")
        
        # 测试公司识别
        simulated_path = Path(simulated_filename)
        detected_company = determine_company_from_filename(simulated_path, TEMPLATE_REGISTRY)
        print(f"   识别结果: {detected_company}")
        
        if detected_company == 'imtoken':
            print(f"   ✅ 公司识别正确")
            
            # 测试模板加载（但不实际处理数据）
            template_path = TEMPLATE_REGISTRY[detected_company]
            if template_path.exists():
                print(f"   ✅ 模板可用: {template_path}")
            else:
                print(f"   ❌ 模板不存在")
        else:
            print(f"   ❌ 公司识别错误，期望: imtoken, 实际: {detected_company}")
    else:
        print(f"❌ 真实测试文件不存在: {real_imtoken_file}")
    
    print("\n4. 前端选项验证")
    print("-" * 50)
    
    frontend_companies = ['欧意', '币安', '火币', 'ImToken', 'TokenPocket']
    backend_mapping = {
        '币安': 'binance',
        '欧易': 'okx', 
        '火币': 'htx',
        'ImToken': 'imtoken',
        'TokenPocket': 'tokenpocket'
    }
    
    print("前端公司选项与后端模板匹配:")
    for company in frontend_companies:
        backend_name = backend_mapping.get(company, company.lower())
        has_template = backend_name in TEMPLATE_REGISTRY
        status = "✅" if has_template else "❌"
        print(f"   {company} → {backend_name} {status}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_upload_workflow()
