import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/upload' },
  {
    path: '/upload',
    component: () => import('@/pages/UploadPage.vue'),
  },
  {
    path: '/preview',
    component: () => import('@/pages/PreviewPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
