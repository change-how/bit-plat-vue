<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { UploadFilled } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus'; // 引入 ElMessage 和 ElMessageBox

// --- 状态定义 (State) ---
// 页面核心状态
const searchQuery = ref('');
const router = useRouter();

// 上传悬浮窗相关状态
const dialogUploadVisible = ref(false);
const companies = ref(['欧意', '币安', '火币', 'ImToken', 'TokenPocket']);
const selectedCompany = ref('');


// --- 生命周期钩子 (Lifecycle Hooks) ---
onMounted(() => {
  // 初始化公司选择，实现记忆功能
  const savedCompany = localStorage.getItem('lastSelectedCompany');
  if (savedCompany && companies.value.includes(savedCompany)) {
    selectedCompany.value = savedCompany;
  } else {
    selectedCompany.value = companies.value[0]; // 默认选择第一个
  }
});


// --- 方法定义 (Methods) ---

/**
 * 处理页面主搜索逻辑
 */
function handleSearch() {
  const queryValue = searchQuery.value.trim();
  if (!queryValue) {
    ElMessage.warning('请输入查询内容！'); // 使用 ElMessage 提升体验
    return;
  }
  router.push({
    name: 'results',
    params: { query: queryValue },
  });
}

/**
 * 上传前的验证函数
 * @param {object} file - 文件对象
 */
function beforeUpload(file) {
  // 验证文件大小（100MB限制）
  const maxSize = 100 * 1024 * 1024; // 100MB
  if (file.size > maxSize) {
    ElMessage.error({
      message: `文件大小不能超过100MB，当前文件大小: ${(file.size / (1024 * 1024)).toFixed(1)}MB`,
      duration: 5000,
      showClose: true
    });
    return false;
  }
  
  // 验证文件类型
  const allowedTypes = ['.xls', '.xlsx', '.csv'];
  const fileName = file.name.toLowerCase();
  const isValidType = allowedTypes.some(type => fileName.endsWith(type));
  
  if (!isValidType) {
    ElMessage.error({
      message: `不支持的文件格式，请上传Excel(.xlsx/.xls)或CSV文件`,
      duration: 5000,
      showClose: true
    });
    return false;
  }
  
  return true;
}

/**
 * el-upload 上传成功后的回调函数
 * @param {object} response - 服务器返回的响应
 * @param {object} uploadFile - 上传的文件信息对象
 */
function handleUploadSuccess(response, uploadFile) {
  console.log('收到服务器响应:', response);
  
  // 检查响应是否为成功
  if (response && response.success === true) {
    // 1. 保存当前选择，用于下次记忆
    localStorage.setItem('lastSelectedCompany', selectedCompany.value);

    // 2. 关闭悬浮窗
    dialogUploadVisible.value = false;

    // 3. 给出成功提示
    ElMessage.success({
      message: response.message || '文件上传和处理成功！',
      duration: 5000,
      showClose: true
    });
  } else {
    // 处理服务器返回的错误响应（即使HTTP状态码是200，但success为false）
    console.error('服务器返回错误:', response);
    handleErrorResponse(response);
  }
}

/**
 * 处理错误响应的统一函数
 * @param {object} errorResponse - 错误响应对象
 */
function handleErrorResponse(errorResponse) {
  console.log('handleErrorResponse 被调用，参数:', errorResponse);
  
  const error = errorResponse.error || {};
  
  // 基础错误消息
  const title = error.title || error.user_message || '处理文件时发生错误';
  
  console.log('基础错误消息:', title);
  
  // 构建详细的错误内容（HTML格式）
  let detailsHtml = `<div style="text-align: left;">`;
  
  // 添加主要错误信息
  detailsHtml += `<div style="font-size: 16px; font-weight: bold; color: #e74c3c; margin-bottom: 16px;">`;
  detailsHtml += `🚫 ${title}`;
  detailsHtml += `</div>`;
  
  // 添加详细信息
  if (error.details) {
    // 尝试解析结构化错误信息（多模板错误）
    let structuredError = null;
    try {
      structuredError = JSON.parse(error.details);
    } catch (e) {
      // 不是JSON格式，使用原始文本
    }
    
    if (structuredError && structuredError.template_errors && structuredError.template_errors.length > 0) {
      // 处理多模板结构化错误
      detailsHtml += `<div style="margin-bottom: 16px;">`;
      detailsHtml += `<div style="font-weight: bold; color: #2c3e50; margin-bottom: 12px;">📋 模板匹配详情：</div>`;
      
      // 显示平台和模板数量概述
      detailsHtml += `<div style="background: #f8f9fa; padding: 12px; border-radius: 6px; margin-bottom: 12px; border-left: 4px solid #3498db;">`;
      detailsHtml += `<div style="font-weight: bold; color: #2c3e50; margin-bottom: 8px;">📊 ${structuredError.platform} 平台</div>`;
      detailsHtml += `<div style="color: #555; font-size: 14px;">已测试 ${structuredError.template_count} 个模板版本，均无法匹配您的文件</div>`;
      detailsHtml += `</div>`;
      
      // 显示每个模板的错误详情
      structuredError.template_errors.forEach((templateError, index) => {
        const isLast = index === structuredError.template_errors.length - 1;
        
        detailsHtml += `<div style="background: #fff5f5; padding: 12px; border-radius: 6px; margin-bottom: ${isLast ? '0' : '8px'}; border-left: 4px solid #e74c3c;">`;
        detailsHtml += `<div style="display: flex; align-items: center; margin-bottom: 6px;">`;
        detailsHtml += `<div style="background: #e74c3c; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; margin-right: 8px; flex-shrink: 0;">${index + 1}</div>`;
        detailsHtml += `<div style="font-weight: bold; color: #2c3e50;">${templateError.template_name}</div>`;
        detailsHtml += `</div>`;
        
        // 优化工作表名称的显示
        let errorDisplay = templateError.error_summary;
        if (errorDisplay.includes('缺少工作表：') && errorDisplay.length > 50) {
          // 如果工作表名称很长，进行换行处理
          const parts = errorDisplay.split('缺少工作表：');
          if (parts.length > 1) {
            const worksheetNames = parts[1];
            const names = worksheetNames.split('、');
            if (names.length > 3) {
              // 多于3个工作表时，按行显示
              let formattedNames = '';
              for (let i = 0; i < names.length; i += 3) {
                const batch = names.slice(i, i + 3);
                formattedNames += batch.join('、');
                if (i + 3 < names.length) {
                  formattedNames += '<br>　　　　　　';
                }
              }
              errorDisplay = `缺少工作表：<br>　　　　　　${formattedNames}`;
            }
          }
        }
        
        detailsHtml += `<div style="color: #e74c3c; font-size: 14px; margin-left: 28px; line-height: 1.6;">${errorDisplay}</div>`;
        detailsHtml += `</div>`;
      });
      
      detailsHtml += `</div>`;
    } else {
      // 处理普通错误信息
      detailsHtml += `<div style="margin-bottom: 16px;">`;
      detailsHtml += `<div style="font-weight: bold; color: #2c3e50; margin-bottom: 8px;">📋 错误详情：</div>`;
      detailsHtml += `<div style="background: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #e74c3c; font-size: 14px; color: #555; line-height: 1.5;">`;
      detailsHtml += error.details;
      detailsHtml += `</div>`;
      detailsHtml += `</div>`;
    }
  }
  
  // 添加建议信息
  if (error.suggestions && error.suggestions.length > 0) {
    detailsHtml += `<div style="margin-bottom: 16px;">`;
    detailsHtml += `<div style="font-weight: bold; color: #2c3e50; margin-bottom: 8px;">💡 解决建议：</div>`;
    detailsHtml += `<div style="background: #e8f5e8; padding: 16px; border-radius: 6px; border-left: 4px solid #27ae60;">`;
    
    let currentSection = '';
    error.suggestions.forEach(suggestion => {
      // 检查是否是空行（用于分段）
      if (suggestion.trim() === "") {
        detailsHtml += `<div style="height: 12px;"></div>`;
      } else if (suggestion.includes('：') && !suggestion.startsWith('•')) {
        // 主要标题（如 "🔍 模板匹配结果："）
        currentSection = suggestion;
        detailsHtml += `<div style="font-weight: bold; color: #2c3e50; margin-bottom: 8px; font-size: 15px;">${suggestion}</div>`;
      } else if (suggestion.startsWith('•')) {
        // 建议项
        const content = suggestion.substring(1).trim();
        detailsHtml += `<div style="display: flex; align-items: flex-start; margin-bottom: 6px;">`;
        detailsHtml += `<div style="color: #27ae60; margin-right: 8px; margin-top: 2px;">•</div>`;
        detailsHtml += `<div style="color: #555; font-size: 14px; line-height: 1.4;">${content}</div>`;
        detailsHtml += `</div>`;
      } else {
        // 普通文本（如数字信息）
        const textColor = suggestion.includes('已尝试') ? '#666' : '#555';
        const fontSize = suggestion.includes('已尝试') ? '13px' : '14px';
        detailsHtml += `<div style="margin-bottom: 6px; color: ${textColor}; font-size: ${fontSize}; margin-left: 4px;">${suggestion}</div>`;
      }
    });
    
    detailsHtml += `</div>`;
    detailsHtml += `</div>`;
  }
  
  detailsHtml += `</div>`;
  
  console.log('生成的详细错误HTML:', detailsHtml);

  // 使用 ElMessageBox 显示更美观的错误对话框
  ElMessageBox.alert(detailsHtml, '文件处理失败', {
    confirmButtonText: '我知道了',
    type: 'error',
    dangerouslyUseHTMLString: true,
    customStyle: {
      width: '700px',
      maxWidth: '95vw'
    },
    customClass: 'custom-error-dialog',
    beforeClose: (action, instance, done) => {
      done();
    }
  }).catch(() => {
    // 用户取消时不需要处理
  });

  // 在控制台输出完整错误信息，便于调试
  console.error('处理错误完成:', errorResponse);
}

/**
 * el-upload 上传失败后的回调函数
 * @param {Error} error - 错误对象
 * @param {object} uploadFile - 上传的文件信息对象
 */
function handleUploadError(error, uploadFile) {
  console.error('=== 上传错误开始分析 ===');
  console.error('错误对象类型:', typeof error);
  console.error('错误对象:', error);
  console.error('错误详情:', {
    message: error.message,
    status: error.status,
    responseText: error.responseText,
    response: error.response
  });
  
  let errorResponse = null;
  
  try {
    // Element Plus的上传组件错误处理
    // 服务器返回的错误通常在error.responseText中
    if (error.responseText) {
      console.log('尝试解析 responseText:', error.responseText);
      errorResponse = JSON.parse(error.responseText);
    } else if (error.response && error.response.data) {
      console.log('尝试解析 response.data:', error.response.data);
      errorResponse = error.response.data;
    } else if (error.response) {
      console.log('尝试解析 response:', error.response);
      errorResponse = error.response;
    } else if (error.message && typeof error.message === 'string' && error.message.trim().startsWith('{')) {
      // Element Plus 特殊情况：错误信息在 message 字段中作为 JSON 字符串
      console.log('尝试解析 error.message 中的 JSON:', error.message);
      errorResponse = JSON.parse(error.message);
    }
    
    console.log('解析的错误响应:', errorResponse);
    
    // 优先处理我们的结构化错误响应
    if (errorResponse && errorResponse.error) {
      console.log('找到结构化错误，使用详细错误处理');
      handleErrorResponse(errorResponse);
      return;
    }
    
    // 处理简单的错误信息
    if (errorResponse && errorResponse.success === false) {
      console.log('找到错误响应，使用详细错误处理');
      handleErrorResponse(errorResponse);
      return;
    }
    
    console.log('没有找到结构化错误响应，使用通用错误处理');
    
  } catch (e) {
    console.error('解析错误响应失败:', e);
    console.error('原始错误信息:', error.message);
    console.error('原始响应文本:', error.responseText);
  }
  
  // 如果无法解析服务器错误，显示通用错误消息
  let defaultMessage = '文件上传失败';
  
  // 根据错误状态码提供更具体的信息
  if (error.status) {
    switch (error.status) {
      case 400:
        defaultMessage = '请求格式错误，请检查文件格式和选择的平台';
        break;
      case 413:
        defaultMessage = '文件过大，请选择较小的文件';
        break;
      case 500:
        defaultMessage = '服务器内部错误，请稍后重试或联系技术支持';
        break;
      case 0:
        defaultMessage = '网络连接失败，请检查网络连接后重试';
        break;
      default:
        defaultMessage = `上传失败 (错误代码: ${error.status})`;
    }
  } else if (error.message) {
    if (error.message.includes('Network Error') || error.message.includes('timeout')) {
      defaultMessage = '网络连接失败，请检查网络连接后重试';
    } else {
      defaultMessage = `上传失败: ${error.message}`;
    }
  }
  
  ElMessage.error({
    message: defaultMessage,
    duration: 8000,
    showClose: true
  });
}
</script>

<template>
  <div class="main-container">
    <h1>虚拟币查询平台</h1>

    <form @submit.prevent="handleSearch" class="search-form">
      <div class="search-wrapper">
        <span class="search-label">单个要素查询</span>
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="请输入比特币地址或手机号..."
        />
        <button type="submit" class="btn query-button">查询</button>
        <button type="button" class="btn upload-button" @click="dialogUploadVisible = true">上传数据</button>
      </div>
    </form>
    
    <p>示例数据：1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw</p>
  </div>

  <el-dialog v-model="dialogUploadVisible" title="上传数据文件" width="500px">
    <div class="upload-dialog-content">
      <span>选择目标公司：</span>
      <el-select v-model="selectedCompany" placeholder="请选择公司" style="flex-grow: 1;">
        <el-option
          v-for="company in companies"
          :key="company"
          :label="company"
          :value="company"
        />
      </el-select>
    </div>

    <el-upload
      drag
      action="http://127.0.0.1:5000/api/upload"
      :data="{ company: selectedCompany }"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :before-upload="beforeUpload"
      :auto-upload="true"
      accept=".xls, .xlsx, .csv, .json"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 .xls, .xlsx, .csv, .json 格式的文件
        </div>
      </template>
    </el-upload>
  </el-dialog>
</template>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 110px); /* 减去header和footer的高度 */
  padding: 40px 20px;
  box-sizing: border-box;
}

.main-container h1 {
  font-size: 3em;
  color: #2c3e50;
  margin-bottom: 40px;
  text-align: center;
  font-weight: 600;
}

.search-form {
  width: 100%;
  max-width: 800px;
  margin-bottom: 30px;
}

.search-wrapper {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  flex-wrap: wrap;
  justify-content: center;
}

.search-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
  white-space: nowrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.query-button {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.query-button:hover {
  background: linear-gradient(135deg, #764ba2, #667eea);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.upload-button {
  background: linear-gradient(135deg, #52c41a, #389e0d);
  color: white;
}

.upload-button:hover {
  background: linear-gradient(135deg, #389e0d, #52c41a);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

.main-container p {
  color: #7f8c8d;
  font-size: 14px;
  text-align: center;
  margin: 0;
}

.upload-dialog-content {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.upload-dialog-content span {
  margin-right: 15px;
  font-weight: 500;
  color: #2c3e50;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-container {
    padding: 20px 10px;
  }
  
  .main-container h1 {
    font-size: 2em;
    margin-bottom: 30px;
  }
  
  .search-wrapper {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .search-input {
    min-width: auto;
    width: 100%;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .main-container h1 {
    font-size: 1.5em;
  }
  
  .search-wrapper {
    padding: 15px;
  }
  
  .btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>

<style>
/* 美化错误对话框样式 */
.custom-error-dialog {
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.custom-error-dialog .el-message-box__header {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;
    border-radius: 12px 12px 0 0;
    padding: 20px 24px;
}

.custom-error-dialog .el-message-box__title {
    color: white;
    font-weight: 600;
    font-size: 18px;
}

.custom-error-dialog .el-message-box__content {
    padding: 24px;
    max-height: 70vh;
    overflow-y: auto;
}

.custom-error-dialog .el-message-box__btns {
    padding: 16px 24px 20px;
    border-top: 1px solid #ebeef5;
}

.custom-error-dialog .el-button--primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.custom-error-dialog .el-button--primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 滚动条美化 */
.custom-error-dialog .el-message-box__content::-webkit-scrollbar {
    width: 6px;
}

.custom-error-dialog .el-message-box__content::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
}

.custom-error-dialog .el-message-box__content::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.custom-error-dialog .el-message-box__content::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}
</style>