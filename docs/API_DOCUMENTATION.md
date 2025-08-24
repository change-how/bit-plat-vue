# 虚拟币平台数据处理系统 API 文档

## 📋 项目概述

虚拟币平台数据处理系统是一个企业级的数据处理与可视化平台，专门用于处理各大虚拟币交易平台的调证数据。系统支持Excel文件上传、自动化数据提取、标准化存储以及思维导图形式的数据可视化展示。

### 🏗️ 系统架构

```
Frontend (Vue.js 3)  ←→  Backend (Flask)  ←→  Database (MySQL)
        ↓                      ↓                    ↓
   数据可视化               ETL数据处理           标准化存储
   思维导图展示             配置驱动映射           6张核心表
```

### 💻 技术栈

- **前端**: Vue.js 3 + Element Plus + simple-mind-map
- **后端**: Flask + SQLAlchemy + pandas
- **数据库**: MySQL 5.7+
- **文件处理**: openpyxl + pandas

### 🎯 支持的平台

| 平台 | 标识符 | 配置文件 | 支持格式 |
|------|--------|----------|----------|
| 欧易 | okx | okx_map.jsonc | Excel |
| 币安 | binance | binance_map.jsonc | Excel |
| 火币 | huobi | huobi_map.jsonc | Excel |
| ImToken | imtoken | imtoken_map.jsonc | CSV/Excel |
| TokenPocket | tokenpocket | tokenpocket_map.jsonc | CSV/Excel |

---

## 🔗 API 接口文档

### 基础信息

- **Base URL**: `http://localhost:5000`
- **API 前缀**: `/api`
- **Content-Type**: `application/json`
- **编码**: UTF-8
- **CORS**: 已启用跨域访问

---

## 1. 用户搜索接口

### `GET /api/search_uid`

**功能**: 通过关键词模糊搜索用户信息

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | 是 | 搜索关键词（支持姓名、手机号、邮箱、用户ID、IP地址、设备ID、钱包地址等） |

#### 请求示例

```bash
# 按姓名搜索
curl "http://localhost:5000/api/search_uid?query=张三"

# 按手机号搜索
curl "http://localhost:5000/api/search_uid?query=138"

# 按用户ID搜索
curl "http://localhost:5000/api/search_uid?query=12345"

# 按IP地址搜索
curl "http://localhost:5000/api/search_uid?query=192.168"
```

#### 响应格式

```json
{
  "status": "success",
  "users": [
    {
      "user_id": "12345",
      "name": "张三",
      "phone_number": "13800138000",
      "email": "zhangsan@example.com",
      "source": "OKX",
      "match_type": "用户信息",
      "match_details": "姓名: 张三 | 手机: 13800138000"
    }
  ],
  "count": 1
}
```

#### 错误响应

```json
{
  "status": "error",
  "message": "查询参数不能为空"
}
```

---

## 2. 数据获取接口

### `GET /api/mindmap_data`

**功能**: 获取指定用户的完整数据，用于思维导图展示

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| user_id | string | 是 | 用户ID |

#### 请求示例

```bash
curl "http://localhost:5000/api/mindmap_data?user_id=12345"
```

#### 响应格式

```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "user_id": "12345",
        "name": "张三",
        "phone_number": "13800138000",
        "email": "zhangsan@example.com",
        "registration_time": "2023-01-15T10:30:00",
        "source": "OKX",
        "source_file_name": "okx_data_20231215.xlsx"
      }
    ],
    "transactions": [
      {
        "user_id": "12345",
        "transaction_id": "TXN001",
        "transaction_time": "2023-12-15T14:30:00",
        "transaction_type": "SPOT",
        "direction": "BUY",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "price": "42000.50",
        "quantity": "0.1",
        "total_amount": "4200.05",
        "fee": "4.20",
        "fee_asset": "USDT",
        "source": "OKX",
        "source_file_name": "okx_data_20231215.xlsx"
      }
    ],
    "asset_movements": [
      {
        "user_id": "12345",
        "direction": "DEPOSIT",
        "asset": "BTC",
        "quantity": "0.5",
        "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "txid": "abc123def456",
        "network": "BTC",
        "transaction_time": "2023-12-15T12:00:00",
        "status": "SUCCESS",
        "source": "OKX",
        "source_file_name": "okx_data_20231215.xlsx"
      }
    ],
    "login_logs": [
      {
        "user_id": "12345",
        "login_time": "2023-12-15T09:00:00",
        "login_ip": "192.168.1.100",
        "device_id": "DEVICE001",
        "source": "OKX",
        "source_file_name": "okx_data_20231215.xlsx"
      }
    ],
    "devices": [
      {
        "user_id": "12345",
        "device_id": "DEVICE001",
        "client_type": "iOS",
        "ip_address": "192.168.1.100",
        "add_time": "2023-01-15T10:30:00",
        "source": "OKX",
        "source_file_name": "okx_data_20231215.xlsx"
      }
    ],
    "source_files": [
      {
        "file_name": "1734567890_okx_data_20231215.xlsx",
        "original_filename": "OKX陈兆群.xlsx",
        "file_size": "2.5 MB",
        "file_type": "xlsx",
        "upload_time": "2023-12-15 16:30:45",
        "platform": "OKX",
        "record_count": 150,
        "status": "已处理"
      }
    ]
  }
}
```

---

## 3. 文件上传接口

### `POST /api/upload`

**功能**: 上传Excel/CSV文件并自动处理

#### 请求参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| file | file | 是 | 要上传的Excel或CSV文件 |
| company | string | 是 | 平台标识符（okx、binance、huobi、imtoken、tokenpocket） |

#### 请求示例

```bash
curl -X POST \
  -F "file=@okx_data.xlsx" \
  -F "company=okx" \
  http://localhost:5000/api/upload
```

#### 响应格式

**成功响应:**
```json
{
  "status": "success",
  "message": "文件上传并处理成功",
  "data": {
    "filename": "1734567890_okx_data.xlsx",
    "original_filename": "okx_data.xlsx",
    "file_size": "2.5 MB",
    "platform": "OKX",
    "processed_records": {
      "users": 1,
      "transactions": 50,
      "asset_movements": 20,
      "login_logs": 30,
      "devices": 5
    },
    "upload_time": "2023-12-15 16:30:45"
  }
}
```

**错误响应:**
```json
{
  "status": "error",
  "message": "文件格式不支持，请上传Excel或CSV文件",
  "error_type": "FILE_FORMAT_ERROR"
}
```

---

## 📊 数据库结构

### 核心表设计

系统采用标准化的6表设计：

#### 1. users - 用户信息表
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50),           -- 数据来源平台
    user_id VARCHAR(255) UNIQUE,  -- 用户ID
    name VARCHAR(255),            -- 姓名
    registration_time DATETIME,   -- 注册时间
    phone_number VARCHAR(100),    -- 手机号
    email VARCHAR(255),           -- 邮箱
    source_file_name TEXT,        -- 源文件名
    extra_data JSON               -- 额外数据
);
```

#### 2. transactions - 交易记录表
```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50),
    user_id VARCHAR(255),
    transaction_id VARCHAR(255),
    transaction_time DATETIME,
    transaction_type VARCHAR(50),   -- 交易类型
    direction VARCHAR(50),          -- 买卖方向
    base_asset VARCHAR(50),         -- 基础币种
    quote_asset VARCHAR(50),        -- 计价币种
    price DECIMAL(36, 18),          -- 价格
    quantity DECIMAL(36, 18),       -- 数量
    total_amount DECIMAL(36, 18),   -- 总金额
    fee DECIMAL(36, 18),            -- 手续费
    fee_asset VARCHAR(50),          -- 手续费币种
    source_file_name TEXT,
    extra_data JSON
);
```

#### 3. asset_movements - 充提记录表
```sql
CREATE TABLE asset_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50),
    user_id VARCHAR(255),
    direction VARCHAR(50),          -- 充币/提币
    asset VARCHAR(50),              -- 币种
    quantity DECIMAL(36, 18),       -- 数量
    address TEXT,                   -- 地址
    txid TEXT,                      -- 交易哈希
    network VARCHAR(100),           -- 网络
    transaction_time DATETIME,      -- 交易时间
    status VARCHAR(100),            -- 状态
    source_file_name TEXT,
    extra_data JSON
);
```

#### 4. login_logs - 登录日志表
```sql
CREATE TABLE login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50),
    user_id VARCHAR(255),
    login_time DATETIME,            -- 登录时间
    login_ip VARCHAR(100),          -- 登录IP
    device_id VARCHAR(255),         -- 设备ID
    source_file_name TEXT,
    extra_data JSON
);
```

#### 5. devices - 设备信息表
```sql
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(50),
    user_id VARCHAR(255),
    device_id VARCHAR(255),         -- 设备ID
    client_type VARCHAR(100),       -- 客户端类型
    ip_address VARCHAR(100),        -- IP地址
    add_time DATETIME,              -- 添加时间
    source_file_name TEXT,
    extra_data JSON
);
```

#### 6. file_metadata - 文件元信息表
```sql
CREATE TABLE file_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_name VARCHAR(255) UNIQUE NOT NULL,    -- 存储文件名
    original_filename VARCHAR(255),            -- 原始文件名
    file_size BIGINT,                          -- 文件大小
    file_type VARCHAR(20),                     -- 文件类型
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    platform VARCHAR(50),                     -- 平台
    record_count INT DEFAULT 0,               -- 记录数
    status VARCHAR(50) DEFAULT '已处理'        -- 处理状态
);
```

---

## 🔧 配置系统

### 配置文件结构

系统使用JSONC格式的配置文件来定义数据映射规则：

```jsonc
{
  "metadata": {
    "source_name": "OKX",
    "version": "7.0",
    "display_name": "OKX 完整版调证模板"
  },
  "sources": [
    {
      "source_id": "user_info_raw",
      "worksheet_name": "用户信息",
      "data_layout": "form_layout",
      "section_header_aliases": ["uuid", "姓名"],
      "header_offset": 0
    }
  ],
  "destinations": [
    {
      "target_table": "users",
      "primary_source": "user_info_raw",
      "mappings": [
        {
          "target_field": "user_id",
          "source_field_aliases": ["uuid"]
        },
        {
          "target_field": "name",
          "source_field_aliases": ["姓名"]
        }
      ]
    }
  ]
}
```

---

## 🚀 部署说明

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Node.js 16+

### 后端部署

1. **安装依赖**
```bash
pip install flask flask-cors pandas sqlalchemy mysql-connector-python openpyxl
```

2. **配置数据库**
```python
# scripts/main.py
DB_CONFIG = {
    'type': 'mysql',
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'port': '3306',
    'db_name': 'your_database'
}
```

3. **初始化数据库**
```bash
python scripts/db_setup.py
```

4. **启动服务**
```bash
python app.py
```

### 前端部署

1. **安装依赖**
```bash
npm install
```

2. **开发模式**
```bash
npm run dev
```

3. **生产构建**
```bash
npm run build
```

---

## 🔍 错误码说明

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| FILE_FORMAT_ERROR | 文件格式不支持 | 请上传Excel或CSV文件 |
| TEMPLATE_NOT_FOUND | 找不到平台配置模板 | 检查平台标识符是否正确 |
| DATABASE_ERROR | 数据库连接失败 | 检查数据库配置和连接 |
| PROCESSING_ERROR | 数据处理失败 | 检查文件格式和数据完整性 |
| VALIDATION_ERROR | 数据验证失败 | 检查必填字段是否完整 |

---

## 📝 开发指南

### 添加新平台支持

1. **创建配置文件**
   - 在 `config/` 目录下创建新的映射文件
   - 参考现有配置文件格式

2. **更新平台注册表**
   - 在 `scripts/main.py` 的 `TEMPLATE_REGISTRY` 中添加新平台

3. **前端支持**
   - 在 `HomeView.vue` 的 `companies` 数组中添加新平台

### 扩展数据转换函数

1. **添加转换函数**
   - 在 `scripts/transforms.py` 中定义新函数

2. **注册函数**
   - 在 `scripts/main.py` 的 `FUNCTION_REGISTRY` 中注册

---

## 📞 技术支持

如需技术支持或有疑问，请联系开发团队。

**版本**: v1.0.0  
**最后更新**: 2024年12月18日

**成功响应** (200)
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "user_id": "user123",
      "name": "张三",
      "phone_number": "13812345678",
      "email": "zhangsan@example.com",
      "source": "OKX",
      "match_type": "用户信息",
      "match_details": "手机: 13812345678"
    },
    {
      "user_id": "user456", 
      "name": "李四",
      "phone_number": "",
      "email": "",
      "source": "Binance",
      "match_type": "登录日志",
      "match_details": "登录IP: 192.168.1.100"
    }
  ]
}
```

**错误响应**
```json
{
  "status": "error",
  "message": "未找到匹配 '搜索词' 的用户信息"
}
```

#### 错误状态码

- `400`: 缺少查询参数
- `404`: 未找到匹配的用户
- `500`: 服务器内部错误

#### 支持的查找字段

| 表名 | 支持的字段 | 描述 |
|------|-----------|------|
| users | name, phone_number, email, source | 用户基本信息 |
| login_logs | login_ip, device_id | 登录日志信息 |
| devices | device_id, client_type, ip_address | 设备信息 |
| asset_movements | address, txid, network | 资产流水信息 |

---

### 2. 文件上传接口

**上传并处理虚拟币平台数据文件**

```http
POST /api/upload
```

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| file | file | 是 | 要上传的文件 (支持 .xls, .xlsx, .csv) |
| company | string | 是 | 平台名称 (欧意/币安/火币/ImToken/TokenPocket) |

#### 文件要求

- **支持格式**: `.xls`, `.xlsx`, `.csv`
- **最大大小**: 100MB
- **编码**: 支持UTF-8

#### 请求示例

```bash
curl -X POST \
  -F "file=@data.xlsx" \
  -F "company=欧意" \
  "http://localhost:5000/api/upload"
```

#### 响应格式

**成功响应** (200)
```json
{
  "success": true,
  "message": "文件处理成功",
  "data": {
    "filename": "1642123456_okx_data.xlsx",
    "original_filename": "data.xlsx",
    "platform": "欧意",
    "processed_at": "1642123456"
  }
}
```

**错误响应**
```json
{
  "success": false,
  "error": {
    "type": "FILE_FORMAT_ERROR",
    "title": "文件格式不支持",
    "user_message": "文件格式 'txt' 不受支持",
    "suggestions": [
      "请上传Excel文件(.xlsx, .xls)或CSV文件",
      "确认文件未损坏",
      "尝试重新导出文件"
    ]
  }
}
```

#### 错误类型

| 错误类型 | 描述 | HTTP状态码 |
|----------|------|------------|
| `INVALID_REQUEST` | 请求格式错误 | 400 |
| `FILE_FORMAT_ERROR` | 文件格式不支持 | 400 |
| `FILE_TOO_LARGE` | 文件过大 | 400 |
| `PROCESSING_ERROR` | 数据处理失败 | 500 |
| `UNKNOWN_ERROR` | 未知错误 | 500 |
| `SERVER_ERROR` | 服务器错误 | 500 |

#### 支持的平台映射

| 前端显示名称 | 后端识别码 |
|-------------|-----------|
| 欧意 | okx |
| 币安 | binance |
| 火币 | huobi |
| ImToken | imtoken |
| TokenPocket | tokenpocket |

---

### 2. 思维导图数据接口

**获取指定用户的思维导图数据**

```http
GET /api/mindmap_data?user_id={user_id}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID |

#### 请求示例

```bash
curl -X GET "http://localhost:5000/api/mindmap_data?user_id=user123"
```

#### 响应格式

**成功响应** (200)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": "user123",
      "transaction_time": "2024-01-01 10:00:00",
      "amount": "1000.00",
      "currency": "BTC",
      // ... 其他数据字段
    }
  ]
}
```

**错误响应**
```json
{
  "status": "error",
  "message": "无法从数据库获取数据或数据为空"
}
```

#### 错误状态码

- `400`: 缺少 user_id 参数
- `404`: 无法获取数据或数据为空
- `500`: 服务器内部错误

---

## 数据处理流程

### ETL处理过程

1. **文件上传**: 接收并验证上传文件
2. **文件保存**: 使用时间戳和平台前缀重命名文件
3. **数据提取**: 根据平台类型和配置提取数据
4. **数据转换**: 清洗和标准化数据格式
5. **数据加载**: 将处理后的数据存储到数据库

### 配置文件映射

系统使用配置文件来映射不同平台的数据格式：

- `config/okx_map.jsonc` - 欧意平台配置
- `config/binance_map.jsonc` - 币安平台配置
- `config/huobi_map.jsonc` - 火币平台配置
- `config/imtoken_map_v2.jsonc` - ImToken平台配置
- `config/tokenpocket_map.jsonc` - TokenPocket平台配置

---

## 错误处理

### 统一错误格式

所有错误响应都采用统一格式：

```json
{
  "success": false,
  "error": {
    "type": "ERROR_TYPE",
    "title": "错误标题",
    "user_message": "用户友好的错误描述",
    "details": "详细错误信息（可选）",
    "suggestions": [
      "建议解决方案1",
      "建议解决方案2"
    ]
  }
}
```

### 常见错误场景

1. **文件格式错误**: 上传非支持格式的文件
2. **文件过大**: 文件超过100MB限制
3. **数据格式不匹配**: 文件内容与所选平台不匹配
4. **数据库连接失败**: 无法连接到数据库
5. **配置文件缺失**: 缺少平台对应的配置文件

---

## 使用示例

### JavaScript/Ajax 示例

```javascript
// 模糊查找用户ID
fetch('/api/search_uid?query=138')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log('找到用户:', data.data);
      console.log('匹配数量:', data.count);
      
      // 如果找到多个用户，可以让用户选择
      if (data.count > 1) {
        // 显示用户选择界面
        showUserSelectionDialog(data.data);
      } else if (data.count === 1) {
        // 直接使用唯一的用户ID获取思维导图数据
        const userId = data.data[0].user_id;
        getMindmapData(userId);
      }
    } else {
      console.error('查找失败:', data.message);
    }
  });

// 获取思维导图数据
function getMindmapData(userId) {
  fetch(`/api/mindmap_data?user_id=${userId}`)
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        console.log('思维导图数据:', data.data);
        // 在前端展示思维导图
        renderMindmap(data.data);
      } else {
        console.error('获取数据失败:', data.message);
      }
    });
}

// 文件上传
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('company', '欧意');

fetch('/api/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('上传成功:', data.message);
  } else {
    console.error('上传失败:', data.error.user_message);
  }
});
```

### Python 示例

```python
import requests

# 模糊查找用户ID
response = requests.get(
    'http://localhost:5000/api/search_uid',
    params={'query': '138'}
)
search_result = response.json()

if search_result['status'] == 'success':
    users = search_result['data']
    print(f"找到 {len(users)} 个匹配用户")
    
    # 选择第一个用户或让用户选择
    if users:
        selected_user_id = users[0]['user_id']
        
        # 获取思维导图数据
        mindmap_response = requests.get(
            'http://localhost:5000/api/mindmap_data',
            params={'user_id': selected_user_id}
        )
        mindmap_data = mindmap_response.json()
        
        if mindmap_data['status'] == 'success':
            print("思维导图数据:", mindmap_data['data'])

# 文件上传
files = {'file': open('data.xlsx', 'rb')}
data = {'company': '欧意'}
response = requests.post(
    'http://localhost:5000/api/upload',
    files=files,
    data=data
)
result = response.json()
```

---

## 系统配置

### 数据库配置

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

### 文件存储

- **上传目录**: `uploads/`
- **数据文件**: `data/`
- **配置文件**: `config/`

---

## 安全说明

1. **文件名安全**: 自动清理文件名中的危险字符
2. **文件大小限制**: 最大100MB，防止资源耗尽
3. **格式验证**: 只允许特定格式的文件上传
4. **CORS配置**: 仅允许API路径的跨域访问
5. **错误信息**: 避免泄露敏感的系统信息

---

## 版本信息

- **API版本**: v1.0
- **最后更新**: 2025年8月23日
- **兼容性**: Flask 2.x, Python 3.8+

---

## 联系支持

如有问题或建议，请联系技术支持团队。
