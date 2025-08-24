
<template>
  <div class="page-wrapper">
    <aside class="sidebar-left">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        <h2>大纲目录</h2>
      </div>
      <div class="sidebar-content">
        <div v-if="isMindMapLoading">正在加载大纲...</div>
        <div v-else-if="mindMapError">加载失败: {{ mindMapError }}</div>
        <outlinetree
          v-else
          :data="outlineData"      
          :props="defaultProps"
          node-key="id"
          :default-expanded-keys="[1]"
        />
      </div>
    </aside>

    <main class="main-content">
      <div class="main-content-header">
        <h3>数据图谱: {{ currentUserInfo?.name || queryAddress }}</h3>
      </div>
      <div v-if="isMindMapLoading" class="detail-panel-placeholder">正在加载图谱...</div>
      <div v-else-if="mindMapError" class="detail-panel-placeholder" style="color: #ff4d4f;">
        <p>查询失败: {{ mindMapError }}</p>
      </div>
      <div v-else id="mindMapContainer"></div>
      <!-- <GraphDisplay v-else-if="graphData" :graphData="mindMapData" /> -->
    </main>

    <aside class="sidebar-right">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
        <h2>节点详情</h2>
      </div>
      
      <div class="sidebar-content">
        <div v-if="isLoading" class="detail-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="!selectedNodeData" class="detail-placeholder">
          <el-icon><InfoFilled /></el-icon>
          <p>请点击思维导图中的节点查看详细信息</p>
          <div v-if="cachedData" class="cache-status">
            <el-icon style="color: #52c41a;"><SuccessFilled /></el-icon>
            <span>数据已缓存，点击节点瞬间显示</span>
          </div>
        </div>
        <div v-else-if="error" class="detail-error">
          <el-icon><WarningFilled /></el-icon>
          <p>{{ error }}</p>
        </div>
        <div v-else class="detail-content">
          <div class="detail-header">
            <h4>{{ selectedNodeData?.nodeData?.data?.text || selectedNodeData?.data?.text || '节点详情' }}</h4>
            <span class="data-count">{{ detailTableData.length }} 条记录</span>
          </div>
          
          <!-- 用户信息 - 竖向显示 -->
          <div v-if="selectedNodeType === 'users'" class="table-container">
            <div class="user-info-display">
              <div v-for="item in paginatedData" :key="item.user_id" class="user-info-card">
                <div class="info-row">
                  <span class="info-label">用户ID:</span>
                  <span class="info-value">{{ item.user_id }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">姓名:</span>
                  <span class="info-value">{{ item.name || '暂无' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">手机号:</span>
                  <span class="info-value">{{ item.phone_number || '暂无' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">邮箱:</span>
                  <span class="info-value">{{ item.email || '暂无' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">平台:</span>
                  <span class="info-value">{{ item.source || '暂无' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">创建时间:</span>
                  <span class="info-value">{{ item.registration_time || '暂无' }}</span>
                </div>
              </div>
            </div>
            <!-- 分页组件 -->
            <div class="pagination-container" v-if="totalItems > pageSize">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
                small
              />
            </div>
          </div>
          
          <!-- 源文件表格 - 带下载功能 -->
          <div v-else-if="selectedNodeType === 'source_files'" class="table-container">
            <el-table 
              :data="paginatedData"
              style="width: 100%"
              max-height="350"
              size="small"
              :cell-style="{ padding: '8px 4px' }"
              :header-cell-style="{ padding: '10px 4px' }"
            >
              <el-table-column prop="file_name" label="文件名" min-width="160" show-overflow-tooltip />
              <el-table-column prop="file_size" label="大小" min-width="80" />
              <el-table-column prop="upload_time" label="上传时间" min-width="120" />
              <el-table-column prop="platform" label="平台" min-width="80" />
              <el-table-column label="操作" min-width="80">
                <template #default="scope">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="handleFileDownload(scope.row.file_name)"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <!-- 分页组件 -->
            <div class="pagination-container" v-if="totalItems > pageSize">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
                small
              />
            </div>
          </div>
          
          <!-- 大数据量表格 - 使用虚拟滚动 -->
          <div v-else-if="detailTableData.length > 100" class="table-container virtual-table-container">
            <div class="virtual-table-info">
              <span>数据量较大({{ detailTableData.length }}条)，使用虚拟滚动显示</span>
            </div>
            <el-table-v2
              :columns="tableColumnsForV2"
              :data="detailTableData"
              :width="virtualTableWidth"
              :height="350"
              :row-height="45"
              :header-height="40"
              :scrollbar-always-on="true"
              class="virtual-table-with-scrollbar"
            />
          </div>
          
          <!-- 普通表格 -->
          <div v-else class="table-container">
            <el-table 
              :data="paginatedData"
              style="width: 100%"
              max-height="350"
              size="small"
              :cell-style="{ padding: '8px 4px' }"
              :header-cell-style="{ padding: '10px 4px' }"
            >
              <el-table-column 
                v-for="col in tableColumns" 
                :key="col.prop"
                :prop="col.prop"
                :label="col.label"
                :min-width="col.minWidth"
                show-overflow-tooltip
              />
            </el-table>
            <!-- 分页组件 -->
            <div class="pagination-container" v-if="totalItems > pageSize">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50, 100]"
                :total="totalItems"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handlePageChange"
                small
              />
            </div>
          </div>
        </div>
      </div>
    </aside>
  </div>
</template>



<script setup>

import { ref, onMounted, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { Loading, InfoFilled, WarningFilled, SuccessFilled } from '@element-plus/icons-vue';
import GraphDisplay from '../components/GraphDisplay.vue'; // 导入我们刚创建的图谱组件
import outlinetree from '../components/outlinetree.vue'
import ELtable from '../components/ELtable.vue'; // 导入我们刚创建的图谱组件
import MindMap from "simple-mind-map";
import data_test from '../../data/data_mindmap.json'; // 导入测试数据
import { transformToMindMapData } from '../utils/dataTransform.js'; // 导入数据转换工具

//计算大纲的函数
function extractNonLeafNodes(mindMapData) {
  // 定义一个内部递归函数，用于处理每个节点
  // 使用一个计数器来为每个节点生成唯一的ID，这在UI渲染中很有用
  let idCounter = 0;

  function recursiveTransform(node) {
    // 检查当前节点是否是非叶子节点。
    // 判断条件是：节点有 children 属性，该属性是数组，且数组不为空。
    const isNonLeaf = node && Array.isArray(node.children) && node.children.length > 0;

    // 如果不是非叶子节点（即叶子节点或空节点），则直接返回 null，表示在结果中舍弃它。
    if (!isNonLeaf) {
      return null;
    }

    // 如果是，则开始转换...
    // 1. 递归处理所有子节点
    const transformedChildren = node.children
      .map(child => recursiveTransform(child)) // 对每个子节点调用自身
      .filter(Boolean); // 关键一步：过滤掉所有返回 null 的结果（即所有叶子节点）

    // 2. 构建并返回符合新格式的节点对象
    return {
      id: ++idCounter, // 分配一个唯一的ID
      label: node.data.text, // 将 "data.text" 映射为 "label"
      children: transformedChildren, // 使用处理过的子节点数组
    };
  }

  // 从根节点开始执行转换
  const result = recursiveTransform(mindMapData);

  // 因为UI组件通常接收一个数组，而我们的转换结果是单个根节点对象，
  // 所以最后把它包裹在一个数组里返回。如果根节点本身就是叶子节点，结果会是 [null]，需要处理一下。
  return result ? [result] : [];
}

// 数据库直连数据容器 (新)
const mindMapData = ref(null); // 用于存放从新接口获取的数据
const mindMapError = ref(null); // 新接口的错误信息
const isMindMapLoading = ref(true); // 新接口的加载状态

// 用户信息存储
const currentUserInfo = ref(null); // 存储搜索到的用户信息

// 全局数据缓存 - 避免重复请求
const cachedData = ref(null); // 缓存完整的数据

// 2. 获取路由参数
const route = useRoute();              // 获取当前路由信息对象
const queryAddress = route.params.query; // 从 URL 中拿到查询地址 (例如 /results/xxx 中的 xxx)

// 计算大纲数据 - 使用响应式计算属性
const outlineData = computed(() => {
  if (mindMapData.value) {
    return extractNonLeafNodes(mindMapData.value);
  }
  return [];
});

// 大纲树组件的配置
const defaultProps = {
  children: 'children',
  label: 'label'
};

// 右侧表格的数据和状态
const isLoading = ref(false);
const error = ref(null);
const selectedNodeData = ref(null); // 选中的节点数据
const selectedNodeType = ref(null); // 选中的节点类型
const detailTableData = ref([]); // 详细表格数据

// 分页相关状态
const currentPage = ref(1);
const pageSize = ref(20);
const totalItems = ref(0);

// 计算虚拟表格的宽度 - 适应右侧边栏
const virtualTableWidth = computed(() => {
  // 右侧边栏宽度420px，减去左右内边距(20px * 2)，减去边框等空间
  return 420 - 40 - 4; // 376px
});

// 计算当前页显示的数据
const paginatedData = computed(() => {
  if (selectedNodeType.value === 'users' || detailTableData.value.length <= 100) {
    // 用户信息或少量数据直接分页
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    totalItems.value = detailTableData.value.length;
    return detailTableData.value.slice(start, end);
  }
  // 大数据量使用el-table-v2，不需要分页
  return detailTableData.value;
});

// 分页改变处理
const handlePageChange = (page) => {
  currentPage.value = page;
};

const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
};

// 节点点击处理函数 - 优化版本，使用缓存
const handleNodeClick = async (node) => {
  console.log('点击了节点:', node);
  
  // 从节点对象中获取文本数据 - 更安全的数据访问
  let nodeText = '';
  try {
    if (node && node.nodeData && node.nodeData.data && node.nodeData.data.text) {
      nodeText = node.nodeData.data.text;
    } else if (node && node.data && node.data.text) {
      nodeText = node.data.text;
    } else if (typeof node === 'string') {
      nodeText = node;
    } else {
      console.log('无法获取节点文本，节点结构:', Object.keys(node || {}));
      return;
    }
  } catch (err) {
    console.error('解析节点文本时出错:', err);
    return;
  }
  
  console.log('节点文本:', nodeText);
  
  // 检查是否是数据类别节点
  let categoryType = null;
  if (nodeText.includes('用户信息') || nodeText.includes('基础信息')) {
    categoryType = 'users';
  } else if (nodeText.includes('交易记录') || nodeText.includes('交易') || nodeText.includes('交易统计')) {
    categoryType = 'transactions';
  } else if (nodeText.includes('资产变动') || nodeText.includes('资产')) {
    categoryType = 'asset_movements';
  } else if (nodeText.includes('登录日志') || nodeText.includes('登录')) {
    categoryType = 'login_logs';
  } else if (nodeText.includes('设备信息') || nodeText.includes('设备')) {
    categoryType = 'devices';
  } else if (nodeText.includes('源文件') || nodeText.includes('Excel')) {
    categoryType = 'source_files';
  }
  
  console.log('识别的类别:', categoryType);
  
  if (categoryType) {
    selectedNodeType.value = categoryType;
    selectedNodeData.value = node;
    error.value = null;
    
    // 重置分页状态
    currentPage.value = 1;
    pageSize.value = 20;
    
    // 🚀 优化：优先从缓存获取数据
    if (cachedData.value && cachedData.value[categoryType]) {
      console.log('🎯 从缓存加载数据，瞬间显示');
      detailTableData.value = cachedData.value[categoryType];
      isLoading.value = false;
      console.log(`${categoryType}数据已从缓存加载:`, cachedData.value[categoryType].length, '条记录');
      return;
    }
    
    // 如果缓存中没有数据，则从网络获取
    console.log('📡 缓存中无数据，从网络获取...');
    isLoading.value = true;
    
    try {
      // 检查是否有有效的用户信息
      if (!currentUserInfo.value || !currentUserInfo.value.user_id) {
        console.error('无有效用户信息进行详细数据查询');
        error.value = '无有效用户信息';
        return;
      }
      
      // 获取详细数据
      const response = await fetch(`http://127.0.0.1:5000/api/mindmap_data?user_id=${currentUserInfo.value.user_id}`);
      if (response.ok) {
        const result = await response.json();
        console.log('🔄 从网络获取到的详细数据:', result);
        if (result.status === 'success' && result.data) {
          // 🎯 关键优化：将完整数据存储到缓存
          cachedData.value = result.data;
          console.log('💾 数据已缓存，后续点击将瞬间显示');
          
          // 显示当前类别的数据
          if (result.data[categoryType]) {
            detailTableData.value = result.data[categoryType];
            console.log(`${categoryType}数据:`, result.data[categoryType]);
          } else {
            detailTableData.value = [];
          }
        } else {
          detailTableData.value = [];
        }
      } else {
        throw new Error('获取数据失败');
      }
    } catch (err) {
      console.error('获取详细数据失败:', err);
      error.value = '获取详细数据失败';
    } finally {
      isLoading.value = false;
    }
  } else {
    console.log('未识别的节点类型，不处理');
  }
};

// 文件下载处理函数
const handleFileDownload = async (filename) => {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/download/${encodeURIComponent(filename)}`);
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } else {
      console.error('文件下载失败');
    }
  } catch (err) {
    console.error('文件下载错误:', err);
  }
};

// 计算表格列配置
const tableColumns = computed(() => {
  if (!selectedNodeType.value) return [];
  
  switch (selectedNodeType.value) {
    case 'users':
      return [
        { prop: 'user_id', label: '用户ID', minWidth: 120 },
        { prop: 'name', label: '姓名', minWidth: 100 },
        { prop: 'phone_number', label: '手机号', minWidth: 140 },
        { prop: 'email', label: '邮箱', minWidth: 180 },
        { prop: 'source', label: '平台', minWidth: 80 }
      ];
    case 'transactions':
      return [
        { prop: 'transaction_id', label: '交易ID', minWidth: 140 },
        { prop: 'total_amount', label: '金额', minWidth: 100 },
        { prop: 'base_asset', label: '基础资产', minWidth: 80 },
        { prop: 'transaction_type', label: '类型', minWidth: 80 },
        { prop: 'transaction_time', label: '时间', minWidth: 160 }
      ];
    case 'asset_movements':
      return [
        { prop: 'direction', label: '方向', minWidth: 80 },
        { prop: 'asset', label: '资产类型', minWidth: 100 },
        { prop: 'quantity', label: '数量', minWidth: 120 },
        { prop: 'status', label: '状态', minWidth: 80 },
        { prop: 'transaction_time', label: '时间', minWidth: 160 }
      ];
    case 'login_logs':
      return [
        { prop: 'login_time', label: '登录时间', minWidth: 160 },
        { prop: 'login_ip', label: 'IP地址', minWidth: 130 },
        { prop: 'device_id', label: '设备ID', minWidth: 140 },
        { prop: 'source', label: '平台', minWidth: 80 }
      ];
    case 'devices':
      return [
        { prop: 'client_type', label: '客户端类型', minWidth: 120 },
        { prop: 'ip_address', label: 'IP地址', minWidth: 150 },
        { prop: 'add_time', label: '添加时间', minWidth: 180 },
        { prop: 'source', label: '平台', minWidth: 100 }
      ];
    case 'source_files':
      return [
        { prop: 'file_name', label: '文件名', minWidth: 180 },
        { prop: 'file_size', label: '文件大小', minWidth: 100 },
        { prop: 'upload_time', label: '上传时间', minWidth: 160 },
        { prop: 'platform', label: '平台', minWidth: 100 },
        { label: '操作', minWidth: 100, type: 'action' }
      ];
    default:
      return [];
  }
});

// 为el-table-v2格式化的列配置
const tableColumnsForV2 = computed(() => {
  return tableColumns.value.map(col => ({
    key: col.prop,
    title: col.label,
    dataKey: col.prop,
    width: col.width,
    cellRenderer: ({ cellData }) => cellData || '暂无'
  }));
});
onMounted(
  async function(){
    // 完整的数据获取流程：先搜索用户，再获取思维导图数据
    try {
      console.log('开始搜索用户:', queryAddress);
      
      // 第一步：搜索用户
      const searchResponse = await fetch(`http://127.0.0.1:5000/api/search_uid?query=${encodeURIComponent(queryAddress)}`);
      console.log('搜索响应状态:', searchResponse.status);
      
      if (!searchResponse.ok) {
        const errData = await searchResponse.json();
        console.log('搜索错误响应:', errData);
        throw new Error(errData.message || '用户搜索失败');
      }
      
      const searchResult = await searchResponse.json();
      console.log('搜索结果:', searchResult);
      
      if (searchResult.status !== 'success' || !searchResult.users || searchResult.users.length === 0) {
        console.log('搜索结果检查失败:', {
          status: searchResult.status,
          hasUsers: !!searchResult.users,
          usersLength: searchResult.users ? searchResult.users.length : 0
        });
        throw new Error('未找到匹配的用户');
      }
      
      // 获取第一个匹配的用户
      const foundUser = searchResult.users[0];
      currentUserInfo.value = foundUser;
      console.log('找到用户:', foundUser);
      
      // 第二步：使用找到的用户ID获取思维导图数据
      const mindMapResponse = await fetch(`http://127.0.0.1:5000/api/mindmap_data?user_id=${foundUser.user_id}`);
      if (!mindMapResponse.ok) {
        const errData = await mindMapResponse.json();
        throw new Error(errData.message || '数据获取失败');
      }
      
      const mindMapResult = await mindMapResponse.json();
      if (mindMapResult.status === 'success') {
        // 🎯 关键优化：立即缓存完整数据
        cachedData.value = mindMapResult.data;
        console.log('💾 初始数据已缓存，节点点击将瞬间响应');
        
        // 第三步：转换数据格式
        const transformedData = transformToMindMapData(mindMapResult.data, foundUser);
        mindMapData.value = transformedData;
        
        console.log('从API获取的真实数据:', mindMapResult.data);
        console.log('转换后的思维导图数据结构已准备就绪');
        console.log('数据节点信息:', {
          hasUsers: !!mindMapResult.data.users,
          hasTransactions: !!mindMapResult.data.transactions,
          hasAssetMovements: !!mindMapResult.data.asset_movements,
          usersCount: mindMapResult.data.users?.length || 0,
          transactionsCount: mindMapResult.data.transactions?.length || 0,
          assetMovementsCount: mindMapResult.data.asset_movements?.length || 0
        });
        
        isMindMapLoading.value = false;
        await nextTick();
        
        // 第四步：渲染思维导图
        const mindMapContainer = document.getElementById('mindMapContainer');
        console.log('容器元素:', mindMapContainer);
        console.log('容器尺寸:', mindMapContainer?.offsetWidth, 'x', mindMapContainer?.offsetHeight);
        
        if (mindMapContainer) {
          // 确保容器有最小尺寸
          mindMapContainer.style.minHeight = '500px';
          mindMapContainer.style.backgroundColor = '#f5f5f5';
          
          console.log('开始渲染真实数据...');
          const mindMap = new MindMap({
            el: mindMapContainer,
            data: transformedData, // 使用真实优化后的数据
            layout: 'mindMap', // 改为脑图布局，左右分布
            theme: 'default',
            readonly: false, // 允许交互
            enableFreeDrag: true, // 允许自由拖拽
            enableNodeDoubleClickEdit: false, // 禁用双击编辑
            // 性能优化配置
            enableNodeRichText: false, // 禁用富文本以提高性能
            enableAnimation: true, // 启用动画，脑图布局下动画效果更好
            // 初始展开配置
            initRootNodePosition: ['center', 'center'], // 根节点居中
            // 节点样式配置
            nodeTextMargin: [8, 4], // 文字边距
            nodeActiveStyle: {
              strokeColor: '#1890ff',
              strokeWidth: 2
            }
          });
          
          // 添加节点点击事件监听
          mindMap.on('node_click', (node, event) => {
            console.log('节点点击事件触发:', node, event);
            handleNodeClick(node);
          });
          
          // 等待渲染完成后设置初始展开状态
          setTimeout(() => {
            const root = mindMap.renderer.root;
            if (root) {
              // 确保根节点展开
              if (root.data && !root.data.isExpand) {
                root.expand();
              }
              
              // 展开第一层子节点，折叠第二层及以下
              if (root.children) {
                root.children.forEach(child => {
                  if (child && child.data && !child.data.isExpand) {
                    child.expand();
                  }
                  // 折叠所有孙子节点
                  if (child && child.children) {
                    child.children.forEach(grandChild => {
                      if (grandChild && grandChild.data && grandChild.data.isExpand) {
                        grandChild.unexpand();
                      }
                    });
                  }
                });
              }
              
              // 重新渲染以应用更改
              mindMap.render();
            }
          }, 500);
          
          console.log('MindMap实例:', mindMap);
        } else {
          console.error('找不到mindMapContainer元素');
        }
        
        console.log('思维导图渲染完成');
      } else {
        throw new Error(mindMapResult.message);
      }

    } catch (err) {
      console.error('数据获取失败:', err);
      isMindMapLoading.value = false;
      mindMapError.value = err.message;
    }
  }
);


</script>
<style scoped>
.main-content {
  display: flex;
  flex-direction: column;
  /* 如果外层 page-wrapper 已经控制了高度，可能不需要下面这行 */
  /* 但加上它可以确保在各种情况下，main-content 都占满整个视口高度 */
  height: 100vh; 
}
#mindMapContainer {
  flex-grow: 1; /* 告诉它，占据父容器里所有剩余的垂直空间 */
  width: 100%; /* 宽度占满 */
}

/* 右侧详情面板样式 */
.detail-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #666;
}

.detail-loading .el-icon {
  margin-right: 8px;
  font-size: 18px;
}

.detail-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #999;
  text-align: center;
}

.detail-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #d9d9d9;
}

.detail-placeholder p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.detail-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #ff4d4f;
  text-align: center;
}

.detail-error .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.detail-content {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.detail-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.data-count {
  font-size: 12px;
  color: #8c8c8c;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.table-container {
  flex: 1;
  padding: 16px 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 专门为虚拟表格调整的容器样式 */
.virtual-table-container {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  align-items: stretch; /* 确保虚拟表格占满容器宽度 */
  gap: 12px; /* 虚拟表格与信息提示之间的间距 */
  overflow: hidden; /* 防止内容溢出 */
}

.virtual-table-container .virtual-table-info {
  margin-bottom: 0; /* 重置间距，使用gap控制 */
}

.virtual-table-container .virtual-table-with-scrollbar {
  align-self: center; /* 表格本身居中 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* 添加轻微阴影 */
}

/* 为表格容器添加滚动条样式 */
.table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.table-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.table-container :deep(.el-table) {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  flex-shrink: 0;
}

.table-container :deep(.el-table th) {
  background-color: #fafafa;
  font-weight: 600;
}

.table-container :deep(.el-table--small .el-table__cell) {
  padding: 8px 4px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.virtual-table-info {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 4px;
  font-size: 12px;
  color: #0369a1;
  text-align: center;
}

/* 虚拟表格滚动条样式 */
.virtual-table-with-scrollbar {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto; /* 居中显示 */
}

/* 为虚拟表格添加更明显的滚动条 */
.virtual-table-with-scrollbar :deep(.el-table-v2__scrollbar) {
  display: block !important;
}

.virtual-table-with-scrollbar :deep(.el-table-v2__scrollbar-thumb) {
  background-color: #c1c1c1 !important;
  border-radius: 4px !important;
  min-height: 20px !important;
}

.virtual-table-with-scrollbar :deep(.el-table-v2__scrollbar-thumb:hover) {
  background-color: #a8a8a8 !important;
}

.virtual-table-with-scrollbar :deep(.el-table-v2__scrollbar-track) {
  background-color: #f1f1f1 !important;
  border-radius: 4px !important;
  width: 8px !important;
}

/* 确保表格内容区域有正确的滚动行为 */
.virtual-table-with-scrollbar :deep(.el-table-v2__body) {
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

/* 增强表格行的视觉效果 */
.virtual-table-with-scrollbar :deep(.el-table-v2__row) {
  border-bottom: 1px solid #f0f0f0;
}

.virtual-table-with-scrollbar :deep(.el-table-v2__row:hover) {
  background-color: #f5f7fa;
}

/* 通用滚动条样式（备用方案） */
.virtual-table-with-scrollbar :deep(*::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

.virtual-table-with-scrollbar :deep(*::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 4px;
}

.virtual-table-with-scrollbar :deep(*::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 4px;
}

.virtual-table-with-scrollbar :deep(*::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}

/* 确保容器允许滚动 */
.virtual-table-with-scrollbar :deep(.el-scrollbar__view) {
  overflow-y: auto !important;
}

/* 右侧边栏调整 */
.sidebar-right {
  width: 420px; /* 稍微增加宽度，给虚拟表格更多空间 */
  border-left: 1px solid #e8e8e8;
  background: #fff;
  display: flex;
  flex-direction: column;
  min-width: 420px; /* 防止压缩过小 */
}

.sidebar-right .sidebar-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 0; /* 移除默认内边距，由子容器控制 */
}

/* 用户信息卡片样式 */
.user-info-display {
  padding: 0;
}

.user-info-card {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 12px;
  background: #fafafa;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  margin-bottom: 0;
  border-bottom: none;
}

.info-label {
  min-width: 80px;
  font-weight: 600;
  color: #666;
  margin-right: 12px;
}

.info-value {
  flex: 1;
  color: #333;
  word-break: break-all;
}

/* 缓存状态提示样式 */
.cache-status {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #52c41a;
}

.cache-status .el-icon {
  font-size: 16px;
}
</style>