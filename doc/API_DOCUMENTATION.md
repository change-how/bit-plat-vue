# 虚拟币平台数据处理系统 API 文档

## 概述

本文档描述了虚拟币平台数据处理系统的 RESTful API 接口。系统支持多个虚拟币平台的数据上传、处理和查询功能。

### 基础信息

- **基础URL**: `http://localhost:5000`
- **API前缀**: `/api`
- **支持格式**: JSON
- **编码**: UTF-8
- **CORS**: 已启用，支持跨域访问

### 支持的平台

- 欧意 (OKX)
- 币安 (Binance)
- 火币 (Huobi)
- ImToken
- TokenPocket

---

## API 接口列表

### 1. 数据搜索接口

**获取指定地址的数据**

```http
GET /api/search?query={address}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| query | string | 是 | 要查询的地址字符串 |

#### 请求示例

```bash
curl -X GET "http://localhost:5000/api/search?query=1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw"
```

#### 响应格式

**成功响应** (200)
```json
{
  "status": "success",
  "data": {
    // 地址相关的完整数据对象
    "address": "1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw",
    "transactions": [...],
    "balance": "...",
    // ... 其他数据字段
  }
}
```

**错误响应**
```json
{
  "status": "error",
  "message": "未找到地址 '1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw' 对应的数据文件。"
}
```

#### 错误状态码

- `400`: 缺少查询参数
- `404`: 未找到对应数据文件
- `500`: 服务器内部错误

---

### 2. 数据大纲接口

**获取数据的树形结构大纲**

```http
GET /api/outline?query={address}
```

#### 请求参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| query | string | 是 | 要查询的地址字符串 |

#### 请求示例

```bash
curl -X GET "http://localhost:5000/api/outline?query=1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw"
```

#### 响应格式

**成功响应** (200)
```json
{
  "status": "success",
  "data": [
    {
      "label": "节点名称",
      "children": [
        {
          "label": "子节点名称",
          "children": [...]
        }
      ]
    }
  ]
}
```

**错误响应**
```json
{
  "status": "error",
  "message": "未找到地址 '...' 对应的数据文件。"
}
```

#### 错误状态码

- `400`: 缺少查询参数
- `404`: 未找到对应数据文件
- `500`: 服务器内部错误

---

### 3. 文件上传接口

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

### 4. 思维导图数据接口

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
// 搜索数据
fetch('/api/search?query=1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw')
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      console.log('数据:', data.data);
    } else {
      console.error('错误:', data.message);
    }
  });

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

# 搜索数据
response = requests.get(
    'http://localhost:5000/api/search',
    params={'query': '1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw'}
)
data = response.json()

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
