<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">款式管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增款式</el-button>
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
          <el-table-column prop="name" label="名称" width="180" />
          <el-table-column prop="description" label="描述" />
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
      :title="isEdit ? '编辑款式' : '新增款式'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="编号" prop="code">
          <el-input v-model="form.code" placeholder="请输入编号" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
import { styleApi } from '@/api'
import { type Style } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const list = ref<Style[]>([])

const filterForm = reactive({
  code: '',
  name: ''
})

const form = reactive({
  id: 0,
  code: '',
  name: '',
  description: ''
})

const rules: FormRules = {
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchCode = !filterForm.code || item.code.includes(filterForm.code)
    const matchName = !filterForm.name || item.name.includes(filterForm.name)
    return matchCode && matchName
  })
})

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
    const res = await styleApi.getList()
    list.value = res.data.items || []
  } catch (e) {
    console.error('Load styles failed', e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.code = ''
  filterForm.name = ''
  loadList()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = 0
  form.code = ''
  form.name = ''
  form.description = ''
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const handleEdit = (row: Style) => {
  isEdit.value = true
  form.id = row.id
  form.code = row.code
  form.name = row.name
  form.description = row.description
  dialogVisible.value = true
}

const handleDelete = (row: Style) => {
  ElMessageBox.confirm(`确定要删除款式"${row.name}"吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await styleApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (e) {
      console.error('Delete style failed', e)
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
        await styleApi.update(form.id, {
          code: form.code,
          name: form.name,
          description: form.description
        })
        ElMessage.success('编辑成功')
      } else {
        await styleApi.create({
          code: form.code,
          name: form.name,
          description: form.description
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e) {
      console.error('Submit style failed', e)
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
