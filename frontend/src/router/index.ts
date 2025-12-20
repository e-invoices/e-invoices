import { createRouter, createWebHistory } from 'vue-router'
import OrganizationLayout from '@/layouts/OrganizationLayout.vue'

const routes = [
  // Auth routes (OrganizationLayout without sidebar and profile)
  {
    path: '/login',
    component: OrganizationLayout,
    props: { showSidebar: false, showProfile: false },
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('@/pages/auth/LoginPage.vue'),
        meta: { guestOnly: true },
      },
    ],
  },
  {
    path: '/register',
    component: OrganizationLayout,
    props: { showSidebar: false, showProfile: false },
    children: [
      {
        path: '',
        name: 'register',
        component: () => import('@/pages/auth/RegisterPage.vue'),
        meta: { guestOnly: true },
      },
    ],
  },
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
  // Organization selection/creation (OrganizationLayout without sidebar)
  {
    path: '/organization',
    component: OrganizationLayout,
    props: { showSidebar: false, showProfile: true },
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
      {
        path: 'join',
        name: 'organization-join',
        component: () => import('@/pages/organization/JoinPage.vue'),
        // No requiresAuth - the page handles auth state itself
      },
    ],
  },
  // Organization app routes (authenticated, with org context and sidebar)
  {
    path: '/organization',
    component: OrganizationLayout,
    children: [
      {
        path: 'overview',
        name: 'organization-overview',
        component: () => import('@/pages/organization/OverviewPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'settings',
        name: 'organization-settings',
        component: () => import('@/pages/organization/SettingsPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: 'team',
        name: 'organization-team',
        component: () => import('@/pages/organization/TeamPage.vue'),
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
    // Redirect to login page with redirect query param
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  } else if (to.meta.guestOnly && isAuthenticated) {
    // Redirect authenticated users away from guest-only pages (login/register)
    // But respect the redirect query param if present
    const redirectPath = to.query.redirect as string
    if (redirectPath) {
      next(redirectPath)
    } else {
      next({ name: 'organization-select' })
    }
  } else {
    next()
  }
})

export default router
