<template>
  <el-container class="main-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo-area">
        <div class="logo">
          <el-icon :size="28" color="#fff"><Cpu /></el-icon>
          <span v-show="!isCollapse" class="logo-text">蜡模管理系统</span>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        class="sidebar-menu"
        background-color="#1e3a5f"
        text-color="#cbd5e1"
        active-text-color="#f59e0b"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <template #title>首页仪表盘</template>
        </el-menu-item>

        <el-sub-menu index="/base-data" v-if="userStore.userRole === 'admin'">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>基础数据管理</span>
          </template>
          <el-menu-item index="/base-data/styles">款式管理</el-menu-item>
          <el-menu-item index="/base-data/wax-batches">蜡料批次管理</el-menu-item>
          <el-menu-item index="/base-data/molds">模具管理</el-menu-item>
          <el-menu-item index="/base-data/stations">台位管理</el-menu-item>
          <el-menu-item index="/base-data/inspection-cycles">质检周期管理</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/batches">
          <el-icon><Tickets /></el-icon>
          <template #title>批次管理</template>
        </el-menu-item>

        <el-menu-item index="/warnings">
          <el-icon><Warning /></el-icon>
          <template #title>预警中心</template>
          <el-badge v-if="warningCount > 0" :value="warningCount" class="warning-badge" />
        </el-menu-item>

        <el-menu-item index="/users" v-if="userStore.userRole === 'admin'">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleSidebar" :size="20">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="刷新数据" placement="bottom">
            <el-icon class="header-icon" @click="refreshData" :size="18">
              <RefreshRight />
            </el-icon>
          </el-tooltip>
          <el-tooltip content="预警信息" placement="bottom">
            <el-badge :value="warningCount" class="header-badge">
              <el-icon class="header-icon" @click="goToWarnings" :size="18">
                <Bell />
              </el-icon>
            </el-badge>
          </el-tooltip>
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <div class="user-text">
                <span class="user-name">{{ userStore.userName }}</span>
                <span class="user-role">{{ roleName }}</span>
              </div>
              <el-icon><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Cpu, DataLine, Setting, Tickets, Warning, User,
  Expand, Fold, RefreshRight, Bell, UserFilled,
  CaretBottom, SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ROLE_MAP } from '@/types'
import { warningApi } from '@/api'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const warningCount = ref(0)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/base-data/')) {
    return '/base-data'
  }
  if (path.startsWith('/batches/')) {
    return '/batches'
  }
  return path
})

const roleName = computed(() => ROLE_MAP[userStore.userRole] || '')

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title as string
  }))
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const refreshData = () => {
  window.location.reload()
}

const goToWarnings = () => {
  router.push('/warnings')
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
    }).catch(() => {})
  } else if (command === 'profile') {
    router.push('/users')
  }
}

const loadWarnings = async () => {
  try {
    const res = await warningApi.getList()
    warningCount.value = res.data.items?.length || 0
  } catch (e) {
    console.error('Load warnings failed', e)
  }
}

onMounted(() => {
  loadWarnings()
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.sidebar {
  background: #1e3a5f;
  transition: width 0.3s;
  overflow: hidden;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  height: calc(100vh - 60px);
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.05);
}

.header {
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  cursor: pointer;
  color: #64748b;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #1e3a5f;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  cursor: pointer;
  color: #64748b;
  transition: color 0.2s;
}

.header-icon:hover {
  color: #1e3a5f;
}

.header-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-info:hover {
  background: #f1f5f9;
}

.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.user-role {
  font-size: 11px;
  color: #94a3b8;
}

.main-content {
  padding: 0;
  overflow-y: auto;
  background: #f3f4f6;
}

.warning-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
