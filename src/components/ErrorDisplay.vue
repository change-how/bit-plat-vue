<template>
  <div class="error-display">
    <!-- 错误卡片 -->
    <el-card v-if="error" class="error-card" shadow="hover">
      <template #header>
        <div class="error-header">
          <el-icon class="error-icon" :size="24" color="#F56C6C">
            <Warning />
          </el-icon>
          <span class="error-title">{{ error.title || '处理错误' }}</span>
        </div>
      </template>
      
      <!-- 主要错误信息 -->
      <div class="error-content">
        <p class="error-message">{{ error.user_message || error.message || '发生了未知错误' }}</p>
        
        <!-- 详细信息 -->
        <el-collapse v-if="error.details" class="error-details">
          <el-collapse-item title="查看详细信息" name="details">
            <div class="details-content">
              <code>{{ error.details }}</code>
            </div>
          </el-collapse-item>
        </el-collapse>
        
        <!-- 建议列表 -->
        <div v-if="error.suggestions && error.suggestions.length > 0" class="suggestions">
          <h4>解决建议：</h4>
          <ul>
            <li v-for="(suggestion, index) in error.suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
        
        <!-- 错误类型标签 -->
        <div v-if="error.type" class="error-type">
          <el-tag :type="getErrorTagType(error.type)" size="small">
            {{ getErrorTypeLabel(error.type) }}
          </el-tag>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <template #footer>
        <div class="error-actions">
          <el-button @click="$emit('retry')" type="primary" size="small">
            重试
          </el-button>
          <el-button @click="$emit('close')" size="small">
            关闭
          </el-button>
          <el-button @click="copyErrorInfo" size="small" type="info">
            复制错误信息
          </el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  error: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['retry', 'close'])

// 获取错误类型对应的标签样式
function getErrorTagType(errorType) {
  const typeMap = {
    'FILE_NOT_FOUND': 'warning',
    'FILE_FORMAT_ERROR': 'warning',
    'FILE_ENCODING_ERROR': 'warning',
    'FILE_EMPTY': 'info',
    'FILE_TOO_LARGE': 'warning',
    'DB_CONNECTION_ERROR': 'danger',
    'DB_WRITE_ERROR': 'danger',
    'DB_READ_ERROR': 'danger',
    'TEMPLATE_NOT_FOUND': 'warning',
    'COMPANY_NOT_RECOGNIZED': 'warning',
    'COLUMN_MISSING': 'warning',
    'DATA_VALIDATION_ERROR': 'warning',
    'NETWORK_ERROR': 'danger',
    'UNKNOWN_ERROR': 'danger'
  }
  return typeMap[errorType] || 'info'
}

// 获取错误类型的中文标签
function getErrorTypeLabel(errorType) {
  const labelMap = {
    'FILE_NOT_FOUND': '文件未找到',
    'FILE_FORMAT_ERROR': '文件格式错误',
    'FILE_ENCODING_ERROR': '文件编码错误',
    'FILE_EMPTY': '文件为空',
    'FILE_TOO_LARGE': '文件过大',
    'DB_CONNECTION_ERROR': '数据库连接错误',
    'DB_WRITE_ERROR': '数据库写入错误',
    'DB_READ_ERROR': '数据库读取错误',
    'TEMPLATE_NOT_FOUND': '模板未找到',
    'COMPANY_NOT_RECOGNIZED': '平台识别失败',
    'COLUMN_MISSING': '缺少必需列',
    'DATA_VALIDATION_ERROR': '数据验证失败',
    'NETWORK_ERROR': '网络错误',
    'UNKNOWN_ERROR': '未知错误'
  }
  return labelMap[errorType] || '系统错误'
}

// 复制错误信息到剪贴板
function copyErrorInfo() {
  if (!props.error) return
  
  let errorText = `错误类型: ${getErrorTypeLabel(props.error.type)}\n`
  errorText += `错误信息: ${props.error.user_message || props.error.message}\n`
  
  if (props.error.details) {
    errorText += `详细信息: ${props.error.details}\n`
  }
  
  if (props.error.suggestions && props.error.suggestions.length > 0) {
    errorText += `建议解决方案:\n`
    props.error.suggestions.forEach((suggestion, index) => {
      errorText += `${index + 1}. ${suggestion}\n`
    })
  }
  
  navigator.clipboard.writeText(errorText).then(() => {
    ElMessage.success('错误信息已复制到剪贴板')
  }).catch(() => {
    ElMessage.warning('复制失败，请手动复制')
  })
}
</script>

<style scoped>
.error-display {
  margin: 20px 0;
}

.error-card {
  border-left: 4px solid #F56C6C;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-title {
  font-weight: 600;
  font-size: 16px;
  color: #F56C6C;
}

.error-content {
  line-height: 1.6;
}

.error-message {
  margin-bottom: 16px;
  font-size: 14px;
  color: #666;
}

.error-details {
  margin: 16px 0;
}

.details-content {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
  word-break: break-all;
}

.suggestions {
  margin: 16px 0;
}

.suggestions h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #409EFF;
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 4px;
  font-size: 13px;
  color: #666;
}

.error-type {
  margin-top: 16px;
}

.error-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
