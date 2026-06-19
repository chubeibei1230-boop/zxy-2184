<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">质检周期管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增周期</el-button>
        <el-button :icon="RefreshRight" @click="loadList" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-form :inline="true" :model="filterForm" @submit.prevent>
          <el-form-item label="款式">
            <el-select v-model="filterForm.style_id" placeholder="全部款式" clearable @change="loadList">
              <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="周期天数">
            <el-input-number v-model="filterForm.cycle_days" :min="1" placeholder="周期天数" clearable @change="loadList" />
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
          <el-table-column label="款式" width="200">
            <template #default="{ row }">
              {{ getStyleName(row.style_id) }}
            </template>
          </el-table-column>
          <el-table-column label="周期天数" width="120">
            <template #default="{ row }">
              {{ row.cycle_days }} 天
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
      :title="isEdit ? '编辑质检周期' : '新增质检周期'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="款式" prop="style_id">
          <el-select v-model="form.style_id" placeholder="请选择款式" style="width: 100%;">
            <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期天数" prop="cycle_days">
          <el-input-number v-model="form.cycle_days" :min="1" style="width: 100%;" />
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
import { inspectionCycleApi, styleApi } from '@/api'
import { type InspectionCycle, type Style } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const list = ref<InspectionCycle[]>([])
const styles = ref<Style[]>([])

const filterForm = reactive({
  style_id: null as number | null,
  cycle_days: null as number | null
})

const form = reactive({
  id: 0,
  style_id: null as number | null,
  cycle_days: 7
})

const rules: FormRules = {
  style_id: [{ required: true, message: '请选择款式', trigger: 'change' }],
  cycle_days: [{ required: true, message: '请输入周期天数', trigger: 'blur' }]
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchStyle = !filterForm.style_id || item.style_id === filterForm.style_id
    const matchDays = !filterForm.cycle_days || item.cycle_days === filterForm.cycle_days
    return matchStyle && matchDays
  })
})

const getStyleName = (styleId: number) => {
  const style = styles.value.find(s => s.id === styleId)
  return style ? style.name : '-'
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
    const res = await inspectionCycleApi.getList()
    list.value = res.data.items || []
  } catch (e) {
    console.error('Load inspection cycles failed', e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.style_id = null
  filterForm.cycle_days = null
  loadList()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = 0
  form.style_id = null
  form.cycle_days = 7
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const handleEdit = (row: InspectionCycle) => {
  isEdit.value = true
  form.id = row.id
  form.style_id = row.style_id
  form.cycle_days = row.cycle_days
  dialogVisible.value = true
}

const handleDelete = (row: InspectionCycle) => {
  const styleName = getStyleName(row.style_id)
  ElMessageBox.confirm(`确定要删除款式"${styleName}"的质检周期吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await inspectionCycleApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (e) {
      console.error('Delete inspection cycle failed', e)
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
        await inspectionCycleApi.update(form.id, {
          style_id: form.style_id,
          cycle_days: form.cycle_days
        })
        ElMessage.success('编辑成功')
      } else {
        await inspectionCycleApi.create({
          style_id: form.style_id,
          cycle_days: form.cycle_days
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e) {
      console.error('Submit inspection cycle failed', e)
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
