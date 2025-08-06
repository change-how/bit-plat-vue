<template>
  <div id="app-wrapper">
    <header v-if="!currentRoute.meta.hideHeaderFooter">
      <div class="logo-title-container">
        <el-icon :size="28" color="#333">
          <el-icon><add-location/></el-icon>
        </el-icon>
        <span class="title-text">虚拟币查询平台</span>
      </div>
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/about">使用手册</router-link>
        <router-link to="/products">接口API</router-link>
        <router-link to="/studypage">学习文档</router-link>
      </nav>
    </header>

    <main>
      <router-view></router-view>
    </main>

    <footer v-if="!currentRoute.meta.hideHeaderFooter">
      <p>&copy; 2025 虚拟币数据小平台</p>
    </footer>
  </div>
</template>

<script setup>
  // ✨✨✨ 导入 useRouter 和 useRoute 钩子 ✨✨✨
  import { useRoute } from 'vue-router';
  const currentRoute = useRoute();


</script>

<style scoped>
/* App.vue 的全局布局样式 */
#app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  height:100%;
}
header {
  display: flex;
  background-color: rgba(174, 153, 253, 0.7);
  align-items: center;
  height:10%;
  text-align: center;
  justify-content:space-between;;
  /* opacity:90%; */
  padding: 0 24px;
}
.logo-title-container {
  display: flex; /* 使用 flex 布局 */
  align-items: center; /* 垂直居中对齐图标和文字 */
  gap: 12px; /* 在图标和文字之间创建一个优雅的间距 */
}

/* 标题文字的样式 */
.title-text {
  font-size: 20px;
  font-weight: 600; /* 字体加粗 */
  color: #333; /* 标题颜色 */
}
footer {
  display: flex;
  background-color: rgba(174, 153, 253, 0.7);
  align-items: center;
  justify-content:center;
  text-align: center;
  opacity:80%;
  height:10%;
}
main {
  width:100%;
  height: 100%;

  display: flex;
  justify-content: center;
  align-items: center;   
}
nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #333;

}
</style>