<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增用户</el-button>
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="table-container">
      <el-table :data="users" style="width: 100%" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="name" label="姓名" width="150" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">
              {{ ROLE_MAP[row.role] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="users.length === 0" description="暂无用户数据" />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '新增用户'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="工艺员" value="technician" />
            <el-option label="质检员" value="inspector" />
          </el-select>
        </el-form-item>
        <el-form-item
          label="密码"
          prop="password"
          :required="!isEdit"
        >
          <el-input
            v-model="formData.password"
            type="password"
            :placeholder="isEdit ? '不修改请留空' : '请输入密码'"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
    >
      <div class="delete-confirm">
        <el-icon :size="24" color="#f59e0b"><Warning /></el-icon>
        <span>确定要删除用户「{{ deleteUser?.name }}」吗？此操作不可恢复。</span>
      </div>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete" :loading="deleting">确定删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, RefreshRight, Warning } from '@element-plus/icons-vue'
import { userApi } from '@/api'
import { ROLE_MAP, type User } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const deleting = ref(false)
const users = ref<User[]>([])
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const deleteUser = ref<User | null>(null)
const formRef = ref<FormInstance>()

const formData = reactive({
  username: '',
  name: '',
  role: 'inspector' as 'admin' | 'technician' | 'inspector',
  password: ''
})

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && !value) {
          callback(new Error('请输入密码'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getRoleTagType = (role: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    admin: 'danger',
    technician: 'primary',
    inspector: 'success'
  }
  return typeMap[role] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await userApi.getList()
    users.value = res.data.items || []
  } catch (e) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  formData.username = ''
  formData.name = ''
  formData.role = 'inspector'
  formData.password = ''
  dialogVisible.value = true
}

const handleEdit = (row: User) => {
  isEdit.value = true
  editId.value = row.id
  formData.username = row.username
  formData.name = row.name
  formData.role = row.role
  formData.password = ''
  dialogVisible.value = true
}

const handleDelete = (row: User) => {
  deleteUser.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  if (!deleteUser.value) return
  deleting.value = true
  try {
    await userApi.delete(deleteUser.value.id)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    deleting.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data: any = {
          username: formData.username,
          name: formData.name,
          role: formData.role
        }
        if (formData.password) {
          data.password = formData.password
        }
        if (isEdit.value && editId.value) {
          await userApi.update(editId.value, data)
          ElMessage.success('编辑成功')
        } else {
          await userApi.create(data)
          ElMessage.success('新增成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (e) {
        ElMessage.error(isEdit.value ? '编辑失败' : '新增失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.delete-confirm {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #374151;
}
</style>
