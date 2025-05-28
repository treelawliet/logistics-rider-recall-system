"""
数据模型定义
定义系统中所有业务实体的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举定义
class IntentLevel(str, Enum):
    """意愿等级枚举"""
    STRONG = "strong"      # 强意愿
    HESITANT = "hesitant"  # 犹豫
    NEUTRAL = "neutral"    # 中立
    REJECT = "reject"      # 拒绝

class CallStatus(str, Enum):
    """通话状态枚举"""
    PENDING = "pending"    # 待拨打
    CALLING = "calling"    # 拨打中
    CONNECTED = "connected"  # 已接通
    FAILED = "failed"      # 拨打失败
    COMPLETED = "completed"  # 已完成

class RiderStatus(str, Enum):
    """骑手状态枚举"""
    ACTIVE = "active"      # 活跃
    INACTIVE = "inactive"  # 不活跃
    BUSY = "busy"         # 忙碌
    OFFLINE = "offline"    # 离线

# 基础模型
class BaseSchema(BaseModel):
    """基础模型类"""
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

# 站点相关模型
class SiteInfo(BaseSchema):
    """站点信息模型"""
    site_id: str = Field(..., description="站点ID")
    site_name: str = Field(..., description="站点名称")
    city: str = Field(..., description="所在城市")
    district: str = Field(..., description="所在区域")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    active_riders: int = Field(default=0, description="活跃骑手数")
    coverage_radius: float = Field(default=5.0, description="覆盖半径(公里)")

# 骑手相关模型
class RiderProfile(BaseSchema):
    """骑手画像模型"""
    rider_id: str = Field(..., description="骑手ID")
    name: str = Field(..., description="骑手姓名")
    phone: str = Field(..., description="联系电话")
    site_id: str = Field(..., description="所属站点")
    status: RiderStatus = Field(default=RiderStatus.ACTIVE, description="当前状态")
    
    # 历史表现指标
    acceptance_rate: float = Field(default=0.0, description="接单率")
    avg_response_time: int = Field(default=0, description="平均响应时间(秒)")
    completion_rate: float = Field(default=0.0, description="完成率")
    active_days: int = Field(default=0, description="活跃天数")
    
    # 位置信息
    current_latitude: Optional[float] = Field(None, description="当前纬度")
    current_longitude: Optional[float] = Field(None, description="当前经度")
    last_active_time: Optional[datetime] = Field(None, description="最后活跃时间")

class RiderCandidate(BaseModel):
    """候选骑手模型"""
    rider_id: str
    name: str
    phone: str
    score: float = Field(..., description="匹配得分")
    distance: float = Field(..., description="距离站点距离(公里)")
    availability: bool = Field(default=True, description="是否可用")
    priority: str = Field(default="medium", description="优先级")

# 预测相关模型
class PredictionRequest(BaseModel):
    """预测请求模型"""
    site_id: str = Field(..., description="站点ID")
    target_date: str = Field(..., description="目标日期 YYYY-MM-DD")
    include_weather: bool = Field(default=True, description="是否包含天气因素")

class PredictionResult(BaseSchema):
    """预测结果模型"""
    site_id: str = Field(..., description="站点ID")
    target_date: str = Field(..., description="目标日期")
    has_gap: bool = Field(..., description="是否存在运力缺口")
    gap_ratio: float = Field(..., description="缺口比例")
    predicted_orders: int = Field(..., description="预测订单量")
    current_capacity: int = Field(..., description="当前运力")
    required_riders: int = Field(..., description="需要补充的骑手数")
    confidence: float = Field(..., description="预测置信度")
    suggestion: str = Field(..., description="建议行动")

# 召回相关模型
class RecallTask(BaseSchema):
    """召回任务模型"""
    task_id: str = Field(..., description="任务ID")
    site_id: str = Field(..., description="站点ID")
    target_date: str = Field(..., description="目标日期")
    required_riders: int = Field(..., description="需要召回的骑手数")
    status: str = Field(default="pending", description="任务状态")
    created_by: str = Field(..., description="创建人")

class CallRecord(BaseSchema):
    """通话记录模型"""
    call_id: str = Field(..., description="通话ID")
    task_id: str = Field(..., description="关联任务ID")
    rider_id: str = Field(..., description="骑手ID")
    phone: str = Field(..., description="拨打号码")
    status: CallStatus = Field(..., description="通话状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: int = Field(default=0, description="通话时长(秒)")
    transcript: Optional[str] = Field(None, description="通话转写内容")
    intent_level: Optional[IntentLevel] = Field(None, description="意愿等级")
    confidence: float = Field(default=0.0, description="分析置信度")
    notes: Optional[str] = Field(None, description="备注")

# 出勤相关模型
class AttendanceRecord(BaseSchema):
    """出勤记录模型"""
    record_id: str = Field(..., description="记录ID")
    rider_id: str = Field(..., description="骑手ID")
    task_id: str = Field(..., description="关联任务ID")
    target_date: str = Field(..., description="目标日期")
    expected_time: datetime = Field(..., description="预期上班时间")
    actual_time: Optional[datetime] = Field(None, description="实际上班时间")
    is_attended: bool = Field(default=False, description="是否出勤")
    delay_minutes: int = Field(default=0, description="迟到分钟数")
    work_hours: float = Field(default=0.0, description="工作时长")

# 分析相关模型
class AnalyticsResult(BaseSchema):
    """分析结果模型"""
    analysis_id: str = Field(..., description="分析ID")
    task_id: str = Field(..., description="关联任务ID")
    site_id: str = Field(..., description="站点ID")
    
    # 关键指标
    total_calls: int = Field(..., description="总拨打次数")
    successful_calls: int = Field(..., description="成功接通次数")
    attended_riders: int = Field(..., description="实际出勤人数")
    
    # 计算指标
    recall_success_rate: float = Field(..., description="召回成功率")
    call_success_rate: float = Field(..., description="拨打成功率")
    attendance_rate: float = Field(..., description="出勤率")
    prediction_accuracy: float = Field(..., description="预测准确率")
    
    # 时间指标
    avg_response_time: float = Field(..., description="平均响应时间")
    total_process_time: float = Field(..., description="总处理时间")
    
    # 建议
    recommendations: List[str] = Field(default=[], description="优化建议")

# 决策相关模型
class DecisionRequest(BaseModel):
    """决策请求模型"""
    site_id: str = Field(..., description="站点ID")
    prediction_result: PredictionResult = Field(..., description="预测结果")
    manager_feedback: bool = Field(..., description="站长确认结果")
    notes: Optional[str] = Field(None, description="备注")

class DecisionResult(BaseModel):
    """决策结果模型"""
    accepted: bool = Field(..., description="是否接受召回")
    next_step: str = Field(..., description="下一步操作")
    reason: Optional[str] = Field(None, description="决策原因")

# API响应模型
class APIResponse(BaseModel):
    """API响应基础模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

# 工作流状态模型
class WorkflowStatus(BaseModel):
    """工作流状态模型"""
    workflow_id: str = Field(..., description="工作流ID")
    current_stage: str = Field(..., description="当前阶段")
    completed_stages: List[str] = Field(default=[], description="已完成阶段")
    progress: float = Field(default=0.0, description="进度百分比")
    status: str = Field(default="running", description="状态")
    error_message: Optional[str] = Field(None, description="错误信息")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间") 