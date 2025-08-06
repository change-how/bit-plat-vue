<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import * as G6 from '@antv/g6';

// 1. 定义组件的“属性” (Props)
//    这就像是声明这个组件可以接收来自父组件的数据。
//    我们声明它需要一个名为 graphData 的对象。
const props = defineProps({
  graphData: {
    type: Object,
    required: true
  }
});

// 2. 准备工作
const container = ref(null); // 创建一个 ref 来引用模板中的 div 容器
let graph = null;            // 用一个变量来持有 G6 的实例，方便后续销毁

// 3. 核心渲染函数
const renderGraph = (data) => {
  // 如果已有图表实例，先销毁，防止内存泄漏
  if (graph) {
    graph.destroy();
  }
  
  // 确保容器和数据都已准备好
  if (!container.value || !data || !data.id) return;

  // 这是你原来 results.js 中的 G6 配置，我们直接拿来用
  graph = new G6.Graph({
    container: container.value, // 挂载点
    autoFit: 'view',
    behaviors: ['collapse-expand', 'drag-canvas', 'zoom-canvas', 'hover-activate'],
    data: G6.treeToGraphData(data), // 将树形数据转换为 G6 可用的图数据
    node: {
      style: {
        labelText: d => d.data.value ? `${d.data.title}: ${d.data.value}` : d.data.title,
        labelBackground: true,
        labelPlacement: 'right',
        fill: '#2a19e9ff',
        stroke: '#7c45daff',
        lineWidth: 2,
      },
      states: {
        active: {
          stroke: '#ff8800',
          lineWidth: 3,
          shadowColor: '#ff8800',
          shadowBlur: 10,
        },
      }
    },
    edge: {
      type: 'cubic-horizontal',
      style: { stroke: '#aaa' },
    },
    animation: {
      update: { duration: 300, easing: 'ease-in-out' }
    },
    layout: {
      type: 'mindmap',
      direction: 'H',
      getHeight: () => 16,
      getWidth: () => 16,
      getVGap: () => 10,
      getHGap: () => 100,
    },
  });
  
  graph.render(); // 渲染图表
};

// 4. Vue 生命周期钩子 与 监听器
// onMounted: 当组件成功挂载到页面上之后，执行回调
onMounted(() => {
  renderGraph(props.graphData);
});

// onUnmounted: 当组件被销毁（比如离开这个页面时），执行回调
onUnmounted(() => {
  if (graph) {
    graph.destroy(); // 销毁图表实例，释放内存
  }
});

// watch: 监听 props.graphData 的变化
// 如果父组件传入了新的数据，这个函数就会被触发，从而重新渲染图表
watch(() => props.graphData, (newData) => {
  if (newData) {
    renderGraph(newData);
  }
});

</script>

<template>
  <div ref="container" style="width: 100%; height: 100%;"></div>
</template>