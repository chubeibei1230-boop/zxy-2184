<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="goBack" circle style="margin-right: 12px;" />
        <h2 class="page-title">批次详情 - {{ batchDetail?.code }}</h2>
      </div>
      <div class="header-actions">
        <el-button :icon="RefreshRight" @click="loadDetail" :loading="loading">刷新</el-button>
      </div>
    </div>

    <div v-loading="loading" class="detail-content">
      <div class="card batch-info-card">
        <div class="card-header">批次基本信息</div>
        <div class="info-grid" v-if="batchDetail">
          <div class="info-item">
            <span class="label">批次号：</span>
            <span class="value">{{ batchDetail.code }}</span>
          </div>
          <div class="info-item">
            <span class="label">款式：</span>
            <span class="value">{{ batchDetail.style?.name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">蜡料批次：</span>
            <span class="value">{{ batchDetail.wax_batch?.code || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">模具：</span>
            <span class="value">{{ batchDetail.mold?.code || '-' }} {{ batchDetail.mold?.name || '' }}</span>
          </div>
          <div class="info-item">
            <span class="label">台位：</span>
            <span class="value">{{ batchDetail.station?.code || '-' }} {{ batchDetail.station?.name || '' }}</span>
          </div>
          <div class="info-item">
            <span class="label">工艺员：</span>
            <span class="value">{{ batchDetail.technician?.name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">质检员：</span>
            <span class="value">{{ batchDetail.inspector?.name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">状态：</span>
            <span
              class="status-tag"
              :style="{
                backgroundColor: STATUS_COLOR_MAP[batchDetail.status] + '20',
                color: STATUS_COLOR_MAP[batchDetail.status]
              }"
            >
              {{ STATUS_MAP[batchDetail.status] }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">复核状态：</span>
            <span
              v-if="batchDetail.review_status"
              class="status-tag"
              :style="{
                backgroundColor: (batchDetail.review_status_color || REVIEW_STATUS_COLOR_MAP[batchDetail.review_status]) + '20',
                color: batchDetail.review_status_color || REVIEW_STATUS_COLOR_MAP[batchDetail.review_status]
              }"
            >
              {{ batchDetail.review_status_name || REVIEW_STATUS_MAP[batchDetail.review_status] }}
            </span>
            <span v-else class="value">-</span>
          </div>
          <div class="info-item">
            <span class="label">计划开始：</span>
            <span class="value">{{ batchDetail.planned_start_date }}</span>
          </div>
          <div class="info-item">
            <span class="label">计划结束：</span>
            <span class="value">{{ batchDetail.planned_end_date }}</span>
          </div>
          <div class="info-item">
            <span class="label">实际开始：</span>
            <span class="value">{{ batchDetail.actual_start_date ? formatDateTime(batchDetail.actual_start_date) : '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">实际结束：</span>
            <span class="value">{{ batchDetail.actual_end_date ? formatDateTime(batchDetail.actual_end_date) : '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">数量：</span>
            <span class="value">{{ batchDetail.quantity }}</span>
          </div>
          <div class="info-item full-width">
            <span class="label">备注：</span>
            <span class="value">{{ batchDetail.remark || '-' }}</span>
          </div>
        </div>
      </div>

      <div class="action-bar" v-if="batchDetail">
        <el-button
          v-if="canPour"
          type="primary"
          :icon="Watermelon"
          @click="openPourDialog"
        >
          浇注
        </el-button>
        <el-button
          v-if="canDemold"
          type="primary"
          :icon="Box"
          @click="openDemoldDialog"
        >
          脱模
        </el-button>
        <el-button
          v-if="canTrim"
          type="primary"
          :icon="Crop"
          @click="openTrimDialog"
        >
          修边
        </el-button>
        <el-button
          v-if="canRecordBubble"
          type="warning"
          :icon="Warning"
          @click="openBubbleDialog"
        >
          气泡记录
        </el-button>
        <el-button
          v-if="canRework"
          type="warning"
          :icon="RefreshLeft"
          @click="openReworkDialog"
        >
          返工完成
        </el-button>
        <el-button
          v-if="canInspect"
          type="success"
          :icon="CircleCheck"
          @click="openInspectDialog"
        >
          质检
        </el-button>
        <el-button
          v-if="canDeliveryReview"
          type="warning"
          :icon="DocumentChecked"
          @click="openDeliveryReviewDialog"
        >
          交付复核
        </el-button>
        <el-button
          v-if="canDeliveryArchive"
          type="success"
          :icon="Files"
          @click="openDeliveryArchiveDialog"
        >
          交付归档
        </el-button>
      </div>

      <div class="card timeline-card">
        <div class="card-header">工艺记录时间线</div>
        <el-timeline v-if="batchDetail?.process_records?.length">
          <el-timeline-item
            v-for="(record, index) in sortedProcessRecords"
            :key="record.id"
            :timestamp="formatDateTime(record.record_time)"
            :type="getTimelineType(record.type)"
            :color="getTimelineColor(record.type)"
          >
            <div class="timeline-content">
              <div class="timeline-title">
                <span class="record-type">{{ getRecordTypeName(record.type) }}</span>
                <span class="operator">操作人：{{ record.operator?.name || '-' }}</span>
              </div>
              <div class="timeline-details">
                <div v-if="record.temperature !== null">温度：{{ record.temperature }}℃</div>
                <div v-if="record.pressure !== null">压力：{{ record.pressure }} MPa</div>
                <div v-if="record.hold_time !== null">保压时间：{{ record.hold_time }}s</div>
                <div v-if="record.cooling_time !== null">冷却时间：{{ record.cooling_time }}s</div>
                <div v-if="record.bubble_description">气泡描述：{{ record.bubble_description }}</div>
                <div v-if="record.bubble_count !== null">气泡数量：{{ record.bubble_count }} 个</div>
                <div v-if="record.rework_reason">返工原因：{{ record.rework_reason }}</div>
                <div v-if="record.rework_count !== null">返工数量：{{ record.rework_count }} 件</div>
                <div v-if="record.remark">备注：{{ record.remark }}</div>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无工艺记录" />
      </div>

      <div class="card inspection-card">
        <div class="card-header">质检记录</div>
        <div class="table-container" style="box-shadow: none;">
          <el-table
            :data="batchDetail?.inspection_records || []"
            style="width: 100%;"
            stripe
          >
            <el-table-column prop="inspect_time" label="质检时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.inspect_time) }}
              </template>
            </el-table-column>
            <el-table-column label="质检员" width="100">
              <template #default="{ row }">
                {{ row.inspector?.name || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="dimension_deviation" label="尺寸偏差" />
            <el-table-column prop="surface_flatness" label="表面平面度" width="120">
              <template #default="{ row }">
                {{ row.surface_flatness }} mm
              </template>
            </el-table-column>
            <el-table-column prop="pass" label="结果" width="80">
              <template #default="{ row }">
                <el-tag v-if="row.pass" type="success" size="small">通过</el-tag>
                <el-tag v-else type="danger" size="small">不通过</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="opinion" label="质检意见" />
          </el-table>
          <el-empty v-if="!batchDetail?.inspection_records?.length" description="暂无质检记录" />
        </div>
      </div>

      <div class="card delivery-review-card" v-if="batchDetail">
        <div class="card-header">
          <span>交付复核信息</span>
        </div>
        <div v-if="batchDetail.delivery_review" class="review-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">复核时间：</span>
              <span class="value">{{ formatDateTime(batchDetail.delivery_review.review_time) }}</span>
            </div>
            <div class="info-item">
              <span class="label">复核人：</span>
              <span class="value">{{ batchDetail.delivery_review.reviewer?.name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">交付数量：</span>
              <span class="value">{{ batchDetail.delivery_review.delivered_quantity }} / {{ batchDetail.quantity }} 件</span>
            </div>
            <div class="info-item">
              <span class="label">复核结论：</span>
              <span>
                <el-tag v-if="batchDetail.delivery_review.pass" type="success" size="small">通过</el-tag>
                <el-tag v-else type="danger" size="small">不通过</el-tag>
              </span>
            </div>
            <div class="info-item full-width">
              <span class="label">最终质量结论：</span>
              <span class="value">{{ batchDetail.delivery_review.final_quality_conclusion || '-' }}</span>
            </div>
            <div class="info-item full-width" v-if="batchDetail.delivery_review.exception_remark">
              <span class="label">异常备注：</span>
              <span class="value">{{ batchDetail.delivery_review.exception_remark }}</span>
            </div>
          </div>
        </div>
        <div v-else-if="batchDetail.review_status === 'pending_review'" class="review-empty">
          <el-empty description="待交付复核，请点击上方【交付复核】按钮进行操作" />
        </div>
        <div v-else class="review-empty">
          <el-empty description="暂无交付复核信息" />
        </div>
      </div>

      <div class="card delivery-archive-card" v-if="batchDetail">
        <div class="card-header">
          <span>交付归档信息</span>
        </div>
        <div v-if="batchDetail.delivery_archive" class="archive-info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">交付时间：</span>
              <span class="value">{{ formatDateTime(batchDetail.delivery_archive.delivery_time) }}</span>
            </div>
            <div class="info-item">
              <span class="label">归档人：</span>
              <span class="value">{{ batchDetail.delivery_archive.archiver?.name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">交付数量：</span>
              <span class="value">{{ batchDetail.delivery_archive.delivered_quantity }} / {{ batchDetail.quantity }} 件</span>
            </div>
            <div class="info-item">
              <span class="label">接收方：</span>
              <span class="value">{{ batchDetail.delivery_archive.receiver }}</span>
            </div>
            <div class="info-item full-width">
              <span class="label">关联质检结论：</span>
              <span class="value">{{ batchDetail.delivery_archive.quality_conclusion || '-' }}</span>
            </div>
            <div class="info-item full-width" v-if="batchDetail.delivery_archive.delivery_remark">
              <span class="label">交付备注：</span>
              <span class="value">{{ batchDetail.delivery_archive.delivery_remark }}</span>
            </div>
          </div>
        </div>
        <div v-else-if="canDeliveryArchive" class="archive-empty">
          <el-empty description="待交付归档，请点击上方【交付归档】按钮进行操作" />
        </div>
        <div v-else class="archive-empty">
          <el-empty description="暂无交付归档信息" />
        </div>
      </div>
    </div>

    <el-dialog
      v-model="pourDialogVisible"
      title="记录浇注"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="pourFormRef"
        :model="pourForm"
        :rules="pourRules"
        label-width="100px"
      >
        <el-form-item label="浇注时间" prop="record_time">
          <el-date-picker
            v-model="pourForm.record_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="温度" prop="temperature">
          <el-input-number v-model="pourForm.temperature" :min="0" :max="500" :precision="1" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：℃</span>
        </el-form-item>
        <el-form-item label="压力" prop="pressure">
          <el-input-number v-model="pourForm.pressure" :min="0" :max="100" :precision="2" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：MPa</span>
        </el-form-item>
        <el-form-item label="保压时间" prop="hold_time">
          <el-input-number v-model="pourForm.hold_time" :min="0" :max="10000" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：秒</span>
        </el-form-item>
        <el-form-item label="冷却时间" prop="cooling_time">
          <el-input-number v-model="pourForm.cooling_time" :min="0" :max="10000" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：秒</span>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="pourForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pourDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePour" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="demoldDialogVisible"
      title="记录脱模"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="demoldFormRef"
        :model="demoldForm"
        :rules="demoldRules"
        label-width="100px"
      >
        <el-form-item label="脱模时间" prop="record_time">
          <el-date-picker
            v-model="demoldForm.record_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="冷却时间" prop="cooling_time">
          <el-input-number v-model="demoldForm.cooling_time" :min="0" :max="10000" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：秒</span>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="demoldForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="demoldDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDemold" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="trimDialogVisible"
      title="记录修边"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="trimFormRef"
        :model="trimForm"
        :rules="trimRules"
        label-width="100px"
      >
        <el-form-item label="修边时间" prop="record_time">
          <el-date-picker
            v-model="trimForm.record_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="trimForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="trimDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleTrim" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="bubbleDialogVisible"
      title="记录气泡"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="bubbleFormRef"
        :model="bubbleForm"
        :rules="bubbleRules"
        label-width="100px"
      >
        <el-form-item label="记录时间" prop="record_time">
          <el-date-picker
            v-model="bubbleForm.record_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="气泡描述" prop="bubble_description">
          <el-input
            v-model="bubbleForm.bubble_description"
            type="textarea"
            :rows="3"
            placeholder="请描述气泡情况"
          />
        </el-form-item>
        <el-form-item label="气泡数量" prop="bubble_count">
          <el-input-number v-model="bubbleForm.bubble_count" :min="0" :max="10000" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：个</span>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="bubbleForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bubbleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBubble" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="reworkDialogVisible"
      title="返工完成"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="reworkFormRef"
        :model="reworkForm"
        :rules="reworkRules"
        label-width="100px"
      >
        <el-form-item label="返工时间" prop="record_time">
          <el-date-picker
            v-model="reworkForm.record_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="返工原因" prop="rework_reason">
          <el-input
            v-model="reworkForm.rework_reason"
            type="textarea"
            :rows="3"
            placeholder="请输入返工原因"
          />
        </el-form-item>
        <el-form-item label="返工数量" prop="rework_count">
          <el-input-number v-model="reworkForm.rework_count" :min="1" :max="10000" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：件</span>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="reworkForm.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reworkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRework" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="inspectDialogVisible"
      title="质检记录"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="inspectFormRef"
        :model="inspectForm"
        :rules="inspectRules"
        label-width="100px"
      >
        <el-form-item label="质检时间" prop="inspect_time">
          <el-date-picker
            v-model="inspectForm.inspect_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="尺寸偏差" prop="dimension_deviation">
          <el-input v-model="inspectForm.dimension_deviation" placeholder="请输入尺寸偏差" />
        </el-form-item>
        <el-form-item label="表面平面度" prop="surface_flatness">
          <el-input-number v-model="inspectForm.surface_flatness" :min="0" :max="100" :precision="2" style="width: 100%;" />
          <span style="color: #94a3b8; font-size: 12px;">单位：mm</span>
        </el-form-item>
        <el-form-item label="是否通过" prop="pass">
          <el-radio-group v-model="inspectForm.pass">
            <el-radio :value="true">通过</el-radio>
            <el-radio :value="false">不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="质检意见" prop="opinion">
          <el-input
            v-model="inspectForm.opinion"
            type="textarea"
            :rows="3"
            placeholder="请输入质检意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="inspectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleInspect" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="deliveryReviewDialogVisible"
      title="交付复核"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="deliveryReviewFormRef"
        :model="deliveryReviewForm"
        :rules="deliveryReviewRules"
        label-width="110px"
      >
        <el-form-item label="复核时间" prop="review_time">
          <el-date-picker
            v-model="deliveryReviewForm.review_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="交付数量" prop="delivered_quantity">
          <el-input-number
            v-model="deliveryReviewForm.delivered_quantity"
            :min="1"
            :max="batchDetail?.quantity || 10000"
            style="width: 100%;"
          />
          <span style="color: #94a3b8; font-size: 12px;">
            批次总数量：{{ batchDetail?.quantity || '-' }} 件，交付数量不能超过总数量
          </span>
        </el-form-item>
        <el-form-item label="最终质量结论" prop="final_quality_conclusion">
          <el-input
            v-model="deliveryReviewForm.final_quality_conclusion"
            type="textarea"
            :rows="3"
            placeholder="请输入最终质量结论"
          />
        </el-form-item>
        <el-form-item label="复核结论" prop="pass">
          <el-radio-group v-model="deliveryReviewForm.pass">
            <el-radio :value="true">通过</el-radio>
            <el-radio :value="false">不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="异常备注" prop="exception_remark">
          <el-input
            v-model="deliveryReviewForm.exception_remark"
            type="textarea"
            :rows="2"
            placeholder="有异常情况请备注，无异常可留空"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliveryReviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDeliveryReview" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="deliveryArchiveDialogVisible"
      title="交付归档"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="deliveryArchiveFormRef"
        :model="deliveryArchiveForm"
        :rules="deliveryArchiveRules"
        label-width="110px"
      >
        <el-form-item label="交付时间" prop="delivery_time">
          <el-date-picker
            v-model="deliveryArchiveForm.delivery_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="交付数量" prop="delivered_quantity">
          <el-input-number
            v-model="deliveryArchiveForm.delivered_quantity"
            :min="1"
            :max="batchDetail?.quantity || 10000"
            style="width: 100%;"
          />
          <span style="color: #94a3b8; font-size: 12px;">
            批次总数量：{{ batchDetail?.quantity || '-' }} 件，交付数量不能超过总数量
          </span>
        </el-form-item>
        <el-form-item label="接收方" prop="receiver">
          <el-input
            v-model="deliveryArchiveForm.receiver"
            placeholder="请输入接收方"
          />
        </el-form-item>
        <el-form-item label="关联质检结论" prop="quality_conclusion">
          <el-input
            v-model="deliveryArchiveForm.quality_conclusion"
            type="textarea"
            :rows="3"
            placeholder="请输入关联质检结论"
          />
        </el-form-item>
        <el-form-item label="交付备注" prop="delivery_remark">
          <el-input
            v-model="deliveryArchiveForm.delivery_remark"
            type="textarea"
            :rows="2"
            placeholder="有备注请填写，无备注可留空"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliveryArchiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDeliveryArchive" :loading="submitting">确定归档</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  ArrowLeft, RefreshRight, Watermelon, Box, Crop,
  Warning, RefreshLeft, CircleCheck, DocumentChecked, Files
} from '@element-plus/icons-vue'
import { batchApi } from '@/api'
import {
  STATUS_MAP, STATUS_COLOR_MAP,
  REVIEW_STATUS_MAP, REVIEW_STATUS_COLOR_MAP,
  type BatchDetail, type ProcessRecord
} from '@/types'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const submitting = ref(false)
const batchDetail = ref<BatchDetail | null>(null)
const batchId = computed(() => Number(route.params.id))

const pourDialogVisible = ref(false)
const demoldDialogVisible = ref(false)
const trimDialogVisible = ref(false)
const bubbleDialogVisible = ref(false)
const reworkDialogVisible = ref(false)
const inspectDialogVisible = ref(false)
const deliveryReviewDialogVisible = ref(false)
const deliveryArchiveDialogVisible = ref(false)

const pourFormRef = ref<FormInstance>()
const demoldFormRef = ref<FormInstance>()
const trimFormRef = ref<FormInstance>()
const bubbleFormRef = ref<FormInstance>()
const reworkFormRef = ref<FormInstance>()
const inspectFormRef = ref<FormInstance>()
const deliveryReviewFormRef = ref<FormInstance>()
const deliveryArchiveFormRef = ref<FormInstance>()

const now = new Date().toISOString().slice(0, 19).replace('T', ' ')

const pourForm = reactive({
  record_time: now,
  temperature: null as number | null,
  pressure: null as number | null,
  hold_time: null as number | null,
  cooling_time: null as number | null,
  remark: ''
})

const demoldForm = reactive({
  record_time: now,
  cooling_time: null as number | null,
  remark: ''
})

const trimForm = reactive({
  record_time: now,
  remark: ''
})

const bubbleForm = reactive({
  record_time: now,
  bubble_description: '',
  bubble_count: null as number | null,
  remark: ''
})

const reworkForm = reactive({
  record_time: now,
  rework_reason: '',
  rework_count: null as number | null,
  remark: ''
})

const inspectForm = reactive({
  inspect_time: now,
  dimension_deviation: '',
  surface_flatness: null as number | null,
  pass: true,
  opinion: ''
})

const deliveryReviewForm = reactive({
  review_time: now,
  delivered_quantity: null as number | null,
  final_quality_conclusion: '',
  pass: true,
  exception_remark: ''
})

const deliveryArchiveForm = reactive({
  delivery_time: now,
  delivered_quantity: null as number | null,
  receiver: '',
  quality_conclusion: '',
  delivery_remark: ''
})

const pourRules: FormRules = {
  record_time: [{ required: true, message: '请选择浇注时间', trigger: 'change' }],
  temperature: [{ required: true, message: '请输入温度', trigger: 'blur' }],
  pressure: [{ required: true, message: '请输入压力', trigger: 'blur' }],
  hold_time: [{ required: true, message: '请输入保压时间', trigger: 'blur' }],
  cooling_time: [{ required: true, message: '请输入冷却时间', trigger: 'blur' }]
}

const demoldRules: FormRules = {
  record_time: [{ required: true, message: '请选择脱模时间', trigger: 'change' }],
  cooling_time: [{ required: true, message: '请输入冷却时间', trigger: 'blur' }]
}

const trimRules: FormRules = {
  record_time: [{ required: true, message: '请选择修边时间', trigger: 'change' }]
}

const bubbleRules: FormRules = {
  record_time: [{ required: true, message: '请选择记录时间', trigger: 'change' }],
  bubble_description: [{ required: true, message: '请输入气泡描述', trigger: 'blur' }],
  bubble_count: [{ required: true, message: '请输入气泡数量', trigger: 'blur' }]
}

const reworkRules: FormRules = {
  record_time: [{ required: true, message: '请选择返工时间', trigger: 'change' }],
  rework_reason: [{ required: true, message: '请输入返工原因', trigger: 'blur' }],
  rework_count: [{ required: true, message: '请输入返工数量', trigger: 'blur' }]
}

const inspectRules: FormRules = {
  inspect_time: [{ required: true, message: '请选择质检时间', trigger: 'change' }],
  dimension_deviation: [{ required: true, message: '请输入尺寸偏差', trigger: 'blur' }],
  surface_flatness: [{ required: true, message: '请输入表面平面度', trigger: 'blur' }],
  pass: [{ required: true, message: '请选择是否通过', trigger: 'change' }],
  opinion: [{ required: true, message: '请输入质检意见', trigger: 'blur' }]
}

const deliveryReviewRules: FormRules = {
  review_time: [{ required: true, message: '请选择复核时间', trigger: 'change' }],
  delivered_quantity: [
    { required: true, message: '请输入交付数量', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== null && value !== undefined && batchDetail.value && value > batchDetail.value.quantity) {
          callback(new Error('交付数量不能超过批次总数量'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  final_quality_conclusion: [{ required: true, message: '请输入最终质量结论', trigger: 'blur' }],
  pass: [{ required: true, message: '请选择复核结论', trigger: 'change' }]
}

const deliveryArchiveRules: FormRules = {
  delivery_time: [{ required: true, message: '请选择交付时间', trigger: 'change' }],
  delivered_quantity: [
    { required: true, message: '请输入交付数量', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== null && value !== undefined && batchDetail.value && value > batchDetail.value.quantity) {
          callback(new Error('交付数量不能超过批次总数量'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  receiver: [{ required: true, message: '请输入接收方', trigger: 'blur' }],
  quality_conclusion: [{ required: true, message: '请输入关联质检结论', trigger: 'blur' }]
}

const canPour = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && (status === 'pending_pour' || status === 'reworking')
})

const canDemold = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && status === 'molding'
})

const canTrim = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && (status === 'molding' || status === 'reworking')
})

const canRecordBubble = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && (status === 'molding' || status === 'reworking')
})

const canRework = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isTechnician = userStore.userRole === 'technician' || userStore.userRole === 'admin'
  return isTechnician && status === 'reworking'
})

const canInspect = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const isInspector = userStore.userRole === 'inspector' || userStore.userRole === 'admin'
  return isInspector && status === 'pending_inspect'
})

const canDeliveryReview = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const reviewStatus = batchDetail.value.review_status
  const isInspector = userStore.userRole === 'inspector' || userStore.userRole === 'admin'
  return isInspector && status === 'deliverable' && reviewStatus === 'pending_review'
})

const canDeliveryArchive = computed(() => {
  if (!batchDetail.value) return false
  const status = batchDetail.value.status
  const hasArchive = !!batchDetail.value.delivery_archive
  const isInspector = userStore.userRole === 'inspector' || userStore.userRole === 'admin'
  return isInspector && status === 'deliverable' && !hasArchive
})

const sortedProcessRecords = computed(() => {
  if (!batchDetail.value?.process_records) return []
  return [...batchDetail.value.process_records].sort(
    (a, b) => new Date(b.record_time).getTime() - new Date(a.record_time).getTime()
  )
})

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

const getRecordTypeName = (type: string) => {
  const map: Record<string, string> = {
    pour: '浇注',
    demold: '脱模',
    trim: '修边',
    bubble: '气泡记录',
    rework: '返工完成'
  }
  return map[type] || type
}

const getTimelineType = (type: string) => {
  const map: Record<string, 'primary' | 'success' | 'warning' | 'danger' | 'info'> = {
    pour: 'primary',
    demold: 'success',
    trim: 'info',
    bubble: 'warning',
    rework: 'danger'
  }
  return map[type] || 'primary'
}

const getTimelineColor = (type: string) => {
  const map: Record<string, string> = {
    pour: '#3b82f6',
    demold: '#10b981',
    trim: '#06b6d4',
    bubble: '#f59e0b',
    rework: '#ef4444'
  }
  return map[type] || '#3b82f6'
}

const loadDetail = async () => {
  if (!batchId.value) return
  loading.value = true
  try {
    const res = await batchApi.getDetail(batchId.value)
    batchDetail.value = res.data
  } catch (e) {
    console.error('Load batch detail failed', e)
    ElMessage.error('加载批次详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const openPourDialog = () => {
  pourForm.record_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  pourForm.temperature = null
  pourForm.pressure = null
  pourForm.hold_time = null
  pourForm.cooling_time = null
  pourForm.remark = ''
  pourFormRef.value?.resetFields()
  pourDialogVisible.value = true
}

const openDemoldDialog = () => {
  demoldForm.record_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  demoldForm.cooling_time = null
  demoldForm.remark = ''
  demoldFormRef.value?.resetFields()
  demoldDialogVisible.value = true
}

const openTrimDialog = () => {
  trimForm.record_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  trimForm.remark = ''
  trimFormRef.value?.resetFields()
  trimDialogVisible.value = true
}

const openBubbleDialog = () => {
  bubbleForm.record_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  bubbleForm.bubble_description = ''
  bubbleForm.bubble_count = null
  bubbleForm.remark = ''
  bubbleFormRef.value?.resetFields()
  bubbleDialogVisible.value = true
}

const openReworkDialog = () => {
  reworkForm.record_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  reworkForm.rework_reason = ''
  reworkForm.rework_count = null
  reworkForm.remark = ''
  reworkFormRef.value?.resetFields()
  reworkDialogVisible.value = true
}

const openInspectDialog = () => {
  inspectForm.inspect_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  inspectForm.dimension_deviation = ''
  inspectForm.surface_flatness = null
  inspectForm.pass = true
  inspectForm.opinion = ''
  inspectFormRef.value?.resetFields()
  inspectDialogVisible.value = true
}

const openDeliveryReviewDialog = () => {
  deliveryReviewFormRef.value?.resetFields()
  deliveryReviewForm.review_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  deliveryReviewForm.delivered_quantity = batchDetail.value?.quantity ?? null
  deliveryReviewForm.final_quality_conclusion = ''
  deliveryReviewForm.pass = true
  deliveryReviewForm.exception_remark = ''
  deliveryReviewDialogVisible.value = true
}

const openDeliveryArchiveDialog = () => {
  deliveryArchiveFormRef.value?.resetFields()
  deliveryArchiveForm.delivery_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  deliveryArchiveForm.delivered_quantity = batchDetail.value?.delivery_review?.delivered_quantity ?? batchDetail.value?.quantity ?? null
  deliveryArchiveForm.receiver = ''
  deliveryArchiveForm.quality_conclusion = batchDetail.value?.delivery_review?.final_quality_conclusion ?? ''
  deliveryArchiveForm.delivery_remark = ''
  deliveryArchiveDialogVisible.value = true
}

const handlePour = async () => {
  if (!pourFormRef.value) return
  await pourFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordPour(batchId.value, pourForm)
      ElMessage.success('浇注记录已保存')
      pourDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record pour failed', e)
      ElMessage.error(e.response?.data?.message || '保存浇注记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDemold = async () => {
  if (!demoldFormRef.value) return
  await demoldFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordDemold(batchId.value, demoldForm)
      ElMessage.success('脱模记录已保存')
      demoldDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record demold failed', e)
      ElMessage.error(e.response?.data?.message || '保存脱模记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleTrim = async () => {
  if (!trimFormRef.value) return
  await trimFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordTrim(batchId.value, trimForm)
      ElMessage.success('修边记录已保存，批次进入待质检状态')
      trimDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record trim failed', e)
      ElMessage.error(e.response?.data?.message || '保存修边记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleBubble = async () => {
  if (!bubbleFormRef.value) return
  await bubbleFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordBubble(batchId.value, bubbleForm)
      ElMessage.success('气泡记录已保存')
      bubbleDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record bubble failed', e)
      ElMessage.error(e.response?.data?.message || '保存气泡记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleRework = async () => {
  if (!reworkFormRef.value) return
  await reworkFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordRework(batchId.value, reworkForm)
      ElMessage.success('返工完成，批次重新进入待质检状态')
      reworkDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record rework failed', e)
      ElMessage.error(e.response?.data?.message || '记录返工失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleInspect = async () => {
  if (!inspectFormRef.value) return
  await inspectFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordInspect(batchId.value, inspectForm)
      const message = inspectForm.pass
        ? '质检通过，批次已进入可交付状态'
        : '质检未通过，批次进入返工状态'
      ElMessage.success(message)
      inspectDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record inspection failed', e)
      ElMessage.error(e.response?.data?.message || '保存质检记录失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDeliveryReview = async () => {
  if (!deliveryReviewFormRef.value) return
  await deliveryReviewFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordDeliveryReview(batchId.value, deliveryReviewForm)
      ElMessage.success('交付复核完成')
      deliveryReviewDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record delivery review failed', e)
      ElMessage.error(e.response?.data?.message || '保存交付复核失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDeliveryArchive = async () => {
  if (!deliveryArchiveFormRef.value) return
  await deliveryArchiveFormRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await batchApi.recordDeliveryArchive(batchId.value, deliveryArchiveForm)
      ElMessage.success('交付归档完成')
      deliveryArchiveDialogVisible.value = false
      loadDetail()
    } catch (e: any) {
      console.error('Record delivery archive failed', e)
      ElMessage.error(e.response?.data?.message || '保存交付归档失败')
    } finally {
      submitting.value = false
    }
  })
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.header-left {
  display: flex;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.info-item.full-width {
  grid-column: span 3;
}

.info-item .label {
  color: #6b7280;
  width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #1f2937;
  font-weight: 500;
}

.action-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding: 0 4px;
}

.timeline-content {
  padding: 8px 0;
}

.timeline-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-type {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.operator {
  font-size: 12px;
  color: #6b7280;
}

.timeline-details {
  font-size: 13px;
  color: #475569;
  line-height: 1.8;
}

.inspection-card {
  margin-bottom: 20px;
}

.delivery-review-card .review-info .info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.delivery-review-card .review-info .info-item.full-width {
  grid-column: span 2;
}

.review-empty {
  padding: 20px 0;
}

.delivery-archive-card .archive-info .info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.delivery-archive-card .archive-info .info-item.full-width {
  grid-column: span 2;
}

.archive-empty {
  padding: 20px 0;
}
</style>
