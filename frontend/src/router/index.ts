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
      {
        path: 'reset-password',
        name: 'reset-password',
        component: () => import('@/pages/public/ResetPasswordPage.vue'),
      },
    ],
  },
  // Account routes (authenticated, no org context)
  {
    path: '/account',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: 'settings',
        name: 'account-settings',
        component: () => import('@/pages/account/SettingsPage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  // Organization selection/creation (authenticated, no org context)
  {
    path: '/organization',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: '',
        name: 'organization-select',
        component: () => import('@/pages/organization/SelectPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'create',
        name: 'organization-create',
        component: () => import('@/pages/organization/CreatePage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  // Organization app routes (authenticated, with org context and sidebar)
  {
    path: '/organization',
    component: () => import('@/layouts/OrganizationLayout.vue'),
    children: [
      {
        path: 'overview',
        name: 'organization-overview',
        component: () => import('@/pages/organization/OverviewPage.vue'),
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
