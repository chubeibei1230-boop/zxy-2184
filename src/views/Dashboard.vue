<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">首页仪表盘</h2>
      <div class="header-actions">
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="批次号">
          <el-input
            v-model="filterForm.keyword"
            placeholder="请输入批次号"
            clearable
            @keyup.enter="loadData"
            style="width: 180px;"
          />
        </el-form-item>
        <el-form-item label="款式">
          <el-select v-model="filterForm.style_id" placeholder="全部款式" clearable @change="loadData" style="width: 140px;">
            <el-option v-for="style in styles" :key="style.id" :label="style.name" :value="style.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部状态" clearable @change="loadData" style="width: 120px;">
            <el-option label="待浇注" value="pending_pour" />
            <el-option label="成型中" value="molding" />
            <el-option label="待质检" value="pending_inspect" />
            <el-option label="返工中" value="reworking" />
            <el-option label="可交付" value="deliverable" />
            <el-option label="已交付" value="delivered" />
            <el-option label="暂停" value="paused" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任人">
          <el-select v-model="filterForm.technician_id" placeholder="全部工艺员" clearable @change="loadData" style="width: 120px;">
            <el-option v-for="user in technicians" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
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
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-row :gutter="20" class="stat-row">
      <el-col :span="4">
        <div class="stat-card">
          <div class="stat-content">
            <div>
              <div class="stat-value">{{ summary?.total_batches || 0 }}</div>
              <div class="stat-label">总批次</div>
            </div>
            <div class="stat-icon" style="background: #e0f2fe; color: #0284c7;">
              <el-icon><Tickets /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="filterByStatus('pending_pour')">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #f59e0b;">{{ summary?.pending_pour || 0 }}</div>
              <div class="stat-label">待浇注</div>
            </div>
            <div class="stat-icon" style="background: #fef3c7; color: #d97706;">
              <el-icon><Timer /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="filterByStatus('molding')">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #3b82f6;">{{ summary?.molding || 0 }}</div>
              <div class="stat-label">成型中</div>
            </div>
            <div class="stat-icon" style="background: #dbeafe; color: #2563eb;">
              <el-icon><Cpu /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="filterByStatus('pending_inspect')">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #8b5cf6;">{{ summary?.pending_inspect || 0 }}</div>
              <div class="stat-label">待质检</div>
            </div>
            <div class="stat-icon" style="background: #ede9fe; color: #7c3aed;">
              <el-icon><Search /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="filterByStatus('deliverable')">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #10b981;">{{ summary?.deliverable || 0 }}</div>
              <div class="stat-label">可交付</div>
            </div>
            <div class="stat-icon" style="background: #d1fae5; color: #059669;">
              <el-icon><CircleCheck /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="filterByStatus('delivered')">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #0ea5e9;">{{ summary?.delivered || 0 }}</div>
              <div class="stat-label">已交付</div>
            </div>
            <div class="stat-icon" style="background: #e0f2fe; color: #0284c7;">
              <el-icon><Files /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4" v-if="isInspector">
        <div class="stat-card" @click="goToDeliveryReviews">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #f59e0b;">{{ summary?.pending_delivery_review || 0 }}</div>
              <div class="stat-label">待交付复核</div>
            </div>
            <div class="stat-icon" style="background: #fef3c7; color: #d97706;">
              <el-icon><DocumentChecked /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="4">
        <div class="stat-card" @click="goToWarnings">
          <div class="stat-content">
            <div>
              <div class="stat-value" style="color: #ef4444;">{{ summary?.warning_count || 0 }}</div>
              <div class="stat-label">异常预警</div>
            </div>
            <div class="stat-icon" style="background: #fee2e2; color: #dc2626;">
              <el-icon><Warning /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="14">
        <div class="card">
          <div class="card-header">批次进度分布</div>
          <div ref="progressChartRef" class="chart-container" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="card">
          <div class="card-header">台位负载</div>
          <div ref="stationChartRef" class="chart-container" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <div class="card">
          <div class="card-header">
            <span>异常款式预警</span>
            <el-button type="primary" link @click="goToWarnings" style="float: right;">
              查看全部
            </el-button>
          </div>
          <div class="warning-list">
            <div
              v-for="(warning, idx) in warnings"
              :key="idx"
              class="warning-item"
              :class="`warning-${warning.level}`"
            >
              <div class="warning-header">
                <span class="warning-type">{{ WARNING_TYPE_MAP[warning.type] }}</span>
                <span class="warning-level" :style="{ color: WARNING_LEVEL_COLOR[warning.level] }">
                  {{ WARNING_LEVEL_MAP[warning.level] }}
                </span>
              </div>
              <div class="warning-title">{{ warning.title }}</div>
              <div class="warning-content">{{ warning.content }}</div>
              <div class="warning-time">{{ formatDate(warning.created_at) }}</div>
            </div>
            <el-empty v-if="warnings.length === 0" description="暂无异常预警" />
          </div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card">
          <div class="card-header">
            <span>待质检列表</span>
            <el-button type="primary" link @click="goToBatches('pending_inspect')" style="float: right;">
              查看全部
            </el-button>
          </div>
          <div class="table-container" style="box-shadow: none;">
            <el-table :data="pendingInspections" style="width: 100%;" stripe>
              <el-table-column prop="code" label="批次号" width="120" />
              <el-table-column prop="style_name" label="款式" />
              <el-table-column prop="technician_name" label="工艺员" width="100" />
              <el-table-column label="创建时间" width="160">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="超期" width="80">
                <template #default="{ row }">
                  <el-tag v-if="row.days_overdue > 0" type="danger" size="small">
                    {{ row.days_overdue }}天
                  </el-tag>
                  <span v-else style="color: #10b981;">正常</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button type="primary" link @click="viewBatch(row.id)">
                    质检
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="pendingInspections.length === 0" description="暂无待质检批次" />
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;" v-if="isInspector">
      <el-col :span="24">
        <div class="card">
          <div class="card-header">
            <span>待交付复核列表</span>
            <el-button type="primary" link @click="goToDeliveryReviews" style="float: right;">
              查看全部
            </el-button>
          </div>
          <div class="table-container" style="box-shadow: none;">
            <el-table :data="pendingDeliveryReviews" style="width: 100%;" stripe>
              <el-table-column prop="code" label="批次号" width="140" />
              <el-table-column prop="style_name" label="款式" width="160" />
              <el-table-column prop="technician_name" label="工艺员" width="100" />
              <el-table-column prop="inspector_name" label="质检员" width="100">
                <template #default="{ row }">
                  {{ row.inspector_name || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="批次数量" width="100" />
              <el-table-column label="质检完成时间" width="180">
                <template #default="{ row }">
                  {{ row.actual_end_date ? formatDate(row.actual_end_date) : '-' }}
                </template>
              </el-table-column>
              <el-table-column label="待复核天数" width="110">
                <template #default="{ row }">
                  <el-tag v-if="row.days_pending >= 3" type="danger" size="small">
                    {{ row.days_pending }}天
                  </el-tag>
                  <el-tag v-else-if="row.days_pending >= 1" type="warning" size="small">
                    {{ row.days_pending }}天
                  </el-tag>
                  <span v-else style="color: #10b981;">当天</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link @click="viewBatch(row.id)">
                    复核
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-empty v-if="pendingDeliveryReviews.length === 0" description="暂无待交付复核批次" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Tickets, Timer, Cpu, Search, CircleCheck, Warning,
  RefreshRight, DocumentChecked, Files
} from '@element-plus/icons-vue'
import { dashboardApi, warningApi, styleApi, userApi } from '@/api'
import {
  WARNING_TYPE_MAP, WARNING_LEVEL_MAP, WARNING_LEVEL_COLOR,
  type DashboardSummary, type WarningItem, type PendingInspectionItem,
  type BatchProgressItem, type StationLoadItem, type Style, type User,
  type PendingDeliveryReviewItem
} from '@/types'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const isInspector = computed(() => {
  return userStore.userRole === 'inspector' || userStore.userRole === 'admin'
})

const loading = ref(false)
const progressChartRef = ref<HTMLElement>()
const stationChartRef = ref<HTMLElement>()
let progressChart: echarts.ECharts | null = null
let stationChart: echarts.ECharts | null = null

const summary = ref<DashboardSummary | null>(null)
const warnings = ref<WarningItem[]>([])
const pendingInspections = ref<PendingInspectionItem[]>([])
const pendingDeliveryReviews = ref<PendingDeliveryReviewItem[]>([])
const batchProgress = ref<BatchProgressItem[]>([])
const stationLoad = ref<StationLoadItem[]>([])
const styles = ref<Style[]>([])
const technicians = ref<User[]>([])

const filterForm = reactive({
  keyword: '',
  style_id: null as number | null,
  status: null as string | null,
  technician_id: null as number | null,
  date_range: null as string[] | null
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

const loadStyles = async () => {
  try {
    const res = await styleApi.getList()
    styles.value = res.data.items
  } catch (e) {
    console.error('Load styles failed', e)
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

const getFilterParams = () => {
  const params: any = {}
  if (filterForm.keyword) params.keyword = filterForm.keyword
  if (filterForm.style_id) params.style_id = filterForm.style_id
  if (filterForm.status) params.status = filterForm.status
  if (filterForm.technician_id) params.technician_id = filterForm.technician_id
  if (filterForm.date_range?.length === 2) {
    params.start_date = filterForm.date_range[0]
    params.end_date = filterForm.date_range[1]
  }
  return params
}

const loadData = async () => {
  loading.value = true
  try {
    const params = getFilterParams()
    const progressParams = { ...params }
    delete progressParams.status

    const apiPromises: Promise<any>[] = [
      dashboardApi.getSummary(params),
      dashboardApi.getBatchProgress(progressParams),
      dashboardApi.getStationLoad(params),
      dashboardApi.getPendingInspections(params),
      warningApi.getList()
    ]
    if (isInspector.value) {
      apiPromises.splice(4, 0, dashboardApi.getPendingDeliveryReviews(params))
    }

    const results = await Promise.all(apiPromises)
    const summaryRes = results[0]
    const progressRes = results[1]
    const stationRes = results[2]
    const pendingRes = results[3]
    const reviewRes = isInspector.value ? results[4] : null
    const warningRes = isInspector.value ? results[5] : results[4]

    summary.value = summaryRes.data
    batchProgress.value = progressRes.data.items || []
    stationLoad.value = stationRes.data.items || []
    pendingInspections.value = pendingRes.data.items || []
    if (reviewRes) {
      pendingDeliveryReviews.value = reviewRes.data.items || []
    }
    warnings.value = (warningRes.data.items || []).slice(0, 5)

    await nextTick()
    renderProgressChart()
    renderStationChart()
  } catch (e) {
    console.error('Load dashboard data failed', e)
  } finally {
    loading.value = false
  }
}

const renderProgressChart = () => {
  if (!progressChartRef.value) return
  if (!progressChart) {
    progressChart = echarts.init(progressChartRef.value)
  }

  const xData = batchProgress.value.map(item => item.status_name)
  const yData = batchProgress.value.map(item => item.count)
  const colors = batchProgress.value.map(item => item.color)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLabel: {
        interval: 0,
        rotate: 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      name: '批次数量',
      type: 'bar',
      data: yData.map((value, index) => ({
        value,
        itemStyle: {
          color: colors[index] || '#1e3a5f',
          borderRadius: [6, 6, 0, 0]
        }
      })),
      barWidth: '50%',
      label: {
        show: true,
        position: 'top',
        fontWeight: 'bold'
      }
    }]
  }

  progressChart.setOption(option)
}

const renderStationChart = () => {
  if (!stationChartRef.value) return
  if (!stationChart) {
    stationChart = echarts.init(stationChartRef.value)
  }

  const data = stationLoad.value.map(item => ({
    name: `${item.code} ${item.name}`,
    value: item.rate,
    type: item.type_name
  }))

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { fontSize: 12 }
    },
    series: [{
      name: '台位负载',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 6,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      labelLine: {
        show: false
      },
      data: data.map((item, index) => ({
        ...item,
        itemStyle: {
          color: item.value > 70 ? '#ef4444' : item.value > 40 ? '#f59e0b' : '#10b981'
        }
      }))
    }]
  }

  stationChart.setOption(option)
}

const filterByStatus = (status: string) => {
  router.push({
    path: '/batches',
    query: { status }
  })
}

const goToBatches = (status?: string) => {
  const query: any = {}
  if (status) query.status = status
  router.push({ path: '/batches', query })
}

const goToDeliveryReviews = () => {
  router.push({
    path: '/batches',
    query: { review_status: 'pending_review' }
  })
}

const goToWarnings = () => {
  router.push('/warnings')
}

const viewBatch = (id: number) => {
  router.push(`/batches/${id}`)
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.style_id = null
  filterForm.status = null
  filterForm.technician_id = null
  filterForm.date_range = null
  loadData()
}

const handleResize = () => {
  progressChart?.resize()
  stationChart?.resize()
}

onMounted(() => {
  loadStyles()
  loadTechnicians()
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  progressChart?.dispose()
  stationChart?.dispose()
})
</script>

<style scoped>
.stat-row {
  cursor: default;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
}

.warning-list {
  max-height: 400px;
  overflow-y: auto;
}

.warning-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.warning-type {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}

.warning-level {
  font-size: 12px;
  font-weight: 600;
}

.warning-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.warning-content {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
  line-height: 1.5;
}

.warning-time {
  font-size: 12px;
  color: #94a3b8;
}
</style>
