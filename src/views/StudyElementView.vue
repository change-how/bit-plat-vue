<template>
  <div class="common-layout">
    <el-container class="full-height-container">
      <el-aside width=20% class="left-aside">左侧边栏</el-aside>
      <el-main class="drawing-board">
        <MyselfForm/>

      </el-main>
      <el-aside width=20% class="right-aside">右侧边栏</el-aside>
    </el-container>
  </div>
</template>



<script setup>
    import MyselfForm from '../components/MyselfForm.vue'
</script>

<style scoped>
/* 1. 使最外层容器（整个页面）布满视口 */
.common-layout {
  min-height: 100vh; /* 确保div至少和视口一样高 */
  display: flex;     /* 使其成为Flex容器，确保el-container能撑满 */
  width: 100%;  
  height: 100%;   
}

/* 2. 使 el-container 撑满其父容器（.common-layout） */
.full-height-container {
  flex: 1; /* 让 el-container 占据所有可用空间 */
           /* el-container 默认就是 display: flex; flex-direction: row; */
           /* 所以它的子元素 el-aside, el-main 会水平排列 */
}

/* 3. el-aside 和 el-main 的基本样式（可选，但推荐为了看清效果） */
.el-aside {
  background-color: #f0f2f5; /* 边栏背景色 */
  color: #333;
  padding: 20px;
  box-shadow: 2px 0 5px rgba(0,0,0,0.1), -2px 0 5px rgba(0,0,0,0.1); /* 添加阴影效果 */
  overflow-y: auto; /* 如果内容过多可以滚动 */
}

.el-main {
  background-color: #ffffff; /* 画板背景色，通常是白色 */
  color: #333;
  padding: 20px;
  flex: 1; /* ✨ 关键：让 el-main 占据所有剩余空间，实现“布满中间”的效果 */
  overflow: auto; /* 如果画板内容超出，可以滚动 */
  border-left: 1px solid #eee; /* 区分边栏与画板 */
  border-right: 1px solid #eee; /* 区分边栏与画板 */
}

/* 侧边栏内容对齐 */
.left-aside {
  text-align: left;
}
.right-aside {
  text-align: left; /* 或 right，根据需求 */
}

</style>