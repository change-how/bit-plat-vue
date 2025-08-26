#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件元信息数据库初始化和历史文件迁移脚本

功能：
1. 创建 file_metadata 表
2. 扫描现有上传文件并添加元信息
3. 验证表结构和数据完整性
"""
import os
import sys
import glob
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from scripts.file_metadata import create_file_metadata_table, insert_file_metadata, get_all_file_metadata

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'crypto_platform'
}

def init_file_metadata_table():
    """创建文件元信息表"""
    try:
        print("🔄 正在创建 file_metadata 表...")
        create_file_metadata_table(DB_CONFIG)
        print("✅ file_metadata 表创建成功")
        return True
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False

def scan_existing_files():
    """扫描现有上传文件并添加到数据库"""
    uploads_dir = os.path.join(project_root, 'uploads')
    
    if not os.path.exists(uploads_dir):
        print(f"⚠️ 上传目录不存在: {uploads_dir}")
        return []
    
    # 扫描所有Excel文件
    excel_patterns = ['*.xlsx', '*.xls', '*.csv']
    existing_files = []
    
    for pattern in excel_patterns:
        files = glob.glob(os.path.join(uploads_dir, pattern))
        existing_files.extend(files)
    
    print(f"📁 发现 {len(existing_files)} 个现有文件")
    return existing_files

def migrate_existing_files(file_paths):
    """将现有文件信息迁移到数据库"""
    migrated_count = 0
    failed_count = 0
    
    for file_path in file_paths:
        try:
            # 从文件名推断平台信息
            filename = os.path.basename(file_path)
            platform = infer_platform_from_filename(filename)
            
            # 插入文件元信息
            insert_file_metadata(
                DB_CONFIG,
                file_path,
                original_filename=filename,
                platform=platform
            )
            
            print(f"✅ 已迁移: {filename} -> {platform}")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ 迁移失败 {filename}: {e}")
            failed_count += 1
    
    print(f"\n📊 迁移结果: 成功 {migrated_count} 个, 失败 {failed_count} 个")
    return migrated_count, failed_count

def infer_platform_from_filename(filename):
    """从文件名推断平台信息"""
    filename_lower = filename.lower()
    
    # 平台关键词映射
    platform_keywords = {
        'okx': 'OKX',
        'huobi': '火币',
        'binance': 'Binance',
        'bnb': 'Binance',
        'imtoken': 'ImToken',
        'tokenpocket': 'TokenPocket',
        'bitget': 'Bitget',
        'gate': 'Gate.io',
        'bitpie': 'Bitpie'
    }
    
    for keyword, platform in platform_keywords.items():
        if keyword in filename_lower:
            return platform
    
    return '未知平台'

def verify_migration():
    """验证迁移结果"""
    try:
        all_metadata = get_all_file_metadata(DB_CONFIG)
        print(f"\n📋 数据库中共有 {len(all_metadata)} 条文件记录")
        
        # 按平台统计
        platform_stats = {}
        for metadata in all_metadata:
            platform = metadata.get('platform', '未知')
            platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        print("📊 平台分布:")
        for platform, count in platform_stats.items():
            print(f"  {platform}: {count} 个文件")
        
        return True
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始初始化文件元信息系统")
    print("=" * 50)
    
    # 1. 创建表
    if not init_file_metadata_table():
        return False
    
    # 2. 扫描现有文件
    existing_files = scan_existing_files()
    
    if existing_files:
        # 3. 迁移现有文件
        print(f"\n🔄 开始迁移 {len(existing_files)} 个现有文件...")
        migrated, failed = migrate_existing_files(existing_files)
        
        # 4. 验证迁移结果
        print(f"\n🔍 验证迁移结果...")
        verify_migration()
    else:
        print("ℹ️ 没有发现现有文件，跳过迁移步骤")
    
    print("\n" + "=" * 50)
    print("🎉 文件元信息系统初始化完成!")
    print("📝 新上传的文件将自动记录元信息")
    print("💾 Excel下载功能将显示完整的文件信息")
    
    return True

if __name__ == "__main__":
    main()
