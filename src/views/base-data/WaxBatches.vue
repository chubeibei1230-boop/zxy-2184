<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">蜡料批次管理</h2>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">新增批次</el-button>
        <el-button :icon="RefreshRight" @click="loadList" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <div class="filter-bar">
        <el-form :inline="true" :model="filterForm" @submit.prevent>
          <el-form-item label="批次号">
            <el-input v-model="filterForm.code" placeholder="请输入批次号" clearable @keyup.enter="loadList" />
          </el-form-item>
          <el-form-item label="材质">
            <el-input v-model="filterForm.material" placeholder="请输入材质" clearable @keyup.enter="loadList" />
          </el-form-item>
          <el-form-item label="生产日期">
            <el-date-picker
              v-model="filterForm.production_date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
            />
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
          <el-table-column prop="code" label="批次号" width="150" />
          <el-table-column prop="material" label="材质" width="120" />
          <el-table-column label="生产日期" width="130">
            <template #default="{ row }">
              {{ row.production_date || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" />
          <el-table-column prop="remark" label="备注" />
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
      :title="isEdit ? '编辑蜡料批次' : '新增蜡料批次'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="批次号" prop="code">
          <el-input v-model="form.code" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item label="材质" prop="material">
          <el-input v-model="form.material" placeholder="请输入材质" />
        </el-form-item>
        <el-form-item label="生产日期" prop="production_date">
          <el-date-picker
            v-model="form.production_date"
            type="date"
            placeholder="选择生产日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { waxBatchApi } from '@/api'
import { type WaxBatch } from '@/types'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const list = ref<WaxBatch[]>([])

const filterForm = reactive({
  code: '',
  material: '',
  production_date: ''
})

const form = reactive({
  id: 0,
  code: '',
  material: '',
  production_date: '',
  quantity: 1,
  remark: ''
})

const rules: FormRules = {
  code: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  material: [{ required: true, message: '请输入材质', trigger: 'blur' }],
  production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const filteredList = computed(() => {
  return list.value.filter(item => {
    const matchCode = !filterForm.code || item.code.includes(filterForm.code)
    const matchMaterial = !filterForm.material || item.material.includes(filterForm.material)
    const matchDate = !filterForm.production_date || item.production_date === filterForm.production_date
    return matchCode && matchMaterial && matchDate
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
    const res = await waxBatchApi.getList()
    list.value = res.data.items || []
  } catch (e) {
    console.error('Load wax batches failed', e)
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.code = ''
  filterForm.material = ''
  filterForm.production_date = ''
  loadList()
}

const handleAdd = () => {
  isEdit.value = false
  form.id = 0
  form.code = ''
  form.material = ''
  form.production_date = ''
  form.quantity = 1
  form.remark = ''
  formRef.value?.resetFields()
  dialogVisible.value = true
}

const handleEdit = (row: WaxBatch) => {
  isEdit.value = true
  form.id = row.id
  form.code = row.code
  form.material = row.material
  form.production_date = row.production_date
  form.quantity = row.quantity
  form.remark = row.remark
  dialogVisible.value = true
}

const handleDelete = (row: WaxBatch) => {
  ElMessageBox.confirm(`确定要删除蜡料批次"${row.code}"吗？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消'
  }).then(async () => {
    try {
      await waxBatchApi.delete(row.id)
      ElMessage.success('删除成功')
      loadList()
    } catch (e) {
      console.error('Delete wax batch failed', e)
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
        await waxBatchApi.update(form.id, {
          code: form.code,
          material: form.material,
          production_date: form.production_date,
          quantity: form.quantity,
          remark: form.remark
        })
        ElMessage.success('编辑成功')
      } else {
        await waxBatchApi.create({
          code: form.code,
          material: form.material,
          production_date: form.production_date,
          quantity: form.quantity,
          remark: form.remark
        })
        ElMessage.success('新增成功')
      }
      dialogVisible.value = false
      loadList()
    } catch (e) {
      console.error('Submit wax batch failed', e)
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
