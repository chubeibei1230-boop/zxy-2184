<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">模具管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增模具</el-button>
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
          <el-form-item label="款式">
            <el-select v-model="filterForm.style_id" placeholder="全部款式" clearable @change="loadList">
              <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
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
          <el-table-column label="款式" width="150">
            <template #default="{ row }">
              {{ getStyleName(row.style_id) }}
            </template>
          </el-table-column>
          <el-table-column prop="max_cavities" label="最大腔数" width="100" />
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
      :title="isEdit ? '编辑模具' : '新增模具'"
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
        <el-form-item label="款式" prop="style_id">
          <el-select v-model="form.style_id" placeholder="请选择款式" style="width: 100%;">
            <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大腔数" prop="max_cavities">
          <el-input-number v-model="form.max_cavities" :min="1" style="width: 100%;" />
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
import { moldApi, styleApi } from '@/api'
import { type Mold, type Style } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const list = ref<Mold[]>([])
const styles = ref<Style[]>([])

const statusOptions = [
  { value: 'available', label: '可用' },
  { value: 'in_use', label: '使用中' },
  { value: 'maintenance', label: '维护中' }
]

const STATUS_MAP: Record<string, string> = {
  available: '可用',
  in_use: '使用中',
  maintenance: '维护中'
}

const STATUS_TAG_TYPE: Record<string, string> = {
  available: 'success',
  in_use: 'primary',
  maintenance: 'warning'
}

const filterForm = reactive({
  code: '',
  name: '',
  style_id: null as number | null,
  status: ''
})

const form = reactive({
  id: 0,
  code: '',
  name: '',
  style_id: null as number | null,
  max_cavities: 1,
  status: 'available'
})

const rules: FormRules = {
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  style_id: [{ required: true, message: '请选择款式', trigger: 'change' }],
  max_cavities: [{ required: true, message: '请输入最大腔数', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchCode = !filterForm.code || item.code.includes(filterForm.code)
    const matchName = !filterForm.name || item.name.includes(filterForm.name)
    const matchStyle = !filterForm.style_id || item.style_id === filterForm.style_id
    const matchStatus = !filterForm.status || item.status === filterForm.status
    return matchCode && matchName && matchStyle && matchStatus
  })
})

const getStyleName = (styleId: number) => {
  const style = styles.value.find(s => s.id === styleId)
  return style ? style.name : '-'
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

const loadStyles = async () => {
  try {
    const res = await styleApi.getList()
    styles.value = res.data.items || []
  } catch (e) {
    console.error('Load styles failed', e)
  }
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await moldApi.getList()
    list.value = res.data.items || []
  } catch (e) {
    console.error('Load molds failed', e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.code = ''
  filterForm.name = ''
  filterForm.style_id = null
  filterForm.status = ''
  loadList()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = 0
  form.code = ''
  form.name = ''
  form.style_id = null
  form.max_cavities = 1
  form.status = 'available'
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const handleEdit = (row: Mold) => {
  isEdit.value = true
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.style_id = row.style_id
  form.max_cavities = row.max_cavities
  form.status = row.status
  dialogVisible.value = true
}

const handleDelete = (row: Mold) => {
  ElMessageBox.confirm(`确定要删除模具"${row.name}"吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await moldApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (e) {
      console.error('Delete mold failed', e)
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
        await moldApi.update(form.id, {
          code: form.code,
          name: form.name,
          style_id: form.style_id,
          max_cavities: form.max_cavities,
          status: form.status
        })
        ElMessage.success('编辑成功')
      } else {
        await moldApi.create({
          code: form.code,
          name: form.name,
          style_id: form.style_id,
          max_cavities: form.max_cavities,
          status: form.status
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e) {
      console.error('Submit mold failed', e)
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadStyles()
  loadList()
})
</script>

<style scoped>
</style>
