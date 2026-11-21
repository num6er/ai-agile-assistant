import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import Home from './views/Home.vue'
import ProjectDetail from './views/ProjectDetail.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/projects/:id', component: ProjectDetail, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).use(ElementPlus).mount('#app')
