from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


class UserBase(BaseModel):
    username: str
    name: str
    role: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class StyleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class StyleCreate(StyleBase):
    pass


class StyleUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Style(StyleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class WaxBatchBase(BaseModel):
    code: str
    material: str
    production_date: date
    quantity: int
    remark: Optional[str] = None


class WaxBatchCreate(WaxBatchBase):
    pass


class WaxBatchUpdate(BaseModel):
    code: Optional[str] = None
    material: Optional[str] = None
    production_date: Optional[date] = None
    quantity: Optional[int] = None
    remark: Optional[str] = None


class WaxBatch(WaxBatchBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MoldBase(BaseModel):
    code: str
    name: str
    style_id: int
    max_cavities: int
    status: str = "available"


class MoldCreate(MoldBase):
    pass


class MoldUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    style_id: Optional[int] = None
    max_cavities: Optional[int] = None
    status: Optional[str] = None


class Mold(MoldBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MoldWithStyle(Mold):
    style: Style


class StationBase(BaseModel):
    code: str
    name: str
    type: str
    status: str = "idle"


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class Station(StationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InspectionCycleBase(BaseModel):
    style_id: int
    cycle_days: int


class InspectionCycleCreate(InspectionCycleBase):
    pass


class InspectionCycleUpdate(BaseModel):
    style_id: Optional[int] = None
    cycle_days: Optional[int] = None


class InspectionCycle(InspectionCycleBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class InspectionCycleWithStyle(InspectionCycle):
    style: Style


class BatchBase(BaseModel):
    code: str
    style_id: int
    wax_batch_id: int
    mold_id: int
    station_id: int
    technician_id: int
    inspector_id: Optional[int] = None
    planned_start_date: date
    planned_end_date: date
    quantity: int
    remark: Optional[str] = None


class BatchCreate(BatchBase):
    pass


class BatchUpdateStatus(BaseModel):
    status: str
    remark: Optional[str] = None


class Batch(BatchBase):
    id: int
    status: str
    review_status: str = "not_required"
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class DeliveryReviewBase(BaseModel):
    review_time: datetime
    delivered_quantity: int
    final_quality_conclusion: str
    is_pass: bool = Field(alias="pass")
    exception_remark: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class DeliveryReviewCreate(BaseModel):
    review_time: datetime
    delivered_quantity: int
    final_quality_conclusion: str
    is_pass: bool = Field(alias="pass")
    exception_remark: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class DeliveryReview(DeliveryReviewBase):
    id: int
    batch_id: int
    reviewer_id: int
    created_at: datetime


class DeliveryReviewWithReviewer(DeliveryReview):
    reviewer: User


class DeliveryArchiveBase(BaseModel):
    delivery_time: datetime
    delivered_quantity: int
    receiver: str
    delivery_remark: Optional[str] = None
    quality_conclusion: str
    model_config = ConfigDict(from_attributes=True)


class DeliveryArchiveCreate(BaseModel):
    delivery_time: datetime
    delivered_quantity: int
    receiver: str
    delivery_remark: Optional[str] = None
    quality_conclusion: str
    model_config = ConfigDict(from_attributes=True)


class DeliveryArchive(DeliveryArchiveBase):
    id: int
    batch_id: int
    archiver_id: int
    created_at: datetime


class DeliveryArchiveWithArchiver(DeliveryArchive):
    archiver: User


class DeliveryArchiveItem(BaseModel):
    id: int
    batch_id: int
    batch_code: str
    style_id: int
    style_name: str
    wax_batch_code: str
    delivery_time: datetime
    delivered_quantity: int
    receiver: str
    delivery_remark: Optional[str] = None
    quality_conclusion: str
    archiver_id: int
    archiver_name: str
    technician_id: int
    technician_name: str
    status: str
    status_name: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BatchDetail(Batch):
    style: Style
    wax_batch: WaxBatch
    mold: Mold
    station: Station
    technician: User
    inspector: Optional[User] = None
    process_records: List["ProcessRecord"] = []
    inspection_records: List["InspectionRecord"] = []
    delivery_review: Optional[DeliveryReviewWithReviewer] = None
    delivery_archive: Optional[DeliveryArchiveWithArchiver] = None
    rework_records: List["ReworkRecordWithDetails"] = []


class ProcessRecordBase(BaseModel):
    batch_id: int
    type: str
    record_time: datetime
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    hold_time: Optional[int] = None
    cooling_time: Optional[int] = None
    bubble_description: Optional[str] = None
    bubble_count: Optional[int] = None
    rework_reason: Optional[str] = None
    rework_count: Optional[int] = None
    remark: Optional[str] = None


class ProcessRecordCreate(ProcessRecordBase):
    pass


class ProcessRecord(ProcessRecordBase):
    id: int
    operator_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ProcessRecordWithOperator(ProcessRecord):
    operator: User


class PourRecordCreate(BaseModel):
    record_time: datetime
    temperature: float
    pressure: float
    hold_time: int
    cooling_time: int
    remark: Optional[str] = None


class DemoldRecordCreate(BaseModel):
    record_time: datetime
    temperature: Optional[float] = None
    cooling_time: Optional[int] = None
    remark: Optional[str] = None


class TrimRecordCreate(BaseModel):
    record_time: datetime
    remark: Optional[str] = None


class BubbleRecordCreate(BaseModel):
    record_time: datetime
    bubble_description: str
    bubble_count: int
    remark: Optional[str] = None


class ReworkRecordCreate(BaseModel):
    record_time: datetime
    rework_reason: str
    rework_count: int
    remark: Optional[str] = None


class InspectionRecordBase(BaseModel):
    batch_id: int
    inspect_time: datetime
    dimension_deviation: str
    surface_flatness: float
    is_pass: bool = Field(alias="pass")
    opinion: str
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InspectionRecordCreate(BaseModel):
    inspect_time: datetime
    dimension_deviation: str
    surface_flatness: float
    is_pass: bool = Field(alias="pass")
    opinion: str
    model_config = ConfigDict(populate_by_name=True)


class InspectionRecord(InspectionRecordBase):
    id: int
    inspector_id: int
    created_at: datetime


class InspectionRecordWithInspector(InspectionRecord):
    inspector: User


class WarningItem(BaseModel):
    type: str
    level: str
    title: str
    content: str
    related_id: Optional[int] = None
    related_type: Optional[str] = None
    created_at: Optional[datetime] = None


class DashboardSummary(BaseModel):
    total_batches: int
    pending_pour: int
    molding: int
    pending_inspect: int
    reworking: int
    deliverable: int
    delivered: int
    paused: int
    pending_delivery_review: int
    warning_count: int
    pending_rework: int
    overdue_rework: int
    waiting_rework_inspection: int


class BatchProgressItem(BaseModel):
    status: str
    status_name: str
    count: int
    color: str


class StationLoadItem(BaseModel):
    id: int
    code: str
    name: str
    type: str
    type_name: str
    occupied: int
    total: int
    rate: float


class PendingInspectionItem(BaseModel):
    id: int
    code: str
    style_name: str
    technician_name: str
    created_at: datetime
    days_overdue: int


class PendingDeliveryReviewItem(BaseModel):
    id: int
    code: str
    style_name: str
    technician_name: str
    inspector_name: Optional[str] = None
    quantity: int
    actual_end_date: Optional[datetime] = None
    days_pending: int


class ReworkRecordBase(BaseModel):
    batch_id: int
    rework_reason: str
    handling_instruction: Optional[str] = None
    responsible_id: int
    expected_finish_time: Optional[datetime] = None


class ReworkRecordCreate(ReworkRecordBase):
    pass


class ReworkRecordStart(BaseModel):
    pass


class ReworkRecordComplete(BaseModel):
    actual_finish_time: datetime
    rework_result: str


class ReworkRecord(BaseModel):
    id: int
    batch_id: int
    rework_no: int
    initiator_id: int
    responsible_id: int
    status: str
    rework_reason: str
    handling_instruction: Optional[str] = None
    expected_finish_time: Optional[datetime] = None
    actual_finish_time: Optional[datetime] = None
    rework_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ReworkRecordWithDetails(ReworkRecord):
    initiator: User
    responsible: User
    batch_code: Optional[str] = None
    style_name: Optional[str] = None
    status_name: Optional[str] = None


class ReworkStats(BaseModel):
    pending_rework: int
    overdue_rework: int
    waiting_inspection: int
    total_rework: int
