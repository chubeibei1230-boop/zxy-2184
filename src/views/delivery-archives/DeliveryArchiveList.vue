<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">交付归档管理</h2>
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
        <el-form-item label="接收方">
          <el-input
            v-model="filterForm.receiver"
            placeholder="请输入接收方"
            clearable
            @keyup.enter="loadData"
            style="width: 140px;"
          />
        </el-form-item>
        <el-form-item label="归档人">
          <el-select v-model="filterForm.archiver_id" placeholder="全部" clearable @change="loadData" style="width: 120px;">
            <el-option v-for="user in users" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="交付时间">
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

    <div class="card">
      <div class="table-container" style="box-shadow: none;">
        <el-table :data="archives" style="width: 100%;" stripe v-loading="loading">
          <el-table-column prop="batch_code" label="批次号" width="140" fixed="left" />
          <el-table-column prop="style_name" label="款式" width="140" />
          <el-table-column prop="wax_batch_code" label="蜡料批次" width="140" />
          <el-table-column prop="delivery_time" label="交付时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.delivery_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="delivered_quantity" label="交付数量" width="100">
            <template #default="{ row }">
              {{ row.delivered_quantity }} 件
            </template>
          </el-table-column>
          <el-table-column prop="receiver" label="接收方" width="140" />
          <el-table-column prop="archiver_name" label="归档人" width="100" />
          <el-table-column prop="quality_conclusion" label="质检结论" show-overflow-tooltip />
          <el-table-column prop="delivery_remark" label="交付备注" show-overflow-tooltip />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewBatch(row.batch_id)">
                查看批次
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="archives.length === 0 && !loading" description="暂无交付归档记录" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import { deliveryArchiveApi, styleApi, userApi } from '@/api'
import type { DeliveryArchiveItem, Style, User } from '@/types'

const router = useRouter()

const loading = ref(false)
const archives = ref<DeliveryArchiveItem[]>([])
const styles = ref<Style[]>([])
const users = ref<User[]>([])

const filterForm = reactive({
  keyword: '',
  style_id: null as number | null,
  receiver: '',
  archiver_id: null as number | null,
  date_range: null as string[] | null
})

const formatDateTime = (dateStr: string) => {
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

const loadUsers = async () => {
  try {
    const res = await userApi.getList()
    users.value = res.data.items
  } catch (e) {
    console.error('Load users failed', e)
  }
}

const getFilterParams = () => {
  const params: any = {}
  if (filterForm.keyword) params.keyword = filterForm.keyword
  if (filterForm.style_id) params.style_id = filterForm.style_id
  if (filterForm.receiver) params.receiver = filterForm.receiver
  if (filterForm.archiver_id) params.archiver_id = filterForm.archiver_id
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
    const res = await deliveryArchiveApi.getList(params)
    archives.value = res.data.items || []
  } catch (e) {
    ElMessage.error('加载交付归档列表失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.keyword = ''
  filterForm.style_id = null
  filterForm.receiver = ''
  filterForm.archiver_id = null
  filterForm.date_range = null
  loadData()
}

const viewBatch = (id: number) => {
  router.push(`/batches/${id}`)
}

onMounted(() => {
  loadStyles()
  loadUsers()
  loadData()
})
</script>

<style scoped>
</style>
