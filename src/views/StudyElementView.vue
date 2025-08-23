<template>
  <div class="common-layout">
    <el-container class="full-height-container">
      
      <el-aside width="20%" class="left-aside">左侧边栏</el-aside>
      
      <el-main>
              <!-- <div id="mindMapContainer" style="width: 100%; height: 100%;"></div> -->
              <div>
                <input type="text" v-model="inputname" placeholder="请输入你的名字" />
                

                <p>你输入的名字是: {{ username }}</p>
                <button @click="save">保存</button>
              </div>
      </el-main>
      <el-aside width="20%" class="right-aside">右侧边栏</el-aside>
    </el-container>

  </div>
</template>

<script setup>
// 3. 从 'vue' 导入 onMounted 和 onBeforeUnmount
import { onMounted, onBeforeUnmount } from 'vue';
import { ref } from 'vue';
import MindMap from "simple-mind-map";

// 声明一个变量来持有 mindMap 实例
let mindMap = null;
const username = ref('');
const inputname = ref('');
const save = () =>{
  username.value = inputname.value;
}
// 4. 将所有和 DOM 相关的操作放进 onMounted
// onMounted(() => {
//   mindMap = new MindMap({
//     // onMounted 执行时，可以保证 getElementById 能找到元素
//     el: document.getElementById('mindMapContainer'),
//     data: {
//       "data": {
//           "text": "中心主题"
//       },
//       "children": [
//         { "data": { "text": "分支1" } },
//         { "data": { "text": "分支2" } }
//       ]
//     }
//   });
// });

// (推荐) 在组件销毁时清理 mindMap 实例，防止内存泄漏
onBeforeUnmount(() => {
  if (mindMap) {
    mindMap.destroy();
  }
});
</script>

<style scoped>
/* 你的样式代码基本是正确的，现在 el-main 会应用你写的样式了 */
.common-layout {
  min-height: 100vh;
  display: flex;
  width: 100%;  
  height: 100%;   
}

.full-height-container {
  flex: 1;
}

.el-aside {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 现在这个样式会正确应用到 <el-main> 标签上 */
.el-main {
  background-color: #ffffff;
  /* 移除内边距，让思维导图完全填充 */
  padding: 0; 
  flex: 1;
  overflow: hidden; /* 防止思维导图内容溢出 */
}

#mindMapContainer * {
  margin: 0;
  padding: 0;
}
</style>