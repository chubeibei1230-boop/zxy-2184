<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-left">
        <div class="logo-section">
          <div class="logo-icon">
            <el-icon :size="48" color="#fff"><Cpu /></el-icon>
          </div>
          <h1 class="app-title">手作蜡模试制管理平台</h1>
          <p class="app-subtitle">Wax Mold Trial Production Management System</p>
        </div>
        <div class="features">
          <div class="feature-item">
            <el-icon :size="20"><Check /></el-icon>
            <span>智能排程与模具冲突检测</span>
          </div>
          <div class="feature-item">
            <el-icon :size="20"><Check /></el-icon>
            <span>全流程工艺记录追踪</span>
          </div>
          <div class="feature-item">
            <el-icon :size="20"><Check /></el-icon>
            <span>质检数据分析与预警</span>
          </div>
          <div class="feature-item">
            <el-icon :size="20"><Check /></el-icon>
            <span>多角色权限管理</span>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="login-form-wrapper">
          <h2 class="login-title">账号登录</h2>
          <p class="login-desc">请输入您的账号信息</p>
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                clearable
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                class="login-btn"
                :loading="loading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form-item>
          </el-form>
          <div class="test-accounts">
            <p class="test-title">测试账号：</p>
            <div class="account-list">
              <span class="account-item">管理员：admin / admin123</span>
              <span class="account-item">工艺员：tech1 / 123456</span>
              <span class="account-item">质检员：insp1 / 123456</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Cpu, Check } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } catch (e) {
        console.error('Login failed', e)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a8f 50%, #1e3a5f 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 1000px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(180deg, #1e3a5f 0%, #152a45 100%);
  padding: 60px 50px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.logo-section {
  margin-bottom: 40px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  color: white;
}

.app-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.login-right {
  flex: 1;
  padding: 60px 50px;
  display: flex;
  align-items: center;
}

.login-form-wrapper {
  width: 100%;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e3a5f;
  margin-bottom: 8px;
}

.login-desc {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 32px;
}

.login-form {
  margin-bottom: 32px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  letter-spacing: 4px;
}

.test-accounts {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}

.test-title {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.account-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.account-item {
  font-size: 12px;
  color: #94a3b8;
  font-family: 'Courier New', monospace;
}
</style>
