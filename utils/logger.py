"""
日志工具模块
提供统一的日志管理功能
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from config.settings import settings

def setup_logger(name: str = None) -> logging.Logger:
    """
    设置并返回logger实例
    
    Args:
        name: logger名称，默认为调用模块名
        
    Returns:
        logging.Logger: 配置好的logger实例
    """
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 移除默认的loguru handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        settings.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8"
    )
    
    # 为特定模块添加专用日志文件
    if name:
        module_log_file = log_dir / f"{name}.log"
        logger.add(
            str(module_log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level=settings.LOG_LEVEL,
            rotation="1 day",
            retention="7 days",
            filter=lambda record: record["name"] == name
        )
    
    return logger

def log_workflow_step(step_name: str, details: dict = None):
    """
    记录工作流步骤
    
    Args:
        step_name: 步骤名称
        details: 详细信息
    """
    logger.info(f"工作流步骤: {step_name}")
    if details:
        for key, value in details.items():
            logger.info(f"  {key}: {value}")

def log_agent_action(agent_name: str, action: str, result: dict = None):
    """
    记录Agent行为
    
    Args:
        agent_name: Agent名称
        action: 执行的行为
        result: 执行结果
    """
    logger.info(f"Agent行为 [{agent_name}]: {action}")
    if result:
        logger.info(f"  结果: {result}")

def log_performance(operation: str, duration: float, details: dict = None):
    """
    记录性能指标
    
    Args:
        operation: 操作名称
        duration: 执行时长（秒）
        details: 额外详情
    """
    logger.info(f"性能指标 [{operation}]: {duration:.2f}秒")
    if details:
        for key, value in details.items():
            logger.info(f"  {key}: {value}")

def log_error(error: Exception, context: str = None):
    """
    记录错误信息
    
    Args:
        error: 异常对象
        context: 错误上下文
    """
    if context:
        logger.error(f"错误上下文: {context}")
    logger.exception(f"异常信息: {str(error)}")

# 创建专用logger实例
workflow_logger = setup_logger("workflow")
agent_logger = setup_logger("agent")
performance_logger = setup_logger("performance") 