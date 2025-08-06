import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView 
    },
    {
      // 路径规则，:query 是一个动态参数，可以匹配 /results/后面的任意字符串
      path: '/results/:query',
      name: 'results', 
      component: () => import('../views/ResultsView.vue')
    },
    {
      path: '/studypage',
      name: 'studypage', 
      component: () => import('../views/StudyElementView.vue'),
      meta: { hideHeaderFooter: true } 
    }
  ]
})

export default router