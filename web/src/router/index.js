import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppShell.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/plants',
      },
      {
        path: 'plants',
        name: 'Plants',
        component: () => import('@/views/PlantsView.vue'),
      },
      {
        path: 'plants/:id',
        name: 'PlantDetail',
        component: () => import('@/views/PlantDetailView.vue'),
        props: true,
      },
      {
        path: 'locations',
        name: 'Locations',
        component: () => import('@/views/LocationsView.vue'),
      },
      {
        path: 'locations/:id',
        name: 'LocationDetail',
        component: () => import('@/views/LocationDetailView.vue'),
        props: true,
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return { name: 'Plants' }
  }
})

export default router
