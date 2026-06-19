export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

export interface User {
  id: number
  username: string
  name: string
  role: 'admin' | 'technician' | 'inspector'
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Style {
  id: number
  code: string
  name: string
  description: string
  created_at: string
}

export interface WaxBatch {
  id: number
  code: string
  material: string
  production_date: string
  quantity: number
  remark: string
  created_at: string
}

export interface Mold {
  id: number
  code: string
  name: string
  style_id: number
  max_cavities: number
  status: 'available' | 'in_use' | 'maintenance'
  created_at: string
  style?: Style
}

export interface Station {
  id: number
  code: string
  name: string
  type: 'pour' | 'demold' | 'trim' | 'inspect'
  status: 'idle' | 'occupied' | 'disabled'
  created_at: string
}

export interface InspectionCycle {
  id: number
  style_id: number
  cycle_days: number
  created_at: string
  style?: Style
}

export type BatchStatus = 'pending_pour' | 'molding' | 'pending_inspect' | 'reworking' | 'deliverable' | 'delivered' | 'paused'
export type ReviewStatus = 'not_required' | 'pending_review' | 'reviewed'

export interface Batch {
  id: number
  code: string
  style_id: number
  wax_batch_id: number
  mold_id: number
  station_id: number
  technician_id: number
  inspector_id: number | null
  status: BatchStatus
  review_status: ReviewStatus
  planned_start_date: string
  planned_end_date: string
  actual_start_date: string | null
  actual_end_date: string | null
  quantity: number
  remark: string
  created_at: string
  style_name?: string
  technician_name?: string
  inspector_name?: string
  status_name?: string
  status_color?: string
  review_status_name?: string
  review_status_color?: string
}

export interface DeliveryReview {
  id: number
  batch_id: number
  reviewer_id: number
  review_time: string
  delivered_quantity: number
  final_quality_conclusion: string
  pass: boolean
  exception_remark: string | null
  created_at: string
  reviewer?: User
}

export interface DeliveryArchive {
  id: number
  batch_id: number
  archiver_id: number
  delivery_time: string
  delivered_quantity: number
  receiver: string
  delivery_remark: string | null
  quality_conclusion: string
  created_at: string
  archiver?: User
}

export interface DeliveryArchiveItem {
  id: number
  batch_id: number
  batch_code: string
  style_id: number
  style_name: string
  wax_batch_code: string
  delivery_time: string
  delivered_quantity: number
  receiver: string
  delivery_remark: string | null
  quality_conclusion: string
  archiver_id: number
  archiver_name: string
  technician_id: number
  technician_name: string
  status: BatchStatus
  status_name: string
  created_at: string
}

export interface BatchDetail extends Batch {
  style: Style
  wax_batch: WaxBatch
  mold: Mold
  station: Station
  technician: User
  inspector?: User
  process_records: ProcessRecord[]
  inspection_records: InspectionRecord[]
  delivery_review?: DeliveryReview | null
  delivery_archive?: DeliveryArchive | null
  rework_records: ReworkRecord[]
}

export interface ProcessRecord {
  id: number
  batch_id: number
  type: 'pour' | 'demold' | 'trim' | 'bubble' | 'rework'
  operator_id: number
  record_time: string
  temperature: number | null
  pressure: number | null
  hold_time: number | null
  cooling_time: number | null
  bubble_description: string | null
  bubble_count: number | null
  rework_reason: string | null
  rework_count: number | null
  remark: string | null
  created_at: string
  operator?: User
}

export interface InspectionRecord {
  id: number
  batch_id: number
  inspector_id: number
  inspect_time: string
  dimension_deviation: string
  surface_flatness: number
  pass: boolean
  opinion: string
  created_at: string
  inspector?: User
}

export interface WarningItem {
  type: 'bubble_concentration' | 'overdue_inspection' | 'rework_no_conclusion' | 'pass_rate_drop' | 'unreviewed_delivery'
  level: 'low' | 'medium' | 'high'
  title: string
  content: string
  related_id: number | null
  related_type: string | null
  created_at: string
}

export interface DashboardSummary {
  total_batches: number
  pending_pour: number
  molding: number
  pending_inspect: number
  reworking: number
  deliverable: number
  delivered: number
  paused: number
  pending_delivery_review: number
  warning_count: number
  pending_rework: number
  overdue_rework: number
  waiting_rework_inspection: number
}

export interface PendingDeliveryReviewItem {
  id: number
  code: string
  style_name: string
  technician_name: string
  inspector_name: string | null
  quantity: number
  actual_end_date: string | null
  days_pending: number
}

export interface BatchProgressItem {
  status: string
  status_name: string
  count: number
  color: string
}

export interface StationLoadItem {
  id: number
  code: string
  name: string
  type: string
  type_name: string
  occupied: number
  total: number
  rate: number
}

export interface PendingInspectionItem {
  id: number
  code: string
  style_name: string
  technician_name: string
  created_at: string
  days_overdue: number
}

export const STATUS_MAP: Record<BatchStatus, string> = {
  pending_pour: '待浇注',
  molding: '成型中',
  pending_inspect: '待质检',
  reworking: '返工中',
  deliverable: '可交付',
  delivered: '已交付',
  paused: '暂停'
}

export const STATUS_COLOR_MAP: Record<BatchStatus, string> = {
  pending_pour: '#f59e0b',
  molding: '#3b82f6',
  pending_inspect: '#8b5cf6',
  reworking: '#ef4444',
  deliverable: '#10b981',
  delivered: '#0ea5e9',
  paused: '#6b7280'
}

export const ROLE_MAP: Record<string, string> = {
  admin: '管理员',
  technician: '工艺员',
  inspector: '质检员'
}

export const STATION_TYPE_MAP: Record<string, string> = {
  pour: '浇注台',
  demold: '脱模台',
  trim: '修边台',
  inspect: '质检台'
}

export const REVIEW_STATUS_MAP: Record<ReviewStatus, string> = {
  not_required: '无需复核',
  pending_review: '待交付复核',
  reviewed: '已复核'
}

export const REVIEW_STATUS_COLOR_MAP: Record<ReviewStatus, string> = {
  not_required: '#6b7280',
  pending_review: '#f59e0b',
  reviewed: '#10b981'
}

export type ReworkStatus = 'pending' | 'processing' | 'waiting_inspection' | 'completed' | 'cancelled'

export interface ReworkRecord {
  id: number
  batch_id: number
  rework_no: number
  initiator_id: number
  responsible_id: number
  status: ReworkStatus
  rework_reason: string
  handling_instruction: string | null
  expected_finish_time: string | null
  actual_finish_time: string | null
  rework_result: string | null
  created_at: string
  updated_at: string
  initiator?: User
  responsible?: User
  batch_code?: string
  style_name?: string
  status_name?: string
  status_color?: string
}

export interface ReworkStats {
  pending_rework: number
  overdue_rework: number
  waiting_inspection: number
  total_rework: number
}

export const REWORK_STATUS_MAP: Record<ReworkStatus, string> = {
  pending: '待处理',
  processing: '处理中',
  waiting_inspection: '待复检',
  completed: '已完成',
  cancelled: '已取消'
}

export const REWORK_STATUS_COLOR_MAP: Record<ReworkStatus, string> = {
  pending: '#f59e0b',
  processing: '#3b82f6',
  waiting_inspection: '#8b5cf6',
  completed: '#10b981',
  cancelled: '#6b7280'
}

export const WARNING_TYPE_MAP: Record<string, string> = {
  bubble_concentration: '气泡集中',
  overdue_inspection: '质检超期',
  rework_no_conclusion: '返工无结论',
  pass_rate_drop: '通过率下降',
  unreviewed_delivery: '待复核超期',
  rework_overdue: '返工超期',
  multiple_reworks: '多次返工'
}

export const WARNING_LEVEL_MAP: Record<string, string> = {
  high: '高',
  medium: '中',
  low: '低'
}

export const WARNING_LEVEL_COLOR: Record<string, string> = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#10b981'
}
