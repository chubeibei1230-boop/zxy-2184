<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">预警中心</h2>
      <div class="header-actions">
        <el-button :icon="RefreshRight" @click="loadData" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm" @submit.prevent>
        <el-form-item label="预警类型">
          <el-select v-model="filterForm.type" placeholder="全部类型" clearable @change="filterData">
            <el-option label="气泡集中" value="bubble_concentration" />
            <el-option label="质检超期" value="overdue_inspection" />
            <el-option label="返工无结论" value="rework_no_conclusion" />
            <el-option label="通过率下降" value="pass_rate_drop" />
          </el-select>
        </el-form-item>
        <el-form-item label="预警级别">
          <el-select v-model="filterForm.level" placeholder="全部级别" clearable @change="filterData">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <div class="card-header">预警列表</div>
      <div class="warning-list">
        <div
          v-for="(warning, idx) in filteredWarnings"
          :key="idx"
          class="warning-item"
          :class="`warning-${warning.level}`"
        >
          <div class="warning-header">
            <div class="warning-tags">
              <el-tag size="small" :type="getTypeTagType(warning.type)" effect="light">
                {{ WARNING_TYPE_MAP[warning.type] }}
              </el-tag>
              <el-tag size="small" :style="{ backgroundColor: WARNING_LEVEL_COLOR[warning.level], color: '#fff', border: 'none' }">
                {{ WARNING_LEVEL_MAP[warning.level] }}
              </el-tag>
            </div>
            <span class="warning-time">{{ formatDate(warning.created_at) }}</span>
          </div>
          <div class="warning-title">{{ warning.title }}</div>
          <div class="warning-content">{{ warning.content }}</div>
          <div class="warning-footer">
            <el-button
              v-if="warning.related_id && warning.related_type === 'batch'"
              type="primary"
              link
              @click="goToBatch(warning.related_id)"
            >
              查看关联批次
            </el-button>
          </div>
        </div>
        <el-empty v-if="filteredWarnings.length === 0" description="暂无预警信息" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import { warningApi } from '@/api'
import {
  WARNING_TYPE_MAP,
  WARNING_LEVEL_MAP,
  WARNING_LEVEL_COLOR,
  type WarningItem
} from '@/types'

const router = useRouter()

const loading = ref(false)
const warnings = ref<WarningItem[]>([])

const filterForm = reactive({
  type: null as string | null,
  level: null as string | null
})

const filteredWarnings = computed(() => {
  let result = warnings.value
  if (filterForm.type) {
    result = result.filter(w => w.type === filterForm.type)
  }
  if (filterForm.level) {
    result = result.filter(w => w.level === filterForm.level)
  }
  return result
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

const getTypeTagType = (type: string) => {
  const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info' | 'primary'> = {
    bubble_concentration: 'danger',
    overdue_inspection: 'warning',
    rework_no_conclusion: 'danger',
    pass_rate_drop: 'warning'
  }
  return typeMap[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await warningApi.getList()
    warnings.value = res.data.items || []
  } catch (e) {
    ElMessage.error('加载预警列表失败')
  } finally {
    loading.value = false
  }
}

const filterData = () => {
}

const resetFilter = () => {
  filterForm.type = null
  filterForm.level = null
  loadData()
}

const goToBatch = (id: number) => {
  router.push(`/batches/${id}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.warning-list {
  max-height: calc(100vh - 320px);
  overflow-y: auto;
}

.warning-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.warning-tags {
  display: flex;
  gap: 8px;
}

.warning-time {
  font-size: 12px;
  color: #94a3b8;
}

.warning-title {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 6px;
}

.warning-content {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
  line-height: 1.6;
}

.warning-footer {
  display: flex;
  justify-content: flex-end;
}
</style>
