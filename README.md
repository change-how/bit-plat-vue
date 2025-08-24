# 虚拟币平台数据处理系统 - 快速入门

## 🚀 项目简介

这是一个专门用于处理各大虚拟币交易平台调证数据的企业级系统，支持Excel文件上传、自动化数据提取、标准化存储以及思维导图形式的数据可视化展示。

## 📋 功能特性

- ✅ **多平台支持**: OKX、币安、火币、ImToken、TokenPocket
- ✅ **自动化ETL**: Excel文件自动解析和数据提取
- ✅ **标准化存储**: 统一的6表数据库设计
- ✅ **可视化展示**: 思维导图形式展示用户数据关系
- ✅ **模糊搜索**: 支持多字段智能搜索
- ✅ **配置驱动**: 新平台通过配置文件快速接入

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   后端API       │    │   MySQL数据库   │
│   Vue.js 3      │◄──►│   Flask         │◄──►│   6张核心表     │
│   思维导图展示  │    │   ETL数据处理   │    │   标准化存储    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ⚡ 快速开始

### 1. 环境准备

**系统要求:**
- Python 3.8+
- MySQL 5.7+
- Node.js 16+

### 2. 后端启动

```bash
# 1. 安装Python依赖
pip install flask flask-cors pandas sqlalchemy mysql-connector-python openpyxl

# 2. 配置数据库（修改 scripts/main.py 中的 DB_CONFIG）
DB_CONFIG = {
    'type': 'mysql',
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'your_database'
}

# 3. 初始化数据库
python scripts/db_setup.py

# 4. 启动Flask服务
python app.py
```

### 3. 前端启动

```bash
# 1. 安装Node.js依赖
npm install

# 2. 启动开发服务器
npm run dev
```

### 4. 访问系统

打开浏览器访问: `http://localhost:3000`

## 📖 使用流程

### 1. 上传文件
1. 在首页点击"上传文件"按钮
2. 选择平台类型（OKX、币安等）
3. 上传Excel/CSV文件
4. 系统自动处理并入库

### 2. 查询数据
1. 在搜索框输入关键词（姓名、手机号、用户ID等）
2. 系统返回匹配的用户列表
3. 点击用户查看详细数据

### 3. 查看结果
- **左侧**: 大纲导航
- **中间**: 思维导图展示用户数据关系
- **右侧**: 点击节点查看详细信息

## 🎯 核心API

### 搜索用户
```bash
GET /api/search_uid?query=张三
```

### 获取用户数据
```bash
GET /api/mindmap_data?user_id=12345
```

### 上传文件
```bash
POST /api/upload
Content-Type: multipart/form-data
- file: Excel/CSV文件
- company: 平台标识符
```

## 📊 数据库表结构

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| users | 用户信息 | user_id, name, phone_number, email |
| transactions | 交易记录 | transaction_id, direction, base_asset, quantity |
| asset_movements | 充提记录 | direction, asset, address, txid |
| login_logs | 登录日志 | login_time, login_ip, device_id |
| devices | 设备信息 | device_id, client_type, ip_address |
| file_metadata | 文件信息 | file_name, upload_time, platform |

## 🔧 配置说明

### 平台配置
- 配置文件位置: `config/`
- 格式: JSONC
- 作用: 定义Excel字段到数据库字段的映射关系

### 添加新平台
1. 在 `config/` 目录创建新的映射文件
2. 在 `scripts/main.py` 的 `TEMPLATE_REGISTRY` 中注册
3. 在前端 `HomeView.vue` 的 `companies` 数组中添加

## 🐛 常见问题

**Q: 上传文件失败？**
A: 检查文件格式（仅支持Excel/CSV）和平台选择是否正确

**Q: 数据库连接失败？**
A: 检查 `scripts/main.py` 中的数据库配置信息

**Q: 搜索无结果？**
A: 确认数据已正确上传入库，尝试使用不同关键词

**Q: 前端页面无法访问？**
A: 确认前端开发服务器已启动（npm run dev）

## 📞 技术支持

详细的API文档请参考: `API_DOCUMENTATION.md`

**版本**: v1.0.0  
**最后更新**: 2024年12月18日
