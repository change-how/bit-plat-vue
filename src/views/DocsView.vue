<template>
  <div class="docs-container">
    <div class="docs-header">
      <h1>📚 项目文档中心</h1>
      <p>虚拟币平台数据处理系统 - 完整文档</p>
    </div>

    <div class="docs-grid">
      <!-- 快速入门卡片 -->
      <div class="doc-card primary">
        <div class="card-icon">🚀</div>
        <h3>快速入门</h3>
        <p>了解项目基本功能，快速上手使用系统</p>
        <div class="card-features">
          <span class="feature">环境搭建</span>
          <span class="feature">基本使用</span>
          <span class="feature">常见问题</span>
        </div>
        <div class="card-actions">
          <el-button type="primary" @click="openDoc('QUICK_START_GUIDE.md')">
            <el-icon><DocumentCopy /></el-icon>
            快速上手
          </el-button>
        </div>
      </div>

      <!-- README文档卡片 -->
      <div class="doc-card info">
        <div class="card-icon">📖</div>
        <h3>项目说明</h3>
        <p>项目概述、安装指南和基本配置说明</p>
        <div class="card-features">
          <span class="feature">项目概述</span>
          <span class="feature">安装指南</span>
          <span class="feature">基本配置</span>
        </div>
        <div class="card-actions">
          <el-button type="info" @click="openDoc('README.md')">
            <el-icon><Reading /></el-icon>
            查看README
          </el-button>
        </div>
      </div>

      <!-- API文档卡片 -->
      <div class="doc-card secondary">
        <div class="card-icon">📖</div>
        <h3>API 接口文档</h3>
        <p>详细的API接口说明，包含请求参数和响应格式</p>
        <div class="card-features">
          <span class="feature">接口规范</span>
          <span class="feature">数据格式</span>
          <span class="feature">错误处理</span>
        </div>
        <div class="card-actions">
          <el-button type="success" @click="openDoc('API_DOCUMENTATION.md')">
            <el-icon><Link /></el-icon>
            查看API
          </el-button>
        </div>
      </div>

      <!-- 架构文档卡片 -->
      <div class="doc-card tertiary">
        <div class="card-icon">🏗️</div>
        <h3>项目架构</h3>
        <p>深入了解系统设计和开发指南</p>
        <div class="card-features">
          <span class="feature">系统架构</span>
          <span class="feature">扩展指南</span>
          <span class="feature">最佳实践</span>
        </div>
        <div class="card-actions">
          <el-button type="warning" @click="openDoc('PROJECT_ARCHITECTURE.md')">
            <el-icon><Operation /></el-icon>
            查看架构
          </el-button>
        </div>
      </div>
    </div>

    <!-- 功能特性展示 -->
    <div class="features-section">
      <h2>🎯 核心特性</h2>
      <div class="features-grid">
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><Upload /></el-icon>
          <h4>文件上传</h4>
          <p>支持Excel/CSV文件自动解析和处理</p>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><Search /></el-icon>
          <h4>智能搜索</h4>
          <p>多字段模糊搜索，快速定位用户信息</p>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><DataBoard /></el-icon>
          <h4>可视化展示</h4>
          <p>思维导图形式展示数据关系</p>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><Setting /></el-icon>
          <h4>配置驱动</h4>
          <p>通过配置文件支持新平台接入</p>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><Database /></el-icon>
          <h4>标准化存储</h4>
          <p>统一的6表数据库设计</p>
        </div>
        <div class="feature-item">
          <el-icon class="feature-icon" size="32"><Tools /></el-icon>
          <h4>ETL处理</h4>
          <p>自动化数据提取、转换和加载</p>
        </div>
      </div>
    </div>

    <!-- 技术栈展示 -->
    <div class="tech-stack">
      <h2>🛠️ 技术栈</h2>
      <div class="tech-categories">
        <div class="tech-category">
          <h4>前端技术</h4>
          <div class="tech-tags">
            <el-tag>Vue.js 3</el-tag>
            <el-tag>Element Plus</el-tag>
            <el-tag>simple-mind-map</el-tag>
            <el-tag>Vite</el-tag>
          </div>
        </div>
        <div class="tech-category">
          <h4>后端技术</h4>
          <div class="tech-tags">
            <el-tag type="success">Flask</el-tag>
            <el-tag type="success">SQLAlchemy</el-tag>
            <el-tag type="success">pandas</el-tag>
            <el-tag type="success">openpyxl</el-tag>
          </div>
        </div>
        <div class="tech-category">
          <h4>数据存储</h4>
          <div class="tech-tags">
            <el-tag type="warning">MySQL</el-tag>
            <el-tag type="warning">文件系统</el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 平台支持 -->
    <div class="platforms-section">
      <h2>🏢 支持平台</h2>
      <div class="platforms-grid">
        <div class="platform-item">
          <div class="platform-logo">🏦</div>
          <h4>欧易 (OKX)</h4>
          <p>支持完整的调证数据处理</p>
        </div>
        <div class="platform-item">
          <div class="platform-logo">🌐</div>
          <h4>币安 (Binance)</h4>
          <p>全球最大交易所数据支持</p>
        </div>
        <div class="platform-item">
          <div class="platform-logo">🔥</div>
          <h4>火币 (Huobi)</h4>
          <p>专业的数据映射处理</p>
        </div>
        <div class="platform-item">
          <div class="platform-logo">💎</div>
          <h4>ImToken</h4>
          <p>去中心化钱包数据支持</p>
        </div>
        <div class="platform-item">
          <div class="platform-logo">🎯</div>
          <h4>TokenPocket</h4>
          <p>多链钱包数据处理</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { 
  DocumentCopy, 
  Link, 
  Operation, 
  Upload, 
  Search, 
  DataBoard, 
  Setting, 
  Database, 
  Tools,
  Reading
} from '@element-plus/icons-vue'

const openDoc = (filename) => {
  ElMessage.info(`文档位置: docs/${filename}`)
  
  // 如果需要在浏览器中打开文档，可以创建下载链接
  // 这里简单提示用户文档位置
  console.log(`请查看 docs 目录下的 ${filename} 文件`)
  
  // 可选：在新标签页中打开GitHub仓库的文档
  // window.open(`https://github.com/your-repo/blob/main/docs/${filename}`, '_blank')
}
</script>

<style scoped>
.docs-container {
  min-height: calc(100vh - 110px); /* 减去header和footer的高度 */
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 20px;
  overflow-y: auto;
}

.docs-header {
  text-align: center;
  margin-bottom: 50px;
}

.docs-header h1 {
  font-size: 2.5em;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 600;
}

.docs-header p {
  font-size: 1.2em;
  color: #7f8c8d;
  margin: 0;
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto 60px;
}

.doc-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.doc-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.doc-card.primary {
  border-color: #409eff;
}

.doc-card.secondary {
  border-color: #67c23a;
}

.doc-card.tertiary {
  border-color: #e6a23c;
}

.card-icon {
  font-size: 3em;
  text-align: center;
  margin-bottom: 20px;
}

.doc-card h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.4em;
  font-weight: 600;
}

.doc-card p {
  color: #7f8c8d;
  margin-bottom: 20px;
  line-height: 1.6;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 25px;
}

.feature {
  background: #f8f9fa;
  color: #495057;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  border: 1px solid #e9ecef;
}

.card-actions {
  text-align: center;
}

.features-section, .tech-stack, .platforms-section {
  max-width: 1200px;
  margin: 0 auto 60px;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
}

.features-section h2, .tech-stack h2, .platforms-section h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 1.8em;
  font-weight: 600;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
}

.feature-item {
  text-align: center;
  padding: 25px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.feature-icon {
  color: #409eff;
  margin-bottom: 15px;
}

.feature-item h4 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.1em;
  font-weight: 600;
}

.feature-item p {
  color: #6c757d;
  font-size: 0.9em;
  line-height: 1.5;
  margin: 0;
}

.tech-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.tech-category h4 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 1.1em;
  font-weight: 600;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 25px;
}

.platform-item {
  text-align: center;
  padding: 25px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.platform-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.platform-logo {
  font-size: 2.5em;
  margin-bottom: 15px;
}

.platform-item h4 {
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 1em;
  font-weight: 600;
}

.platform-item p {
  color: #6c757d;
  font-size: 0.85em;
  line-height: 1.4;
  margin: 0;
}

@media (max-width: 768px) {
  .docs-container {
    padding: 20px 10px;
  }
  
  .docs-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .doc-card {
    padding: 20px;
  }
  
  .features-section, .tech-stack, .platforms-section {
    padding: 25px;
    margin-bottom: 40px;
  }
}
</style>
