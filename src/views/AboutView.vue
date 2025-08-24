<template>
  <div class="about-container">
    <h1>使用手册</h1>
    <div class="content">
      <h2>系统介绍</h2>
      <p>虚拟币查询平台是一个专业的数字货币数据分析工具，支持多平台数据整合和可视化展示。</p>
      
      <h2>使用方法</h2>
      <ol>
        <li>在首页输入要查询的用户ID、邮箱或手机号</li>
        <li>系统将自动搜索相关用户信息</li>
        <li>查看思维导图形式的数据概览</li>
        <li>点击节点查看详细数据</li>
        <li>支持数据下载和导出</li>
      </ol>
      
      <h2>支持的平台</h2>
      <ul>
        <li>OKX交易所</li>
        <li>币安(Binance)</li>
        <li>火币(Huobi)</li>
        <li>ImToken钱包</li>
        <li>TokenPocket钱包</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 简单的关于页面，无需复杂逻辑
</script>

<style scoped>
.about-container {
  max-width: 800px;
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

.content p, .content li {
  line-height: 1.6;
  color: #666;
}

.content ol, .content ul {
  padding-left: 20px;
}
</style>
