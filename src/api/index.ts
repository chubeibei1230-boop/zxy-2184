import request from './request'
import type {
  ApiResponse, LoginRequest, LoginResponse, User,
  Style, WaxBatch, Mold, Station, InspectionCycle,
  Batch, BatchDetail, ProcessRecord, InspectionRecord,
  WarningItem, DashboardSummary, BatchProgressItem,
  StationLoadItem, PendingInspectionItem
} from '@/types'

export const authApi = {
  login: (data: LoginRequest) =>
    request.post<any, ApiResponse<LoginResponse>>('/auth/login', data),
  getMe: () =>
    request.get<any, ApiResponse<User>>('/auth/me')
}

export const userApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: User[] }>>('/users'),
  create: (data: any) =>
    request.post<any, ApiResponse<User>>('/users', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<User>>(`/users/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/users/${id}`)
}

export const styleApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: Style[] }>>('/styles'),
  create: (data: any) =>
    request.post<any, ApiResponse<Style>>('/styles', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<Style>>(`/styles/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/styles/${id}`)
}

export const waxBatchApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: WaxBatch[] }>>('/wax-batches'),
  create: (data: any) =>
    request.post<any, ApiResponse<WaxBatch>>('/wax-batches', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<WaxBatch>>(`/wax-batches/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/wax-batches/${id}`)
}

export const moldApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: Mold[] }>>('/molds'),
  getAvailable: (params?: any) =>
    request.get<any, ApiResponse<{ items: Mold[] }>>('/molds/available', { params }),
  create: (data: any) =>
    request.post<any, ApiResponse<Mold>>('/molds', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<Mold>>(`/molds/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/molds/${id}`)
}

export const stationApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: Station[] }>>('/stations'),
  create: (data: any) =>
    request.post<any, ApiResponse<Station>>('/stations', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<Station>>(`/stations/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/stations/${id}`)
}

export const inspectionCycleApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: InspectionCycle[] }>>('/inspection-cycles'),
  create: (data: any) =>
    request.post<any, ApiResponse<InspectionCycle>>('/inspection-cycles', data),
  update: (id: number, data: any) =>
    request.put<any, ApiResponse<InspectionCycle>>(`/inspection-cycles/${id}`, data),
  delete: (id: number) =>
    request.delete<any, ApiResponse>(`/inspection-cycles/${id}`)
}

export const batchApi = {
  getList: (params?: any) =>
    request.get<any, ApiResponse<{ items: Batch[] }>>('/batches', { params }),
  getDetail: (id: number) =>
    request.get<any, ApiResponse<BatchDetail>>(`/batches/${id}`),
  create: (data: any) =>
    request.post<any, ApiResponse<Batch>>('/batches', data),
  updateStatus: (id: number, data: any) =>
    request.put<any, ApiResponse>(`/batches/${id}/status`, data),
  recordPour: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/pour`, data),
  recordDemold: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/demold`, data),
  recordTrim: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/trim`, data),
  recordBubble: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/bubble`, data),
  recordRework: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/rework`, data),
  recordInspect: (id: number, data: any) =>
    request.post<any, ApiResponse>(`/batches/${id}/inspect`, data)
}

export const dashboardApi = {
  getSummary: (params?: any) =>
    request.get<any, ApiResponse<DashboardSummary>>('/dashboard/summary', { params }),
  getBatchProgress: (params?: any) =>
    request.get<any, ApiResponse<{ items: BatchProgressItem[] }>>('/dashboard/batch-progress', { params }),
  getStationLoad: (params?: any) =>
    request.get<any, ApiResponse<{ items: StationLoadItem[] }>>('/dashboard/station-load', { params }),
  getPendingInspections: (params?: any) =>
    request.get<any, ApiResponse<{ items: PendingInspectionItem[] }>>('/dashboard/pending-inspections', { params })
}

export const warningApi = {
  getList: () =>
    request.get<any, ApiResponse<{ items: WarningItem[] }>>('/warnings'),
  getBubbleConcentration: () =>
    request.get<any, ApiResponse<{ items: WarningItem[] }>>('/warnings/bubble-concentration'),
  getOverdueInspection: () =>
    request.get<any, ApiResponse<{ items: WarningItem[] }>>('/warnings/overdue-inspection'),
  getReworkNoConclusion: () =>
    request.get<any, ApiResponse<{ items: WarningItem[] }>>('/warnings/rework-no-conclusion'),
  getPassRateDrop: () =>
    request.get<any, ApiResponse<{ items: WarningItem[] }>>('/warnings/pass-rate-drop')
}
