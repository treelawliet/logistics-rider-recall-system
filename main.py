"""
即时物流骑手智能召回系统 - 主程序
基于CrewAI框架的多Agent协同系统
"""

import argparse
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import json

from agents.prediction_agent import PredictionService, PredictionRequest
from agents.decision_agent import DecisionService, DecisionRequest
from agents.rider_profiler_agent import RiderProfilerService
from models.schemas import WorkflowStatus, APIResponse
from config.settings import settings
from utils.logger import setup_logger

# 设置日志
logger = setup_logger(__name__)

class LogisticsWorkflow:
    """物流调度工作流协调器"""
    
    def __init__(self):
        """初始化所有服务"""
        self.prediction_service = PredictionService()
        self.decision_service = DecisionService()
        self.profiler_service = RiderProfilerService()
        
        # 工作流状态
        self.workflow_status = None
        
    async def run_complete_workflow(self, site_id: str, target_date: str, manager_feedback: bool = None) -> Dict[str, Any]:
        """
        运行完整的召回工作流
        
        Args:
            site_id: 站点ID
            target_date: 目标日期
            manager_feedback: 站长反馈（None表示需要等待反馈）
            
        Returns:
            Dict: 工作流执行结果
        """
        workflow_id = f"workflow_{site_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 初始化工作流状态
        self.workflow_status = WorkflowStatus(
            workflow_id=workflow_id,
            current_stage="初始化",
            completed_stages=[],
            progress=0.0,
            status="running"
        )
        
        logger.info(f"开始执行召回工作流: {workflow_id}")
        logger.info(f"站点: {site_id}, 目标日期: {target_date}")
        
        try:
            # 阶段1: 预测分析
            logger.info("=" * 50)
            logger.info("阶段1: 运力缺口预测")
            logger.info("=" * 50)
            
            self._update_workflow_status("预测分析", 20.0)
            
            prediction_request = PredictionRequest(
                site_id=site_id,
                target_date=target_date,
                include_weather=True
            )
            
            prediction_result = self.prediction_service.predict_demand(prediction_request)
            
            logger.info(f"预测完成:")
            logger.info(f"  存在缺口: {prediction_result.has_gap}")
            logger.info(f"  缺口比例: {prediction_result.gap_ratio:.2%}")
            logger.info(f"  需要骑手: {prediction_result.required_riders}人")
            logger.info(f"  置信度: {prediction_result.confidence:.2%}")
            
            # 如果没有缺口，直接结束
            if not prediction_result.has_gap:
                self._update_workflow_status("完成", 100.0, "success")
                return {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "result": "无需召回",
                    "prediction": prediction_result.dict(),
                    "message": "预测显示运力充足，无需召回骑手"
                }
            
            # 阶段2: 决策确认
            logger.info("\n" + "=" * 50)
            logger.info("阶段2: 站长决策确认")
            logger.info("=" * 50)
            
            self._update_workflow_status("决策确认", 40.0)
            
            # 如果没有提供站长反馈，使用模拟反馈
            if manager_feedback is None:
                logger.info("等待站长确认...")
                # 在实际项目中，这里会等待真实的站长反馈
                # 这里使用模拟反馈（80%概率同意）
                import random
                manager_feedback = random.random() < 0.8
                logger.info(f"收到站长反馈: {'同意' if manager_feedback else '拒绝'}")
            
            decision_request = DecisionRequest(
                site_id=site_id,
                prediction_result=prediction_result,
                manager_feedback=manager_feedback,
                notes="系统自动决策"
            )
            
            decision_result = self.decision_service.make_decision(decision_request)
            
            logger.info(f"决策结果:")
            logger.info(f"  是否启动召回: {decision_result.accepted}")
            logger.info(f"  下一步: {decision_result.next_step}")
            logger.info(f"  原因: {decision_result.reason}")
            
            # 如果决策不通过，结束流程
            if not decision_result.accepted:
                self._update_workflow_status("完成", 100.0, "success")
                return {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "result": "召回被拒绝",
                    "prediction": prediction_result.dict(),
                    "decision": decision_result.dict(),
                    "message": decision_result.reason
                }
            
            # 阶段3: 骑手筛选
            logger.info("\n" + "=" * 50)
            logger.info("阶段3: 候选骑手筛选")
            logger.info("=" * 50)
            
            self._update_workflow_status("骑手筛选", 60.0)
            
            # 根据缺口比例确定紧急程度
            if prediction_result.gap_ratio > 0.3:
                urgency = "high"
            elif prediction_result.gap_ratio > 0.15:
                urgency = "medium"
            else:
                urgency = "low"
                
            candidates = self.profiler_service.select_candidates(
                site_id=site_id,
                target_date=target_date,
                required_riders=prediction_result.required_riders,
                urgency=urgency
            )
            
            logger.info(f"筛选完成:")
            logger.info(f"  找到候选人: {len(candidates)}人")
            logger.info(f"  紧急程度: {urgency}")
            
            if candidates:
                logger.info("  前3名候选人:")
                for i, candidate in enumerate(candidates[:3], 1):
                    logger.info(f"    {i}. {candidate.name} (得分: {candidate.score:.1f}, 距离: {candidate.distance:.1f}km)")
            
            # 阶段4: 模拟召回执行
            logger.info("\n" + "=" * 50)
            logger.info("阶段4: 召回执行 (模拟)")
            logger.info("=" * 50)
            
            self._update_workflow_status("召回执行", 80.0)
            
            # 模拟召回结果
            recall_results = self._simulate_recall_execution(candidates)
            
            logger.info(f"召回执行完成:")
            logger.info(f"  拨打总数: {recall_results['total_calls']}")
            logger.info(f"  接通数量: {recall_results['connected_calls']}")
            logger.info(f"  同意数量: {recall_results['agreed_calls']}")
            logger.info(f"  成功率: {recall_results['success_rate']:.1%}")
            
            # 阶段5: 完成
            self._update_workflow_status("完成", 100.0, "success")
            
            logger.info("\n" + "=" * 50)
            logger.info("工作流执行完成")
            logger.info("=" * 50)
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": "召回成功",
                "prediction": prediction_result.dict(),
                "decision": decision_result.dict(),
                "candidates": [c.dict() for c in candidates],
                "recall_results": recall_results,
                "message": f"成功召回 {recall_results['agreed_calls']} 名骑手"
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            self._update_workflow_status("错误", self.workflow_status.progress, "error", str(e))
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "result": "执行失败",
                "error": str(e),
                "message": f"工作流执行失败: {str(e)}"
            }
    
    def _update_workflow_status(self, stage: str, progress: float, status: str = "running", error: str = None):
        """更新工作流状态"""
        if self.workflow_status:
            if stage not in self.workflow_status.completed_stages and stage != self.workflow_status.current_stage:
                self.workflow_status.completed_stages.append(self.workflow_status.current_stage)
            
            self.workflow_status.current_stage = stage
            self.workflow_status.progress = progress
            self.workflow_status.status = status
            if error:
                self.workflow_status.error_message = error
    
    def _simulate_recall_execution(self, candidates: List) -> Dict[str, Any]:
        """模拟召回执行过程"""
        import random
        
        total_calls = len(candidates)
        connected_calls = 0
        agreed_calls = 0
        
        for candidate in candidates:
            # 模拟拨打结果
            # 接通率约80%
            if random.random() < 0.8:
                connected_calls += 1
                
                # 同意率根据候选人得分决定
                agree_probability = min(0.9, candidate.score / 100)
                if random.random() < agree_probability:
                    agreed_calls += 1
        
        success_rate = agreed_calls / total_calls if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "connected_calls": connected_calls,
            "agreed_calls": agreed_calls,
            "success_rate": success_rate,
            "execution_time": datetime.now().isoformat()
        }
    
    def get_workflow_status(self) -> WorkflowStatus:
        """获取当前工作流状态"""
        return self.workflow_status

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="即时物流骑手智能召回系统")
    parser.add_argument("--site-id", required=True, help="站点ID")
    parser.add_argument("--date", required=True, help="目标日期 (YYYY-MM-DD)")
    parser.add_argument("--manager-feedback", type=bool, default=None, help="站长反馈 (True/False)")
    parser.add_argument("--demo", action="store_true", help="运行演示模式")
    
    args = parser.parse_args()
    
    # 创建工作流实例
    workflow = LogisticsWorkflow()
    
    if args.demo:
        # 演示模式：运行多个场景
        demo_scenarios = [
            {"site_id": "site_001", "date": "2024-02-14", "feedback": True},   # 情人节，同意召回
            {"site_id": "site_002", "date": "2024-05-01", "feedback": False},  # 劳动节，拒绝召回
            {"site_id": "site_003", "date": "2024-06-15", "feedback": None},   # 普通日期，自动决策
        ]
        
        print("=" * 60)
        print("即时物流骑手智能召回系统 - 演示模式")
        print("=" * 60)
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print(f"\n演示场景 {i}: 站点 {scenario['site_id']}, 日期 {scenario['date']}")
            print("-" * 40)
            
            result = asyncio.run(workflow.run_complete_workflow(
                site_id=scenario["site_id"],
                target_date=scenario["date"],
                manager_feedback=scenario["feedback"]
            ))
            
            print(f"结果: {result['result']}")
            print(f"消息: {result['message']}")
            
            if i < len(demo_scenarios):
                input("\n按回车键继续下一个场景...")
    else:
        # 正常模式：运行指定场景
        print("=" * 60)
        print("即时物流骑手智能召回系统")
        print("=" * 60)
        
        result = asyncio.run(workflow.run_complete_workflow(
            site_id=args.site_id,
            target_date=args.date,
            manager_feedback=args.manager_feedback
        ))
        
        print("\n最终结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 