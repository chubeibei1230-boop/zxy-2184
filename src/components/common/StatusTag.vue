<template>
  <el-tag :style="{ backgroundColor: bgColor, color: '#fff', border: 'none' }" size="small">
    {{ statusText }}
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { STATUS_MAP, STATUS_COLOR_MAP, type BatchStatus } from '@/types'

interface Props {
  status: BatchStatus
}

const props = defineProps<Props>()

const statusText = computed(() => STATUS_MAP[props.status] || props.status)
const bgColor = computed(() => STATUS_COLOR_MAP[props.status] || '#6b7280')
</script>

<style scoped>
</style>
