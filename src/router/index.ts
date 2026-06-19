import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false, title: '登录' }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页仪表盘', icon: 'DataLine' }
      },
      {
        path: 'base-data',
        meta: { title: '基础数据管理', icon: 'Setting', roles: ['admin'] },
        children: [
          {
            path: 'styles',
            name: 'Styles',
            component: () => import('@/views/base-data/Styles.vue'),
            meta: { title: '款式管理', roles: ['admin'] }
          },
          {
            path: 'wax-batches',
            name: 'WaxBatches',
            component: () => import('@/views/base-data/WaxBatches.vue'),
            meta: { title: '蜡料批次管理', roles: ['admin'] }
          },
          {
            path: 'molds',
            name: 'Molds',
            component: () => import('@/views/base-data/Molds.vue'),
            meta: { title: '模具管理', roles: ['admin'] }
          },
          {
            path: 'stations',
            name: 'Stations',
            component: () => import('@/views/base-data/Stations.vue'),
            meta: { title: '台位管理', roles: ['admin'] }
          },
          {
            path: 'inspection-cycles',
            name: 'InspectionCycles',
            component: () => import('@/views/base-data/InspectionCycles.vue'),
            meta: { title: '质检周期管理', roles: ['admin'] }
          }
        ]
      },
      {
        path: 'batches',
        name: 'Batches',
        component: () => import('@/views/batches/BatchList.vue'),
        meta: { title: '批次管理', icon: 'Tickets' }
      },
      {
        path: 'batches/:id',
        name: 'BatchDetail',
        component: () => import('@/views/batches/BatchDetail.vue'),
        meta: { title: '批次详情', hidden: true }
      },
      {
        path: 'warnings',
        name: 'Warnings',
        component: () => import('@/views/Warnings.vue'),
        meta: { title: '预警中心', icon: 'Warning' }
      },
      {
        path: 'reworks',
        name: 'Reworks',
        component: () => import('@/views/reworks/ReworkList.vue'),
        meta: { title: '返工管理', icon: 'RefreshLeft' }
      },
      {
        path: 'delivery-archives',
        name: 'DeliveryArchives',
        component: () => import('@/views/delivery-archives/DeliveryArchiveList.vue'),
        meta: { title: '交付归档管理', icon: 'Files' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  userStore.loadUserFromStorage()

  if (to.meta.title) {
    document.title = `${to.meta.title} - 手作蜡模试制管理平台`
  }

  if (to.path === '/login') {
    if (userStore.isLoggedIn) {
      next('/dashboard')
    } else {
      next()
    }
    return
  }

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    next('/login')
    return
  }

  if (to.meta.roles && userStore.user) {
    const hasRole = (to.meta.roles as string[]).includes(userStore.user.role)
    if (!hasRole) {
      ElMessage.error('无权限访问该页面')
      next('/dashboard')
      return
    }
  }

  next()
})

export default router
