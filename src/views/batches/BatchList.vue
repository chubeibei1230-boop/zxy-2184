<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">批次管理</h2>
      <div class="header-actions">
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增批次</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="款式">
          <el-select v-model="filterForm.style_id" placeholder="全部款式" clearable @change="loadData">
            <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="loadData">
            <el-option v-for="(label, value) in STATUS_MAP" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-form-item label="复核状态">
          <el-select v-model="filterForm.review_status" placeholder="全部复核状态" clearable @change="loadData">
            <el-option v-for="(label, value) in REVIEW_STATUS_MAP" :key="value" :label="label" :value="value" />
          </el-select>
        </el-form-item>
        <el-form-item label="工艺员">
          <el-select v-model="filterForm.technician_id" placeholder="全部工艺员" clearable @change="loadData">
            <el-option v-for="user in technicians" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            @change="loadData"
          />
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="batches" style="width: 100%;" stripe v-loading="loading">
        <el-table-column prop="code" label="批次号" width="140" />
        <el-table-column prop="style_name" label="款式" width="120" />
        <el-table-column label="蜡料批次" width="120">
          <template #default="{ row }">
            {{ getWaxBatchCode(row.wax_batch_id) }}
          </template>
        </el-table-column>
        <el-table-column label="模具" width="120">
          <template #default="{ row }">
            {{ getMoldCode(row.mold_id) }}
          </template>
        </el-table-column>
        <el-table-column label="台位" width="120">
          <template #default="{ row }">
            {{ getStationName(row.station_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="technician_name" label="工艺员" width="100" />
        <el-table-column prop="inspector_name" label="质检员" width="100">
          <template #default="{ row }">
            {{ row.inspector_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <span
              class="status-tag"
              :style="{
                backgroundColor: STATUS_COLOR_MAP[row.status] + '20',
                color: STATUS_COLOR_MAP[row.status]
              }"
            >
              {{ STATUS_MAP[row.status] }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="review_status" label="复核状态" width="120">
          <template #default="{ row }">
            <span
              class="status-tag"
              :style="{
                backgroundColor: (row.review_status_color || REVIEW_STATUS_COLOR_MAP[row.review_status]) + '20',
                color: row.review_status_color || REVIEW_STATUS_COLOR_MAP[row.review_status]
              }"
            >
              {{ row.review_status_name || REVIEW_STATUS_MAP[row.review_status] }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="planned_start_date" label="计划开始" width="120" />
        <el-table-column prop="planned_end_date" label="计划结束" width="120" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="batches.length === 0 && !loading" description="暂无批次数据" />
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="新增批次"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="批次号" prop="code">
          <el-input v-model="createForm.code" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item label="款式" prop="style_id">
          <el-select v-model="createForm.style_id" placeholder="请选择款式" style="width: 100%;">
            <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="蜡料批次" prop="wax_batch_id">
          <el-select v-model="createForm.wax_batch_id" placeholder="请选择蜡料批次" style="width: 100%;">
            <el-option
              v-for="wb in waxBatches"
              :key="wb.id"
              :label="`${wb.code} - ${wb.material}`"
              :value="wb.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模具" prop="mold_id">
          <el-select v-model="createForm.mold_id" placeholder="请选择模具" style="width: 100%;">
            <el-option
              v-for="mold in molds"
              :key="mold.id"
              :label="`${mold.code} - ${mold.name}`"
              :value="mold.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="台位" prop="station_id">
          <el-select v-model="createForm.station_id" placeholder="请选择台位" style="width: 100%;">
            <el-option
              v-for="station in stations"
              :key="station.id"
              :label="`${station.code} - ${station.name}`"
              :value="station.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计划开始" prop="planned_start_date">
          <el-date-picker
            v-model="createForm.planned_start_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="计划结束" prop="planned_end_date">
          <el-date-picker
            v-model="createForm.planned_end_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="createForm.quantity" :min="1" :max="10000" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="createForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, RefreshRight } from '@element-plus/icons-vue'
import {
  batchApi, styleApi, waxBatchApi, moldApi, stationApi, userApi
} from '@/api'
import {
  STATUS_MAP, STATUS_COLOR_MAP,
  REVIEW_STATUS_MAP, REVIEW_STATUS_COLOR_MAP,
  type Batch, type Style, type WaxBatch, type Mold, type Station, type User
} from '@/types'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()

const batches = ref<Batch[]>([])
const styles = ref<Style[]>([])
const waxBatches = ref<WaxBatch[]>([])
const molds = ref<Mold[]>([])
const stations = ref<Station[]>([])
const technicians = ref<User[]>([])

const filterForm = reactive({
  style_id: null as number | null,
  status: null as string | null,
  review_status: null as string | null,
  technician_id: null as number | null,
  date_range: null as string[] | null
})

const createForm = reactive({
  code: '',
  style_id: null as number | null,
  wax_batch_id: null as number | null,
  mold_id: null as number | null,
  station_id: null as number | null,
  planned_start_date: '',
  planned_end_date: '',
  quantity: 1,
  remark: ''
})

const createRules: FormRules = {
  code: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  style_id: [{ required: true, message: '请选择款式', trigger: 'change' }],
  wax_batch_id: [{ required: true, message: '请选择蜡料批次', trigger: 'change' }],
  mold_id: [{ required: true, message: '请选择模具', trigger: 'change' }],
  station_id: [{ required: true, message: '请选择台位', trigger: 'change' }],
  planned_start_date: [{ required: true, message: '请选择计划开始日期', trigger: 'change' }],
  planned_end_date: [{ required: true, message: '请选择计划结束日期', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const getWaxBatchCode = (id: number) => {
  const wb = waxBatches.value.find(item => item.id === id)
  return wb?.code || '-'
}

const getMoldCode = (id: number) => {
  const mold = molds.value.find(item => item.id === id)
  return mold?.code || '-'
}

const getStationName = (id: number) => {
  const station = stations.value.find(item => item.id === id)
  return station?.name || '-'
}

const loadStyles = async () => {
  try {
    const res = await styleApi.getList()
    styles.value = res.data.items
  } catch (e) {
    console.error('Load styles failed', e)
  }
}

const loadWaxBatches = async () => {
  try {
    const res = await waxBatchApi.getList()
    waxBatches.value = res.data.items
  } catch (e) {
    console.error('Load wax batches failed', e)
  }
}

const loadMolds = async () => {
  try {
    const res = await moldApi.getList()
    molds.value = res.data.items
  } catch (e) {
    console.error('Load molds failed', e)
  }
}

const loadStations = async () => {
  try {
    const res = await stationApi.getList()
    stations.value = res.data.items
  } catch (e) {
    console.error('Load stations failed', e)
  }
}

const loadTechnicians = async () => {
  try {
    const res = await userApi.getList()
    technicians.value = res.data.items.filter((u: User) => u.role === 'technician')
  } catch (e) {
    console.error('Load technicians failed', e)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (filterForm.style_id) params.style_id = filterForm.style_id
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.review_status) params.review_status = filterForm.review_status
    if (filterForm.technician_id) params.technician_id = filterForm.technician_id
    if (filterForm.date_range?.length === 2) {
      params.start_date = filterForm.date_range[0]
      params.end_date = filterForm.date_range[1]
    }

    const res = await batchApi.getList(params)
    batches.value = res.data.items || []
  } catch (e) {
    console.error('Load batches failed', e)
    ElMessage.error('加载批次列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.style_id = null
  filterForm.status = null
  filterForm.review_status = null
  filterForm.technician_id = null
  filterForm.date_range = null
  loadData()
}

const openCreateDialog = () => {
  createForm.code = ''
  createForm.style_id = null
  createForm.wax_batch_id = null
  createForm.mold_id = null
  createForm.station_id = null
  createForm.planned_start_date = ''
  createForm.planned_end_date = ''
  createForm.quantity = 1
  createForm.remark = ''
  createFormRef.value?.resetFields()
  createDialogVisible.value = true
}

const handleCreate = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      const data = {
        ...createForm,
        technician_id: userStore.user?.id
      }
      await batchApi.create(data)
      ElMessage.success('批次创建成功')
      createDialogVisible.value = false
      loadData()
    } catch (e: any) {
      console.error('Create batch failed', e)
      ElMessage.error(e.response?.data?.message || '创建批次失败')
    } finally {
      submitting.value = false
    }
  })
}

const viewDetail = (id: number) => {
  router.push(`/batches/${id}`)
}

onMounted(() => {
  if (route.query.status) {
    filterForm.status = route.query.status as string
  }
  if (route.query.review_status) {
    filterForm.review_status = route.query.review_status as string
  }
  if (route.query.style_id) {
    filterForm.style_id = Number(route.query.style_id)
  }

  Promise.all([
    loadStyles(),
    loadWaxBatches(),
    loadMolds(),
    loadStations(),
    loadTechnicians()
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
