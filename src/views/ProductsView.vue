<template>
  <div class="products-container">
    <h1>接口API</h1>
    <div class="content">
      <h2>API概览</h2>
      <p>本平台提供RESTful API接口，支持程序化数据查询和分析。</p>
      
      <div class="api-section">
        <h3>1. 用户搜索接口</h3>
        <div class="api-details">
          <p><strong>接口地址：</strong><code>GET /api/search_uid</code></p>
          <p><strong>参数：</strong><code>query</code> - 用户ID、邮箱或手机号</p>
          <p><strong>返回：</strong>匹配的用户信息列表</p>
        </div>
      </div>
      
      <div class="api-section">
        <h3>2. 思维导图数据接口</h3>
        <div class="api-details">
          <p><strong>接口地址：</strong><code>GET /api/mindmap_data</code></p>
          <p><strong>参数：</strong><code>user_id</code> - 用户唯一标识</p>
          <p><strong>返回：</strong>完整的用户关联数据（交易、资产、登录等）</p>
        </div>
      </div>
      
      <div class="api-section">
        <h3>3. 文件下载接口</h3>
        <div class="api-details">
          <p><strong>接口地址：</strong><code>GET /api/download/{filename}</code></p>
          <p><strong>参数：</strong><code>filename</code> - 文件名</p>
          <p><strong>返回：</strong>文件二进制数据</p>
        </div>
      </div>
      
      <h2>使用示例</h2>
      <div class="code-example">
        <pre><code>// 搜索用户
fetch('/api/search_uid?query=user@example.com')
  .then(response => response.json())
  .then(data => console.log(data));

// 获取思维导图数据  
fetch('/api/mindmap_data?user_id=12345')
  .then(response => response.json())
  .then(data => console.log(data));</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup>
// API文档页面
</script>

<style scoped>
.products-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 40px;
}

.content h2 {
  color: #555;
  margin-top: 30px;
  margin-bottom: 15px;
}

.content h3 {
  color: #666;
  margin-top: 25px;
  margin-bottom: 10px;
}

.api-section {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 20px;
  margin: 20px 0;
}

.api-details p {
  margin: 8px 0;
  line-height: 1.6;
}

.api-details code {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', monospace;
}

.code-example {
  background: #2d3748;
  color: #e2e8f0;
  padding: 20px;
  border-radius: 6px;
  margin: 20px 0;
  overflow-x: auto;
}

.code-example pre {
  margin: 0;
  font-family: 'Consolas', monospace;
  line-height: 1.5;
}
</style>
