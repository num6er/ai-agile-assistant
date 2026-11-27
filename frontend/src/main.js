import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
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

// 注入 Element Plus 中文语言包,消除组件内置英文文案(如 "No Data"/"Total"/"OK" 等)
createApp(App).use(router).use(ElementPlus, { locale: zhCn }).mount('#app')
