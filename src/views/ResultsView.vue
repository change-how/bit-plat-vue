
<template>
  <div class="page-wrapper">
    <aside class="sidebar-left">
      <div class="sidebar-header">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        <h2>大纲目录</h2>
      </div>
      <div class="sidebar-content">
        <div v-if="isMindMapLoading ">正在加载大纲...</div>
        <div v-else-if="mindMapError">加载失败: {{ outlineError }}</div>
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
        <h3>数据图谱: {{ queryAddress }}</h3>
      </div>
      <div v-if="isMindMapLoading" class="detail-panel-placeholder">正在加载图谱...</div>
      <div v-else-if="mindMapError" class="detail-panel-placeholder" style="color: #ff4d4f;">
        <p>查询失败: {{ error }}</p>
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

import { ref, onMounted, computed,nextTick } from 'vue';
import { useRoute } from 'vue-router';
import GraphDisplay from '../components/GraphDisplay.vue'; // 导入我们刚创建的图谱组件
import outlinetree from '../components/outlinetree.vue'
import ELtable from '../components/ELtable.vue'; // 导入我们刚创建的图谱组件
import MindMap from "simple-mind-map";
import data_test from '../../data/data_mindmap.json'; // 导入测试数据

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

// 2. 获取路由参数
const route = useRoute();              // 获取当前路由信息对象
const queryAddress = route.params.query; // 从 URL 中拿到查询地址 (例如 /results/xxx 中的 xxx)
const outlineData = extractNonLeafNodes(data_test);
onMounted(
  async function(){
    //try部分成功完成了从接口获取数据
    try {
      const mindMapResponse  = await fetch(`http://127.0.0.1:5000/api/mindmap_data?user_id=${encodeURIComponent(queryAddress)}`);
      //1、错误处理-是否成功得到响应
      if (!mindMapResponse.ok) {
        const errData = await mindMapResponse.json();
        throw new Error(errData.message || '服务器响应错误');
      }
      // const result = await response.json();

      const mindMapResult = await mindMapResponse.json();
      
      if (mindMapResult.status === 'success') {
        mindMapData.value = mindMapResult.data;
        isMindMapLoading.value = false;
        await nextTick();
        console.log('数据拿到了')
        mindMapData.value = data_test;//首先测试绘图功能，暂时依然是静态数据，之后删掉这一行即可
        const mindMap = new MindMap({
          layout: 'mindMap',
          el: document.getElementById('mindMapContainer'),
          "data": mindMapData.value
        });        
      } else {
        throw new Error(mindMapResult.message);
      }

    } catch (err) {//下面这两部分都是错误检查员
      console.error('加载数据失败:(123)', err);
      isMindMapLoading.value = false;
      error.value = err.message; // 捕获任何错误，并存入 error 变量
    } finally {
      // 无论成功还是失败，最终都要结束加载状态
      isMindMapLoading.value = false;
    }


// 3. 打印结果
console.log(JSON.stringify(outlineData, null, 2));



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

</style>