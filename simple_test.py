#!/usr/bin/env python3
# simple_test.py - 简单测试
print("Python运行正常")

try:
    import sqlalchemy
    print("✅ SQLAlchemy已安装")
except ImportError:
    print("❌ SQLAlchemy未安装")

try:
    import mysql.connector
    print("✅ MySQL连接器已安装")
except ImportError:
    print("❌ MySQL连接器未安装")

try:
    import pandas
    print("✅ Pandas已安装")
except ImportError:
    print("❌ Pandas未安装")

# 尝试连接数据库
try:
    import mysql.connector
    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='123456',
        database='test_db'
    )
    print("✅ 数据库连接成功")
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"📊 数据库中的表: {[table[0] for table in tables]}")
    
    # 检查users表
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    print(f"👤 用户表记录数: {users_count}")
    
    if users_count > 0:
        cursor.execute("SELECT user_id FROM users LIMIT 3")
        sample_users = cursor.fetchall()
        print(f"🔍 示例用户ID: {[user[0] for user in sample_users]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")

print("测试完成!")
