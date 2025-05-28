"""
预测分析Agent
负责节假日前3天的订单增量与运力缺口预测
"""

from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from models.schemas import PredictionRequest, PredictionResult
from config.settings import settings, BUSINESS_RULES

class WeatherDataTool(BaseTool):
    """天气数据获取工具"""
    name: str = "weather_data_tool"
    description: str = "获取指定日期和地点的天气预报数据"
    
    def _run(self, date: str, city: str) -> Dict[str, Any]:
        """
        获取天气数据（模拟实现）
        在实际项目中，这里会调用真实的天气API
        """
        # 模拟天气数据
        weather_data = {
            "date": date,
            "city": city,
            "temperature": np.random.randint(15, 30),
            "humidity": np.random.randint(40, 80),
            "precipitation": np.random.choice([0, 0, 0, 0.1, 0.3, 0.5]),  # 大部分时间不下雨
            "wind_speed": np.random.randint(5, 15),
            "weather_type": np.random.choice(["晴天", "多云", "阴天", "小雨"])
        }
        return weather_data

class HistoricalDataTool(BaseTool):
    """历史数据获取工具"""
    name: str = "historical_data_tool"
    description: str = "获取站点的历史订单和履约数据"
    
    def _run(self, site_id: str, days: int = 30) -> Dict[str, Any]:
        """
        获取历史数据（模拟实现）
        在实际项目中，这里会查询真实的数据库
        """
        # 生成模拟的历史数据
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        historical_data = {
            "site_id": site_id,
            "data_points": []
        }
        
        for date in dates:
            # 模拟节假日效应
            is_weekend = date.weekday() >= 5
            is_holiday = date.strftime('%m-%d') in ['01-01', '02-14', '05-01', '10-01']
            
            base_orders = 100
            if is_weekend:
                base_orders *= 1.3
            if is_holiday:
                base_orders *= 1.8
                
            data_point = {
                "date": date.strftime('%Y-%m-%d'),
                "orders": int(base_orders + np.random.normal(0, 20)),
                "active_riders": np.random.randint(15, 25),
                "completion_rate": np.random.uniform(0.85, 0.98),
                "avg_delivery_time": np.random.randint(25, 45),
                "is_weekend": is_weekend,
                "is_holiday": is_holiday
            }
            historical_data["data_points"].append(data_point)
            
        return historical_data

class OrderTrendTool(BaseTool):
    """订单趋势分析工具"""
    name: str = "order_trend_tool"
    description: str = "分析最近24小时的订单趋势"
    
    def _run(self, site_id: str) -> Dict[str, Any]:
        """
        分析订单趋势（模拟实现）
        """
        # 生成最近24小时的订单数据
        hours = pd.date_range(end=datetime.now(), periods=24, freq='H')
        
        trend_data = {
            "site_id": site_id,
            "hourly_orders": [],
            "growth_rate": np.random.uniform(-0.1, 0.3),  # -10% 到 +30%
            "peak_hours": ["11:00-13:00", "18:00-20:00"]
        }
        
        for hour in hours:
            # 模拟一天中的订单分布
            hour_of_day = hour.hour
            if 11 <= hour_of_day <= 13 or 18 <= hour_of_day <= 20:
                base_orders = 15  # 高峰期
            elif 7 <= hour_of_day <= 10 or 14 <= hour_of_day <= 17:
                base_orders = 8   # 次高峰
            else:
                base_orders = 3   # 低峰期
                
            orders = max(0, int(base_orders + np.random.normal(0, 3)))
            
            trend_data["hourly_orders"].append({
                "hour": hour.strftime('%H:00'),
                "orders": orders
            })
            
        return trend_data

def create_prediction_agent() -> Agent:
    """创建预测分析Agent"""
    
    return Agent(
        role="预测分析师",
        goal="准确预测节假日前的订单增量和运力缺口，为调度决策提供数据支持",
        backstory="""
        你是一位经验丰富的数据分析师，专门负责即时物流行业的需求预测。
        你擅长分析历史数据、天气因素、节假日效应等多维度信息，
        能够准确预测未来的订单量和运力需求。
        你的预测结果直接影响站点的运营效率和用户体验。
        """,
        tools=[
            WeatherDataTool(),
            HistoricalDataTool(), 
            OrderTrendTool()
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

def create_prediction_task(agent: Agent, request: PredictionRequest) -> Task:
    """创建预测任务"""
    
    return Task(
        description=f"""
        分析站点 {request.site_id} 在 {request.target_date} 的运力需求：
        
        1. 获取该站点过去30天的历史订单和履约数据
        2. 分析最近24小时的订单趋势，计算增长率
        3. 获取目标日期的天气预报信息
        4. 综合分析节假日效应、天气影响、趋势变化
        5. 预测目标日期的订单量和运力缺口
        6. 给出具体的建议行动
        
        预测阈值：缺口比例超过 {settings.PREDICTION_THRESHOLD} 时触发召回
        
        请确保预测结果包含：
        - 是否存在运力缺口
        - 缺口比例
        - 预测订单量
        - 当前运力
        - 需要补充的骑手数
        - 预测置信度
        - 建议行动
        """,
        agent=agent,
        expected_output="""
        返回JSON格式的预测结果，包含以下字段：
        {
            "site_id": "站点ID",
            "target_date": "目标日期",
            "has_gap": "是否存在缺口(布尔值)",
            "gap_ratio": "缺口比例(浮点数)",
            "predicted_orders": "预测订单量(整数)",
            "current_capacity": "当前运力(整数)",
            "required_riders": "需要补充骑手数(整数)",
            "confidence": "预测置信度(0-1)",
            "suggestion": "建议行动(字符串)"
        }
        """
    )

class PredictionService:
    """预测服务类"""
    
    def __init__(self):
        self.agent = create_prediction_agent()
        
    def predict_demand(self, request: PredictionRequest) -> PredictionResult:
        """
        执行需求预测
        
        Args:
            request: 预测请求
            
        Returns:
            PredictionResult: 预测结果
        """
        try:
            # 创建预测任务
            task = create_prediction_task(self.agent, request)
            
            # 创建Crew并执行
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # 执行预测
            result = crew.kickoff()
            
            # 解析结果
            if isinstance(result, str):
                try:
                    result_data = json.loads(result)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，尝试从文本中提取信息
                    result_data = self._parse_text_result(result, request)
            else:
                result_data = result
                
            # 创建预测结果对象
            prediction_result = PredictionResult(
                site_id=result_data.get("site_id", request.site_id),
                target_date=result_data.get("target_date", request.target_date),
                has_gap=result_data.get("has_gap", False),
                gap_ratio=result_data.get("gap_ratio", 0.0),
                predicted_orders=result_data.get("predicted_orders", 0),
                current_capacity=result_data.get("current_capacity", 0),
                required_riders=result_data.get("required_riders", 0),
                confidence=result_data.get("confidence", 0.0),
                suggestion=result_data.get("suggestion", "无建议")
            )
            
            return prediction_result
            
        except Exception as e:
            # 返回默认结果
            return PredictionResult(
                site_id=request.site_id,
                target_date=request.target_date,
                has_gap=False,
                gap_ratio=0.0,
                predicted_orders=0,
                current_capacity=0,
                required_riders=0,
                confidence=0.0,
                suggestion=f"预测失败: {str(e)}"
            )
    
    def _parse_text_result(self, text_result: str, request: PredictionRequest) -> Dict[str, Any]:
        """
        从文本结果中解析预测信息
        """
        # 简单的文本解析逻辑
        # 在实际项目中，可以使用更复杂的NLP技术
        
        result = {
            "site_id": request.site_id,
            "target_date": request.target_date,
            "has_gap": "缺口" in text_result or "不足" in text_result,
            "gap_ratio": 0.15,  # 默认值
            "predicted_orders": 150,  # 默认值
            "current_capacity": 20,   # 默认值
            "required_riders": 5,     # 默认值
            "confidence": 0.8,        # 默认值
            "suggestion": text_result[:100] if text_result else "建议补充运力"
        }
        
        return result

# 使用示例
if __name__ == "__main__":
    # 创建预测服务
    service = PredictionService()
    
    # 创建预测请求
    request = PredictionRequest(
        site_id="site_001",
        target_date="2024-02-14",  # 情人节
        include_weather=True
    )
    
    # 执行预测
    result = service.predict_demand(request)
    
    print("预测结果:")
    print(f"站点: {result.site_id}")
    print(f"日期: {result.target_date}")
    print(f"存在缺口: {result.has_gap}")
    print(f"缺口比例: {result.gap_ratio:.2%}")
    print(f"预测订单: {result.predicted_orders}")
    print(f"当前运力: {result.current_capacity}")
    print(f"需要骑手: {result.required_riders}")
    print(f"置信度: {result.confidence:.2%}")
    print(f"建议: {result.suggestion}") 