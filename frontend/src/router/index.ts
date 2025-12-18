import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: '',
        name: 'landing',
        component: () => import('@/pages/public/LandingPage.vue'),
      },
      {
        path: 'how-it-works',
        name: 'tutorial',
        component: () => import('@/pages/public/TutorialPage.vue'),
      },
      {
        path: 'benefits',
        name: 'about',
        component: () => import('@/pages/public/AboutPage.vue'),
      },
      {
        path: 'pricing',
        name: 'pricing',
        component: () => import('@/pages/public/PricingPage.vue'),
      },
      {
        path: 'api',
        name: 'api',
        component: () => import('@/pages/public/ApiPage.vue'),
      },
      {
        path: 'verify-email',
        name: 'verify-email',
        component: () => import('@/pages/public/VerifyEmailPage.vue'),
      },
    ],
  },
  // App routes (authenticated) - organization selection/creation uses PublicLayout
  {
    path: '/app',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: 'organizations',
        name: 'organization-select',
        component: () => import('@/pages/public/OrganizationSelectPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'organization/create',
        name: 'organization-create',
        component: () => import('@/pages/public/OrganizationCreatePage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  // App routes (authenticated) - main app with sidebar uses AppLayout
  {
    path: '/app',
    component: () => import('@/layouts/AppLayout.vue'),
    children: [
      {
        path: 'overview',
        name: 'overview',
        component: () => import('@/pages/app/OverviewPage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Navigation guard for protected routes
router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to landing page if trying to access protected route
    next({ name: 'landing' })
  } else {
    next()
  }
})

export default router
