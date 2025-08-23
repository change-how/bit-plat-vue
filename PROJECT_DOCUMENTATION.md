# 虚拟币平台数据处理系统 - 项目文档

## 项目概述
这是一个专门用于处理虚拟币交易平台调证数据的 Web 应用系统，支持 CSV 和 Excel 文件的智能识别、数据提取和入库处理。

## 系统架构

### 前端 (Vue 3 + Element Plus)
- **入口文件**: `index.html`
- **主应用**: `src/App.vue`
- **主页面**: `src/views/HomeView.vue` - 文件上传界面
- **路由配置**: `src/router/index.js`
- **核心组件**: `src/components/` - 数据展示组件

### 后端 (Flask + MySQL)
- **Web 服务器**: `app.py` - Flask 主应用，提供 API 接口
- **数据处理引擎**: `scripts/main.py` - ETL 流程核心控制器
- **数据提取器**: `scripts/data_extract.py` - 4种数据识别方法
- **数据转换器**: `scripts/transforms.py` - 数据清洗和格式化
- **数据库工具**: `scripts/utils.py` - 数据库连接和操作
- **数据库查询**: `scripts/db_queries.py` - 数据查询接口

### 配置系统
- **模板配置**: `config/*.jsonc` - 各平台数据映射模板
  - `binance_map.jsonc` - 币安交易所模板
  - `okx_map.jsonc` - 欧意交易所模板
  - `imtoken_map.jsonc` - ImToken 钱包模板
  - `tokenpocket_map.jsonc` - TokenPocket 钱包模板
  - `csv_universal_map.jsonc` - 通用 CSV 模板

## 核心功能

### 1. 智能文件识别
系统支持 5 个主要平台的数据自动识别：
- 欧意 (OKX)
- 币安 (Binance)  
- 火币 (Huobi)
- ImToken
- TokenPocket

### 2. 4种数据提取方法
- **tabular**: 标准表格格式
- **find_subtable_by_header**: 基于标题查找子表格
- **form_layout**: 表单布局格式
- **merged_key_value**: 合并键值对格式

### 3. 数据库表结构
- `users` - 用户信息表
- `transactions` - 交易记录表
- `asset_movements` - 资产变动表
- `login_logs` - 登录日志表
- `devices` - 设备信息表

## 使用流程

1. **文件上传**: 用户在前端选择平台并上传文件
2. **自动识别**: 系统根据文件名识别平台类型
3. **模板匹配**: 加载对应平台的数据映射模板
4. **数据提取**: 使用4种方法之一提取数据
5. **数据转换**: 清洗和格式化数据
6. **入库保存**: 将数据写入MySQL数据库

## API 接口

### POST /api/upload
文件上传和处理接口
- 参数: `file` (文件), `company` (平台名称)
- 返回: 处理结果状态

### GET /api/search
数据查询接口
- 参数: `query` (查询条件)
- 返回: 查询结果数据

### GET /api/outline
数据大纲接口
- 参数: `query` (查询条件)
- 返回: 树形结构数据

### GET /api/mindmap_data
思维导图数据接口
- 参数: `user_id` (用户ID)
- 返回: 用户相关数据

## 环境配置

### 数据库配置 (scripts/main.py)
```python
DB_CONFIG = {
    'type': 'mysql',
    'user': 'root',
    'password': '123456',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'test_db'
}
```

### Python 环境
- conda 环境: `tweet_crawer`
- 主要依赖: Flask, pandas, openpyxl, mysql-connector-python, SQLAlchemy

## 文件存储
- **上传文件**: `uploads/` - 时间戳_平台_原文件名.扩展名
- **原始数据**: `data/` - JSON 格式的原始数据文件
- **调证资料**: `141数据调证数据/` - 各平台样本数据

## 项目特点

1. **模块化设计**: 各组件职责明确，易于维护
2. **配置驱动**: 通过 JSON 配置文件支持新平台
3. **多格式支持**: 同时支持 CSV 和 Excel 文件
4. **智能识别**: 自动识别文件类型和数据结构
5. **生产就绪**: 清理了所有测试代码，输出简洁

## 启动方式

1. 前端开发服务器: `npm run dev`
2. 后端 Flask 服务器: `python app.py`
3. 访问地址: http://localhost:5173 (前端) + http://localhost:5000 (后端API)

---
*最后更新: 2025年8月22日*
