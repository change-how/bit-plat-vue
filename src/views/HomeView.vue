<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// --- 状态定义 ---
// 使用 ref 创建响应式变量，用于和模板中的元素进行绑定
const searchQuery = ref('');      // 绑定搜索输入框的内容
const uploadStatus = ref('');     // 绑定上传状态的文本
const uploadStatusColor = ref('');// 绑定上传状态文本的颜色

// --- 路由与导航 ---
// 获取路由实例，用于页面跳转
const router = useRouter();

// --- 方法定义 ---

/**
 * 处理搜索表单提交事件
 */
function handleSearch() {
  const queryValue = searchQuery.value.trim();
  if (!queryValue) {
    alert('请输入查询内容！');
    return;
  }
  
  // Vue 单页应用的核心导航方式：
  // 我们不再在这里获取数据，而是直接跳转到结果页，
  // 并将查询词作为参数放在 URL 中。
  // 数据获取的任务，将由结果页自己完成。
  router.push({
    name: 'results', // 对应我们在 router/index.js 中定义的名字
    params: { query: queryValue }
  });
}

/**
 * 触发隐藏的文件上传输入框
 */
function triggerFileUpload() {
  // 在 Vue 中，我们通常不推荐直接操作 DOM，但对于这种简单场景是可接受的。
  document.getElementById('file-uploader').click();
}

/**
 * 处理文件选择后的事件
 */
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const allowedExtensions = ['.xls', '.xlsx'];
  const fileName = file.name;
  const fileExtension = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();

  // 这里不再是操作 DOM，而是更新我们的响应式变量
  if (allowedExtensions.includes(fileExtension)) {
    uploadStatus.value = `文件 "${fileName}" 类型正确，准备上传... (模拟成功 ✓)`;
    uploadStatusColor.value = '#52c41a';
  } else {
    uploadStatus.value = '错误：请选择有效的 Excel 文件 (.xls 或 .xlsx)';
    uploadStatusColor.value = '#ff4d4f';
  }
}
</script>

<template>
    <div class="main-container">
        <h1>虚拟币查询平台</h1>

        <form @submit.prevent="handleSearch">
        <div class="search-wrapper">
            <span class="search-label">单个要素查询</span>
            
            <input 
            type="text" 
            v-model="searchQuery"
            class="search-input" 
            placeholder="请输入比特币地址或手机号..."
            >
            
            <button type="submit" class="btn query-button">查询</button>
            
            <button type="button" class="btn upload-button" @click="triggerFileUpload">上传数据</button>
        </div>
        </form>

        <input type="file" id="file-uploader" style="display: none;" accept=".xls, .xlsx" @change="handleFileUpload">
        
        <p id="upload-status" :style="{ color: uploadStatusColor }">{{ uploadStatus }}</p>
        <p>示例数据：1c1CxaD5GMxsiEzu5YM5EhHpNFWezWMWhw</p>
    </div>
</template>

<style scoped>
.main-container{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center; 
}

</style>