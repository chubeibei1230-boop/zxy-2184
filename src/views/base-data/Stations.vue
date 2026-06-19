<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">台位管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增台位</el-button>
        <el-button :icon="RefreshRight" @click="loadList" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-form :inline="true" :model="filterForm" @submit.prevent>
          <el-form-item label="编号">
            <el-input v-model="filterForm.code" placeholder="请输入编号" clearable @keyup.enter="loadList" />
          </el-form-item>
          <el-form-item label="名称">
            <el-input v-model="filterForm.name" placeholder="请输入名称" clearable @keyup.enter="loadList" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="filterForm.type" placeholder="全部类型" clearable @change="loadList">
              <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="loadList">
              <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadList">查询</el-button>
            <el-button @click="resetFilter">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="table-container">
        <el-table :data="filteredList" style="width: 100%;" stripe v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="code" label="编号" width="150" />
          <el-table-column prop="name" label="名称" width="150" />
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-tag type="info">
                {{ getTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="filteredList.length === 0 && !loading" description="暂无数据" />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑台位' : '新增台位'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="编号" prop="code">
          <el-input v-model="form.code" placeholder="请输入编号" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%;">
            <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import { stationApi } from '@/api'
import { type Station, STATION_TYPE_MAP } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const list = ref<Station[]>([])

const typeOptions = [
  { value: 'pour', label: '浇注台' },
  { value: 'demold', label: '脱模台' },
  { value: 'trim', label: '修边台' },
  { value: 'inspect', label: '质检台' }
]

const statusOptions = [
  { value: 'idle', label: '空闲' },
  { value: 'occupied', label: '占用' },
  { value: 'disabled', label: '禁用' }
]

const STATUS_MAP: Record<string, string> = {
  idle: '空闲',
  occupied: '占用',
  disabled: '禁用'
}

const STATUS_TAG_TYPE: Record<string, string> = {
  idle: 'success',
  occupied: 'warning',
  disabled: 'danger'
}

const filterForm = reactive({
  code: '',
  name: '',
  type: '',
  status: ''
})

const form = reactive({
  id: 0,
  code: '',
  name: '',
  type: 'pour' as Station['type'],
  status: 'idle' as Station['status']
})

const rules: FormRules = {
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchCode = !filterForm.code || item.code.includes(filterForm.code)
    const matchName = !filterForm.name || item.name.includes(filterForm.name)
    const matchType = !filterForm.type || item.type === filterForm.type
    const matchStatus = !filterForm.status || item.status === filterForm.status
    return matchCode && matchName && matchType && matchStatus
  })
})

const getTypeLabel = (type: string) => {
  return STATION_TYPE_MAP[type] || type
}

const getStatusLabel = (status: string) => {
  return STATUS_MAP[status] || status
}

const getStatusTagType = (status: string) => {
  return STATUS_TAG_TYPE[status] || 'info'
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

const loadList = async () => {
  loading.value = true
  try {
    const res = await stationApi.getList()
    list.value = res.data.items || []
  } catch (e) {
    console.error('Load stations failed', e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.code = ''
  filterForm.name = ''
  filterForm.type = ''
  filterForm.status = ''
  loadList()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = 0
  form.code = ''
  form.name = ''
  form.type = 'pour'
  form.status = 'idle'
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const handleEdit = (row: Station) => {
  isEdit.value = true
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.type = row.type
  form.status = row.status
  dialogVisible.value = true
}

const handleDelete = (row: Station) => {
  ElMessageBox.confirm(`确定要删除台位"${row.name}"吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await stationApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (e) {
      console.error('Delete station failed', e)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isEdit.value) {
        await stationApi.update(form.id, {
          code: form.code,
          name: form.name,
          type: form.type,
          status: form.status
        })
        ElMessage.success('编辑成功')
      } else {
        await stationApi.create({
          code: form.code,
          name: form.name,
          type: form.type,
          status: form.status
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e) {
      console.error('Submit station failed', e)
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
</style>
