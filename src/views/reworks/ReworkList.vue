<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">返工管理</h2>
      <div class="header-actions">
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
        <el-button
          v-if="canCreate"
          type="primary"
          :icon="Plus"
          @click="openCreateDialog"
        >
          发起返工
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="loadData">
            <el-option v-for="(label, value) in REWORK_STATUS_MAP" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任人">
          <el-select v-model="filterForm.responsible_id" placeholder="全部责任人" clearable @change="loadData">
            <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="filterForm.keyword" placeholder="请输入批次号" clearable @change="loadData" />
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="reworks" style="width: 100%;" stripe v-loading="loading">
        <el-table-column label="返工编号" width="100">
          <template #default="{ row }">
            第 {{ row.rework_no }} 次
          </template>
        </el-table-column>
        <el-table-column prop="batch_code" label="批次号" width="140" />
        <el-table-column prop="style_name" label="款式" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span
              class="status-tag"
              :style="{
                backgroundColor: (row.status_color || REWORK_STATUS_COLOR_MAP[row.status]) + '20',
                color: row.status_color || REWORK_STATUS_COLOR_MAP[row.status]
              }"
            >
              {{ row.status_name || REWORK_STATUS_MAP[row.status] }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="发起人" width="100">
          <template #default="{ row }">
            {{ row.initiator?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="责任人" width="100">
          <template #default="{ row }">
            {{ row.responsible?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="rework_reason" label="返工原因" min-width="180" show-overflow-tooltip />
        <el-table-column label="预计完成时间" width="180">
          <template #default="{ row }">
            {{ row.expected_finish_time ? formatDateTime(row.expected_finish_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="实际完成时间" width="180">
          <template #default="{ row }">
            {{ row.actual_finish_time ? formatDateTime(row.actual_finish_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewBatchDetail(row.batch_id)">批次详情</el-button>
            <el-button
              v-if="canStart(row)"
              type="success"
              link
              @click="handleStart(row)"
            >
              开始处理
            </el-button>
            <el-button
              v-if="canSubmit(row)"
              type="warning"
              link
              @click="openSubmitDialog(row)"
            >
              提交复检
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="reworks.length === 0 && !loading" description="暂无返工记录" />
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="发起返工"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="110px"
      >
        <el-form-item label="批次" prop="batch_id">
          <el-select v-model="createForm.batch_id" placeholder="请选择批次" style="width: 100%;" filterable>
            <el-option
              v-for="batch in reworkableBatches"
              :key="batch.id"
              :label="`${batch.code} - ${batch.style_name}`"
              :value="batch.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="返工原因" prop="rework_reason">
          <el-input
            v-model="createForm.rework_reason"
            type="textarea"
            :rows="3"
            placeholder="请输入返工原因"
          />
        </el-form-item>
        <el-form-item label="处理说明" prop="handling_instruction">
          <el-input
            v-model="createForm.handling_instruction"
            type="textarea"
            :rows="3"
            placeholder="请输入处理说明"
          />
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_id">
          <el-select v-model="createForm.responsible_id" placeholder="请选择责任人" style="width: 100%;">
            <el-option v-for="user in technicians" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="预计完成时间" prop="expected_finish_time">
          <el-date-picker
            v-model="createForm.expected_finish_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="submitDialogVisible"
      title="提交复检"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="submitFormRef"
        :model="submitForm"
        :rules="submitRules"
        label-width="110px"
      >
        <el-form-item label="实际完成时间" prop="actual_finish_time">
          <el-date-picker
            v-model="submitForm.actual_finish_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="返工结果" prop="rework_result">
          <el-input
            v-model="submitForm.rework_result"
            type="textarea"
            :rows="4"
            placeholder="请详细描述返工处理结果"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交复检</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import { reworkApi, batchApi, userApi } from '@/api'
import {
  REWORK_STATUS_MAP, REWORK_STATUS_COLOR_MAP,
  type ReworkRecord, type Batch, type User
} from '@/types'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const createDialogVisible = ref(false)
const submitDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const submitFormRef = ref<FormInstance>()

const reworks = ref<ReworkRecord[]>([])
const batches = ref<Batch[]>([])
const users = ref<User[]>([])
const technicians = ref<User[]>([])

const currentRework = ref<ReworkRecord | null>(null)

const canCreate = computed(() => {
  return userStore.userRole === 'technician' || userStore.userRole === 'admin'
})

const reworkableBatches = computed(() => {
  return batches.value.filter(b => b.status === 'reworking' || b.status === 'pending_inspect')
})

const filterForm = reactive({
  status: null as string | null,
  responsible_id: null as number | null,
  keyword: ''
})

const createForm = reactive({
  batch_id: null as number | null,
  rework_reason: '',
  handling_instruction: '',
  responsible_id: null as number | null,
  expected_finish_time: ''
})

const submitForm = reactive({
  actual_finish_time: '',
  rework_result: ''
})

const createRules: FormRules = {
  batch_id: [{ required: true, message: '请选择批次', trigger: 'change' }],
  rework_reason: [{ required: true, message: '请输入返工原因', trigger: 'blur' }],
  responsible_id: [{ required: true, message: '请选择责任人', trigger: 'change' }]
}

const submitRules: FormRules = {
  actual_finish_time: [{ required: true, message: '请选择实际完成时间', trigger: 'change' }],
  rework_result: [{ required: true, message: '请输入返工结果', trigger: 'blur' }]
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const canStart = (row: ReworkRecord) => {
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && row.status === 'pending'
}

const canSubmit = (row: ReworkRecord) => {
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && (row.status === 'processing' || row.status === 'pending')
}

const loadUsers = async () => {
  try {
    const res = await userApi.getList()
    users.value = res.data.items
    technicians.value = res.data.items.filter((u: User) => u.role === 'technician')
  } catch (e) {
    console.error('Load users failed', e)
  }
}

const loadBatches = async () => {
  try {
    const res = await batchApi.getList()
    batches.value = res.data.items || []
  } catch (e) {
    console.error('Load batches failed', e)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.responsible_id) params.responsible_id = filterForm.responsible_id
    if (filterForm.keyword) params.keyword = filterForm.keyword

    const res = await reworkApi.getList(params)
    reworks.value = res.data.items || []
  } catch (e) {
    console.error('Load reworks failed', e)
    ElMessage.error('加载返工列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.status = null
  filterForm.responsible_id = null
  filterForm.keyword = ''
  loadData()
}

const viewBatchDetail = (batchId: number) => {
  router.push(`/batches/${batchId}`)
}

const openCreateDialog = () => {
  createForm.batch_id = null
  createForm.rework_reason = ''
  createForm.handling_instruction = ''
  createForm.responsible_id = null
  createForm.expected_finish_time = ''
  createFormRef.value?.resetFields()
  createDialogVisible.value = true
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await reworkApi.create(createForm)
      ElMessage.success('返工记录创建成功')
      createDialogVisible.value = false
      loadData()
      loadBatches()
    } catch (e: any) {
      console.error('Create rework failed', e)
      ElMessage.error(e.response?.data?.message || '创建返工记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleStart = async (row: ReworkRecord) => {
  try {
    await ElMessageBox.confirm('确认开始处理该返工任务？', '确认', {
      type: 'warning'
    })
    await reworkApi.start(row.id)
    ElMessage.success('已开始处理返工')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Start rework failed', e)
      ElMessage.error(e.response?.data?.message || '开始返工失败')
    }
  }
}

const openSubmitDialog = (row: ReworkRecord) => {
  currentRework.value = row
  submitForm.actual_finish_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  submitForm.rework_result = ''
  submitFormRef.value?.resetFields()
  submitDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!submitFormRef.value || !currentRework.value) return

  await submitFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await reworkApi.submitInspection(currentRework.value.id, submitForm)
      ElMessage.success('返工完成，已提交复检')
      submitDialogVisible.value = false
      loadData()
      loadBatches()
    } catch (e: any) {
      console.error('Submit rework failed', e)
      ElMessage.error(e.response?.data?.message || '提交复检失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  Promise.all([
    loadUsers(),
    loadBatches()
  ]).then(() => {
    loadData()
  })
})
</script>

<style scoped>
.header-actions {
  display: flex;
  gap: 12px;
}
</style>
