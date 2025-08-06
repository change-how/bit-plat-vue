
<template>
  <div class="page-wrapper">
    <aside class="sidebar-left">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        <h2>大纲目录</h2>
      </div>
      <div class="sidebar-content">
        <div v-if="isOutlineLoading">正在加载大纲...</div>
        <div v-else-if="outlineError">加载失败: {{ outlineError }}</div>
        <outlinetree
          v-else
          :data="outlineData"      
          :props="defaultProps"
        />
      </div>
    </aside>

    <main class="main-content">
      <div class="main-content-header">
        <h3>数据图谱: {{ queryAddress }}</h3>
      </div>
      <div v-if="isLoading" class="detail-panel-placeholder">正在加载图谱...</div>
      <div v-else-if="error" class="detail-panel-placeholder" style="color: #ff4d4f;">
        <p>查询失败: {{ error }}</p>
      </div>
      <GraphDisplay v-else-if="graphData" :graphData="graphData" />
    </main>

    <aside class="sidebar-right">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
        <h2>节点详情</h2>
      </div>
      
      <div class="sidebar-content">
         <div v-if="isLoading">加载中...</div>
         <div v-else-if="error" class="detail-panel-placeholder">无详细信息</div>
         <div v-else>

          <el-table 
            :data="tableData"
            style="width: 100% height :100%"
            :row-class-name="tableRowClassName"
            max-height="500"
          >
            <el-table-column prop="date" label="日期" min-width="60" />
            <el-table-column prop="name" label="名字" min-width="60" />
            <el-table-column prop="address" label="地址" min-width="60"/>
            <el-table-column prop="tag" label="标签" min-width="60"/>
          </el-table>

         </div>
      </div>
    </aside>
  </div>
</template>



<script setup>

import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import GraphDisplay from '../components/GraphDisplay.vue'; // 导入我们刚创建的图谱组件
import outlinetree from '../components/outlinetree.vue'
import ELtable from '../components/ELtable.vue'; // 导入我们刚创建的图谱组件

//脑图数据容器
const graphData = ref(null); // 用于存放从后端成功获取的图谱数据
const error = ref(null);     // 用于存放射区失败时的错误信息
const isLoading = ref(true); // 用于控制是否显示“加载中”的状态

//大纲数据容器
const outlineData = ref([]); // 准备一个空数组，作为装大纲列表的盘子
const isOutlineLoading = ref(true); // 准备一个布尔值，作为“正在加载”的标志，默认为 true
const outlineError = ref(null);     // 准备一个空值，作为装错误信息的盘子

// 2. 获取路由参数
const route = useRoute();              // 获取当前路由信息对象
const queryAddress = route.params.query; // 从 URL 中拿到查询地址 (例如 /results/xxx 中的 xxx)

// 3. 数据获取逻辑
// onMounted 会在组件挂载到页面后自动执行，是执行初始化数据请求的最佳位置
onMounted(async () => {
//1. 调用知识图谱的api
    //try部分成功完成了从接口获取数据
  try {
    // 调用你原来 app.py 中定义的后端 API获取虚拟币数据
    const response = await fetch(`http://127.0.0.1:5000/api/search?query=${encodeURIComponent(queryAddress)}`);
    //检查是否成功返回
    if (!response.ok) {
      // 如果服务器返回非 2xx 状态码，也视为错误
      const errData = await response.json();
      throw new Error(errData.message || '服务器响应错误');
    }
    //检查内部内容是否成功
    const result = await response.json();
    if (result.status === 'success') {
      graphData.value = result.data; // 成功了！将获取到的数据存入响应式变量
    } else {
      throw new Error(result.message);
    }
  } catch (err) {//下面这两部分都是错误检查员
    console.error('加载数据失败:', err);
    error.value = err.message; // 捕获任何错误，并存入 error 变量
  } finally {
    // 无论成功还是失败，最终都要结束加载状态
    isLoading.value = false;
  }

  
//2. 调用获取大纲的api
  try {
      const outlineResponse = await fetch(`http://127.0.0.1:5000/api/outline?query=${encodeURIComponent(queryAddress)}`);
      if (!outlineResponse.ok) {
        // 如果不成功，就构造一个错误抛出，它会被下面的 catch 接住
        throw new Error('服务器响应错误');
      }
      // ✨ 新增：将返回的 JSON 字符串解析成 JS 对象
      const outlineResult = await outlineResponse.json();
      // ✨ 新增：检查业务状态是否成功
      if (outlineResult.status === 'success') {
        // ✨ 最关键的一步：把“菜”（数据）装入“盘子”（响应式变量）
        outlineData.value = outlineResult.data;
      } else {
        // 如果业务失败，也抛出一个错误
        throw new Error(outlineResult.message);
      }
    } catch (err) {
      // 如果请求失败（比如网络不通），把错误信息装入盘子
      outlineError.value = err.message;
    } finally {
      // 无论成功还是失败，加载过程都结束了，关掉“正在加载”的开关
      isOutlineLoading.value = false;
    }
});

// 4. 计算属性 (用于动态生成侧边栏内容)
// computed 会根据依赖的 ref 自动计算并缓存结果，非常高效
const directoryList = computed(() => {
  return (graphData.value && graphData.value.children) ? graphData.value.children : [];
});

const detailPanelData = computed(() => {
  if (graphData.value) {
    return (graphData.value.children && graphData.value.children.length > 0) ? graphData.value.children : [graphData.value];
  }
  return [];
});


const tableData = [
  {
    date: '2016-05-03',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: '金华',
    zip: 'CA 90036',
    tag: 'Home',
  },
  {
    date: '2016-05-02',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: '嘉兴南湖',
    zip: 'CA 90036',
    tag: 'Office',
  },
  {
    date: '2016-05-04',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: '上海浦东',
    zip: 'CA 90036',
    tag: 'Home',
  },
  {
    date: '2016-05-01',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: '嘉兴嘉善',
    zip: 'CA 90036',
    tag: 'Office',
  },
]


</script>
