"""
即时物流骑手智能召回系统配置文件
包含所有系统配置参数和常量定义
"""

from pydantic_settings import BaseSettings
from typing import Dict, List
import os
from datetime import datetime

class Settings(BaseSettings):
    """系统配置类"""
    
    # 基础配置
    APP_NAME: str = "即时物流骑手智能召回系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./logistics_system.db"
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # 预测模型配置
    PREDICTION_THRESHOLD: float = 0.1  # 缺口比例阈值，超过10%触发召回
    FORECAST_DAYS: int = 3  # 提前预测天数
    MODEL_UPDATE_INTERVAL: int = 30  # 模型更新间隔（天）
    
    # 召回配置
    MAX_CALL_ATTEMPTS: int = 3  # 最大拨打次数
    CALL_TIMEOUT: int = 30  # 通话超时时间（秒）
    RECALL_BATCH_SIZE: int = 10  # 批量召回数量
    
    # 分析配置
    SUCCESS_RATE_TARGET: float = 0.85  # 目标成功率
    ATTENDANCE_RATE_TARGET: float = 0.90  # 目标出勤率
    RESPONSE_TIME_TARGET: int = 300  # 目标响应时间（秒）
    
    # 骑手画像配置
    MIN_ACCEPTANCE_RATE: float = 0.7  # 最低接单率
    MIN_RESPONSE_TIME: int = 60  # 最低响应时间（秒）
    ACTIVE_DAYS_THRESHOLD: int = 7  # 活跃天数阈值
    
    # 通话分析配置
    INTENT_CONFIDENCE_THRESHOLD: float = 0.8  # 意愿识别置信度阈值
    CALL_ANALYSIS_MODEL: str = "sentiment_analysis"  # 通话分析模型
    
    # 节假日配置
    HOLIDAY_API_URL: str = "https://api.holiday.com"  # 节假日API
    HOLIDAY_CACHE_DAYS: int = 365  # 节假日缓存天数
    
    # 通知配置
    NOTIFICATION_CHANNELS: List[str] = ["app", "sms", "email"]
    NOTIFICATION_RETRY_TIMES: int = 3
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/system.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # Agent配置
    AGENT_TIMEOUT: int = 60  # Agent执行超时时间（秒）
    MAX_CONCURRENT_AGENTS: int = 5  # 最大并发Agent数量
    
    # 外部服务配置
    WEATHER_API_KEY: str = ""  # 天气API密钥
    WEATHER_API_URL: str = "https://api.weather.com"
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 缓存过期时间（秒）
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()

# 业务规则配置
BUSINESS_RULES = {
    "prediction": {
        "min_historical_days": 30,  # 最少历史数据天数
        "weather_weight": 0.2,      # 天气因子权重
        "trend_weight": 0.3,        # 趋势因子权重
        "holiday_weight": 0.5       # 节假日因子权重
    },
    "rider_selection": {
        "max_candidates": 50,       # 最大候选人数
        "distance_threshold": 5,    # 距离阈值（公里）
        "availability_hours": 8     # 可用时长阈值（小时）
    },
    "call_strategy": {
        "priority_levels": ["high", "medium", "low"],
        "call_intervals": [0, 30, 120],  # 拨打间隔（分钟）
        "max_daily_calls": 100      # 每日最大拨打数
    }
}

# 意愿分析标签
INTENT_LABELS = {
    "strong": "强意愿",
    "hesitant": "犹豫",
    "neutral": "中立", 
    "reject": "拒绝"
}

# 状态码定义
STATUS_CODES = {
    "success": 200,
    "pending": 201,
    "failed": 400,
    "timeout": 408,
    "error": 500
}

# 数据库表配置
DB_TABLES = {
    "sites": "站点信息表",
    "riders": "骑手信息表", 
    "orders": "订单数据表",
    "predictions": "预测结果表",
    "recalls": "召回记录表",
    "calls": "通话记录表",
    "attendance": "出勤记录表",
    "analytics": "分析结果表"
}

# 应用基本信息
DESCRIPTION: str = "基于多Agent协同的智能骑手召回系统" 