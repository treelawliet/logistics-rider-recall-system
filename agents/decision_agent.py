"""
决策协调Agent
负责处理站长确认反馈，决定是否启动召回流程
"""

from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from typing import Dict, Any, List
import json
from datetime import datetime
from models.schemas import DecisionRequest, DecisionResult, PredictionResult
from config.settings import settings

class NotificationTool(BaseTool):
    """通知工具"""
    name: str = "notification_tool"
    description: str = "向站长发送预测结果通知"
    
    def _run(self, site_id: str, prediction: Dict[str, Any], channels: List[str] = None) -> Dict[str, Any]:
        """
        发送通知给站长（模拟实现）
        在实际项目中，这里会调用真实的通知服务
        """
        if channels is None:
            channels = ["app", "sms"]
            
        notification_data = {
            "site_id": site_id,
            "timestamp": datetime.now().isoformat(),
            "channels": channels,
            "message": f"""
            【运力预警】
            站点: {site_id}
            日期: {prediction.get('target_date')}
            预测订单: {prediction.get('predicted_orders')}
            当前运力: {prediction.get('current_capacity')}
            缺口比例: {prediction.get('gap_ratio', 0):.1%}
            建议行动: {prediction.get('suggestion')}
            
            请确认是否启动骑手召回流程？
            """,
            "status": "sent",
            "delivery_status": {
                "app": "delivered",
                "sms": "delivered"
            }
        }
        
        return notification_data

class FeedbackCollectionTool(BaseTool):
    """反馈收集工具"""
    name: str = "feedback_collection_tool"
    description: str = "收集站长的确认反馈"
    
    def _run(self, site_id: str, timeout_minutes: int = 30) -> Dict[str, Any]:
        """
        收集站长反馈（模拟实现）
        在实际项目中，这里会等待真实的用户反馈
        """
        import random
        
        # 模拟站长反馈
        # 在实际项目中，这里会从数据库或消息队列中获取真实反馈
        feedback_options = [
            {"decision": True, "reason": "同意召回，预测合理"},
            {"decision": True, "reason": "确实需要补充运力"},
            {"decision": False, "reason": "当前运力足够"},
            {"decision": False, "reason": "成本考虑，暂不召回"}
        ]
        
        # 80%概率同意召回（模拟真实场景中站长的决策倾向）
        if random.random() < 0.8:
            feedback = feedback_options[random.randint(0, 1)]
        else:
            feedback = feedback_options[random.randint(2, 3)]
            
        feedback_data = {
            "site_id": site_id,
            "timestamp": datetime.now().isoformat(),
            "manager_decision": feedback["decision"],
            "reason": feedback["reason"],
            "response_time": random.randint(5, timeout_minutes),  # 响应时间（分钟）
            "confidence_level": random.uniform(0.7, 1.0)  # 决策信心度
        }
        
        return feedback_data

class DecisionLogTool(BaseTool):
    """决策日志工具"""
    name: str = "decision_log_tool"
    description: str = "记录决策过程和结果"
    
    def _run(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        记录决策日志（模拟实现）
        在实际项目中，这里会写入数据库
        """
        log_entry = {
            "log_id": f"decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "site_id": decision_data.get("site_id"),
            "prediction_data": decision_data.get("prediction"),
            "manager_feedback": decision_data.get("feedback"),
            "final_decision": decision_data.get("decision"),
            "next_action": decision_data.get("next_step"),
            "decision_factors": decision_data.get("factors", []),
            "status": "logged"
        }
        
        print(f"决策日志已记录: {log_entry['log_id']}")
        return log_entry

def create_decision_agent() -> Agent:
    """创建决策协调Agent"""
    
    return Agent(
        role="决策协调员",
        goal="基于预测结果和站长反馈，做出是否启动召回流程的最终决策",
        backstory="""
        你是一位经验丰富的运营协调员，负责协调预测系统和人工决策。
        你需要综合考虑预测结果的准确性、站长的实际情况反馈、
        以及业务规则，做出最优的决策。
        你的决策直接影响后续的召回流程是否启动。
        """,
        tools=[
            NotificationTool(),
            FeedbackCollectionTool(),
            DecisionLogTool()
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )

def create_decision_task(agent: Agent, request: DecisionRequest) -> Task:
    """创建决策任务"""
    
    prediction = request.prediction_result
    
    return Task(
        description=f"""
        处理站点 {request.site_id} 的召回决策流程：
        
        1. 分析预测结果的可信度和紧急程度
        2. 向站长发送预测结果通知
        3. 收集站长的确认反馈
        4. 综合预测数据和人工反馈做出最终决策
        5. 记录决策过程和结果
        
        预测结果摘要：
        - 目标日期: {prediction.target_date}
        - 存在缺口: {prediction.has_gap}
        - 缺口比例: {prediction.gap_ratio:.1%}
        - 需要骑手: {prediction.required_riders}人
        - 预测置信度: {prediction.confidence:.1%}
        
        决策规则：
        - 缺口比例 > {settings.PREDICTION_THRESHOLD:.1%} 且站长同意 → 启动召回
        - 缺口比例 ≤ {settings.PREDICTION_THRESHOLD:.1%} → 不启动召回
        - 站长明确拒绝 → 不启动召回
        
        请确保决策结果包含：
        - 是否接受召回
        - 下一步操作
        - 决策原因
        """,
        agent=agent,
        expected_output="""
        返回JSON格式的决策结果，包含以下字段：
        {
            "accepted": "是否接受召回(布尔值)",
            "next_step": "下一步操作(字符串)",
            "reason": "决策原因(字符串)"
        }
        """
    )

class DecisionService:
    """决策服务类"""
    
    def __init__(self):
        self.agent = create_decision_agent()
        
    def make_decision(self, request: DecisionRequest) -> DecisionResult:
        """
        执行决策流程
        
        Args:
            request: 决策请求
            
        Returns:
            DecisionResult: 决策结果
        """
        try:
            # 创建决策任务
            task = create_decision_task(self.agent, request)
            
            # 创建Crew并执行
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # 执行决策
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
                
            # 创建决策结果对象
            decision_result = DecisionResult(
                accepted=result_data.get("accepted", False),
                next_step=result_data.get("next_step", "结束流程"),
                reason=result_data.get("reason", "未知原因")
            )
            
            return decision_result
            
        except Exception as e:
            # 返回默认决策结果
            return DecisionResult(
                accepted=False,
                next_step="结束流程",
                reason=f"决策失败: {str(e)}"
            )
    
    def _parse_text_result(self, text_result: str, request: DecisionRequest) -> Dict[str, Any]:
        """
        从文本结果中解析决策信息
        """
        # 简单的文本解析逻辑
        text_lower = text_result.lower()
        
        # 判断是否接受召回
        accept_keywords = ["同意", "接受", "启动", "召回", "yes", "true"]
        reject_keywords = ["拒绝", "不同意", "不启动", "no", "false"]
        
        accepted = any(keyword in text_lower for keyword in accept_keywords)
        if any(keyword in text_lower for keyword in reject_keywords):
            accepted = False
            
        # 根据预测结果和站长反馈综合判断
        if request.prediction_result.has_gap and request.manager_feedback:
            accepted = True
        elif not request.manager_feedback:
            accepted = False
            
        result = {
            "accepted": accepted,
            "next_step": "启动骑手画像筛选" if accepted else "结束召回流程",
            "reason": text_result[:100] if text_result else "基于预测结果和站长反馈的综合决策"
        }
        
        return result
    
    def get_decision_history(self, site_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取决策历史记录
        
        Args:
            site_id: 站点ID
            days: 查询天数
            
        Returns:
            List[Dict]: 决策历史列表
        """
        # 模拟历史决策数据
        # 在实际项目中，这里会查询数据库
        
        import random
        from datetime import timedelta
        
        history = []
        for i in range(random.randint(5, 15)):
            date = datetime.now() - timedelta(days=random.randint(1, days))
            
            decision_record = {
                "decision_id": f"decision_{date.strftime('%Y%m%d')}_{i}",
                "site_id": site_id,
                "date": date.strftime('%Y-%m-%d'),
                "prediction_gap_ratio": random.uniform(0.05, 0.3),
                "manager_feedback": random.choice([True, False]),
                "final_decision": random.choice([True, False]),
                "success_rate": random.uniform(0.7, 0.95) if random.choice([True, False]) else None
            }
            
            history.append(decision_record)
            
        return sorted(history, key=lambda x: x['date'], reverse=True)

# 使用示例
if __name__ == "__main__":
    from agents.prediction_agent import PredictionService, PredictionRequest
    
    # 创建预测服务和决策服务
    prediction_service = PredictionService()
    decision_service = DecisionService()
    
    # 1. 先进行预测
    prediction_request = PredictionRequest(
        site_id="site_001",
        target_date="2024-02-14",
        include_weather=True
    )
    
    prediction_result = prediction_service.predict_demand(prediction_request)
    print("预测结果:")
    print(f"存在缺口: {prediction_result.has_gap}")
    print(f"缺口比例: {prediction_result.gap_ratio:.2%}")
    print(f"建议: {prediction_result.suggestion}")
    print()
    
    # 2. 进行决策
    decision_request = DecisionRequest(
        site_id="site_001",
        prediction_result=prediction_result,
        manager_feedback=True,  # 模拟站长同意
        notes="站长确认需要补充运力"
    )
    
    decision_result = decision_service.make_decision(decision_request)
    print("决策结果:")
    print(f"是否接受: {decision_result.accepted}")
    print(f"下一步: {decision_result.next_step}")
    print(f"原因: {decision_result.reason}")
    print()
    
    # 3. 查看决策历史
    history = decision_service.get_decision_history("site_001")
    print(f"最近决策历史 (共{len(history)}条):")
    for record in history[:3]:  # 显示最近3条
        print(f"日期: {record['date']}, 决策: {record['final_decision']}, 缺口: {record['prediction_gap_ratio']:.1%}") 