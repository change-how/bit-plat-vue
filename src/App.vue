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
        <!-- <router-link to="/about">使用手册</router-link> -->
        <!-- <router-link to="/products">接口API</router-link> --> 
        <router-link to="/docs">📚 文档中心</router-link>
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
  import { AddLocation } from '@element-plus/icons-vue';
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
}

header {
  display: flex;
  background-color: rgba(174, 153, 253, 0.7);
  align-items: center;
  height: 60px;
  text-align: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.logo-title-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-text {
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

main {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}

footer {
  display: flex;
  background-color: rgba(174, 153, 253, 0.7);
  align-items: center;
  justify-content: center;
  text-align: center;
  opacity: 80%;
  height: 50px;
  flex-shrink: 0;
  margin-top: auto;
}

nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

nav a:hover {
  background-color: rgba(255, 255, 255, 0.3);
  color: #2c3e50;
}

nav a.router-link-active {
  background-color: rgba(255, 255, 255, 0.5);
  color: #2c3e50;
  font-weight: 600;
}
</style>