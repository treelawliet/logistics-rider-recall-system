"""
骑手画像Agent
负责生成符合召回需求的骑手画像，并筛选最优候选骑手名单
"""

from crewai import Agent, Task, Crew
from crewai_tools import BaseTool
from typing import Dict, Any, List
import json
import numpy as np
from datetime import datetime, timedelta
from models.schemas import RiderProfile, RiderCandidate, RiderStatus
from config.settings import settings, BUSINESS_RULES

class RiderDataTool(BaseTool):
    """骑手数据获取工具"""
    name: str = "rider_data_tool"
    description: str = "获取站点的骑手基础信息和历史表现数据"
    
    def _run(self, site_id: str, active_only: bool = True) -> Dict[str, Any]:
        """
        获取骑手数据（模拟实现）
        在实际项目中，这里会查询真实的骑手数据库
        """
        import random
        
        # 生成模拟骑手数据
        riders = []
        rider_count = random.randint(30, 50)  # 每个站点30-50个骑手
        
        for i in range(rider_count):
            rider_id = f"rider_{site_id}_{i:03d}"
            
            # 模拟骑手状态分布
            status_weights = [0.6, 0.2, 0.15, 0.05]  # active, inactive, busy, offline
            status = np.random.choice(list(RiderStatus), p=status_weights)
            
            if active_only and status != RiderStatus.ACTIVE:
                continue
                
            rider = {
                "rider_id": rider_id,
                "name": f"骑手{i:03d}",
                "phone": f"138{random.randint(10000000, 99999999)}",
                "site_id": site_id,
                "status": status.value,
                
                # 历史表现指标（模拟真实分布）
                "acceptance_rate": max(0.3, min(1.0, np.random.normal(0.8, 0.15))),
                "avg_response_time": max(30, int(np.random.normal(120, 40))),  # 秒
                "completion_rate": max(0.7, min(1.0, np.random.normal(0.92, 0.08))),
                "active_days": random.randint(10, 300),
                
                # 位置信息（模拟站点周边分布）
                "current_latitude": 39.9042 + np.random.normal(0, 0.01),  # 北京附近
                "current_longitude": 116.4074 + np.random.normal(0, 0.01),
                "last_active_time": (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                
                # 额外特征
                "avg_orders_per_day": random.randint(15, 40),
                "peak_hour_availability": random.choice([True, False]),
                "weekend_availability": random.choice([True, False]),
                "holiday_experience": random.randint(0, 10),  # 节假日工作经验
                "distance_to_site": random.uniform(0.5, 8.0),  # 距离站点距离
            }
            
            riders.append(rider)
            
        return {
            "site_id": site_id,
            "total_riders": len(riders),
            "riders": riders,
            "last_updated": datetime.now().isoformat()
        }

class ProfileGeneratorTool(BaseTool):
    """画像生成工具"""
    name: str = "profile_generator_tool"
    description: str = "基于业务需求生成理想骑手画像"
    
    def _run(self, target_date: str, required_count: int, urgency_level: str = "medium") -> Dict[str, Any]:
        """
        生成骑手画像（基于业务规则）
        """
        # 基础画像要求
        base_profile = {
            "min_acceptance_rate": settings.MIN_ACCEPTANCE_RATE,
            "max_response_time": settings.MIN_RESPONSE_TIME * 2,  # 最大响应时间
            "min_completion_rate": 0.85,
            "min_active_days": settings.ACTIVE_DAYS_THRESHOLD,
        }
        
        # 根据紧急程度调整要求
        if urgency_level == "high":
            # 高紧急度：降低要求，扩大候选范围
            profile = {
                "min_acceptance_rate": max(0.5, base_profile["min_acceptance_rate"] - 0.2),
                "max_response_time": base_profile["max_response_time"] * 1.5,
                "min_completion_rate": max(0.7, base_profile["min_completion_rate"] - 0.1),
                "min_active_days": max(3, base_profile["min_active_days"] - 3),
                "max_distance": 8.0,  # 扩大距离范围
                "priority_factors": ["availability", "distance", "experience"]
            }
        elif urgency_level == "low":
            # 低紧急度：提高要求，精选候选人
            profile = {
                "min_acceptance_rate": min(0.95, base_profile["min_acceptance_rate"] + 0.1),
                "max_response_time": base_profile["max_response_time"] * 0.8,
                "min_completion_rate": min(0.98, base_profile["min_completion_rate"] + 0.05),
                "min_active_days": base_profile["min_active_days"] + 5,
                "max_distance": 3.0,  # 限制距离范围
                "priority_factors": ["performance", "reliability", "experience"]
            }
        else:
            # 中等紧急度：使用基础要求
            profile = {
                **base_profile,
                "max_distance": 5.0,
                "priority_factors": ["balance", "availability", "performance"]
            }
        
        # 节假日特殊要求
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        is_weekend = target_dt.weekday() >= 5
        is_holiday = target_dt.strftime('%m-%d') in ['01-01', '02-14', '05-01', '10-01']
        
        if is_weekend or is_holiday:
            profile["prefer_weekend_available"] = True
            profile["prefer_holiday_experience"] = True
            profile["min_holiday_experience"] = 2
        
        profile.update({
            "target_date": target_date,
            "required_count": required_count,
            "urgency_level": urgency_level,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "generated_at": datetime.now().isoformat()
        })
        
        return profile

class CandidateSelectorTool(BaseTool):
    """候选人筛选工具"""
    name: str = "candidate_selector_tool"
    description: str = "基于画像要求筛选和排序候选骑手"
    
    def _run(self, riders_data: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        筛选和排序候选骑手
        """
        riders = riders_data.get("riders", [])
        candidates = []
        
        for rider in riders:
            # 基础条件筛选
            if not self._meets_basic_requirements(rider, profile):
                continue
                
            # 计算匹配得分
            score = self._calculate_match_score(rider, profile)
            
            # 创建候选人对象
            candidate = {
                "rider_id": rider["rider_id"],
                "name": rider["name"],
                "phone": rider["phone"],
                "score": score,
                "distance": rider["distance_to_site"],
                "availability": rider["status"] == "active",
                "priority": self._determine_priority(score),
                
                # 详细信息
                "acceptance_rate": rider["acceptance_rate"],
                "response_time": rider["avg_response_time"],
                "completion_rate": rider["completion_rate"],
                "active_days": rider["active_days"],
                "holiday_experience": rider.get("holiday_experience", 0)
            }
            
            candidates.append(candidate)
        
        # 按得分排序
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # 限制候选人数量
        max_candidates = BUSINESS_RULES["rider_selection"]["max_candidates"]
        required_count = profile.get("required_count", 10)
        
        # 取所需数量的1.5倍作为候选池，确保有备选
        target_count = min(max_candidates, int(required_count * 1.5))
        selected_candidates = candidates[:target_count]
        
        return {
            "total_evaluated": len(riders),
            "total_qualified": len(candidates),
            "selected_count": len(selected_candidates),
            "candidates": selected_candidates,
            "selection_criteria": profile,
            "avg_score": np.mean([c["score"] for c in selected_candidates]) if selected_candidates else 0,
            "selected_at": datetime.now().isoformat()
        }
    
    def _meets_basic_requirements(self, rider: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """检查是否满足基础要求"""
        checks = [
            rider["acceptance_rate"] >= profile["min_acceptance_rate"],
            rider["avg_response_time"] <= profile["max_response_time"],
            rider["completion_rate"] >= profile["min_completion_rate"],
            rider["active_days"] >= profile["min_active_days"],
            rider["distance_to_site"] <= profile["max_distance"],
            rider["status"] == "active"  # 必须是活跃状态
        ]
        
        return all(checks)
    
    def _calculate_match_score(self, rider: Dict[str, Any], profile: Dict[str, Any]) -> float:
        """计算匹配得分"""
        score = 0.0
        
        # 接单率得分 (30%)
        acceptance_score = min(1.0, rider["acceptance_rate"] / 0.9) * 30
        score += acceptance_score
        
        # 响应时间得分 (20%)
        response_score = max(0, (300 - rider["avg_response_time"]) / 300) * 20
        score += response_score
        
        # 完成率得分 (25%)
        completion_score = min(1.0, rider["completion_rate"] / 0.95) * 25
        score += completion_score
        
        # 距离得分 (15%)
        distance_score = max(0, (5.0 - rider["distance_to_site"]) / 5.0) * 15
        score += distance_score
        
        # 经验得分 (10%)
        experience_score = min(1.0, rider["active_days"] / 100) * 10
        score += experience_score
        
        # 节假日经验加分
        if profile.get("is_holiday") or profile.get("is_weekend"):
            holiday_bonus = min(5, rider.get("holiday_experience", 0))
            score += holiday_bonus
            
        # 可用性加分
        if rider.get("peak_hour_availability"):
            score += 3
        if rider.get("weekend_availability") and profile.get("is_weekend"):
            score += 3
            
        return round(score, 2)
    
    def _determine_priority(self, score: float) -> str:
        """根据得分确定优先级"""
        if score >= 80:
            return "high"
        elif score >= 60:
            return "medium"
        else:
            return "low"

def create_rider_profiler_agent() -> Agent:
    """创建骑手画像Agent"""
    
    return Agent(
        role="骑手画像专家",
        goal="生成精准的骑手画像，筛选出最适合召回的候选骑手名单",
        backstory="""
        你是一位经验丰富的人力资源分析师，专门负责骑手画像分析和候选人筛选。
        你深度理解即时物流业务特点，能够根据不同场景（节假日、紧急情况等）
        制定合适的筛选标准，确保召回的骑手既能满足业务需求，又有较高的响应意愿。
        你的筛选结果直接影响召回成功率和运营效率。
        """,
        tools=[
            RiderDataTool(),
            ProfileGeneratorTool(),
            CandidateSelectorTool()
        ],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

def create_profiler_task(agent: Agent, site_id: str, target_date: str, required_riders: int, urgency: str = "medium") -> Task:
    """创建画像筛选任务"""
    
    return Task(
        description=f"""
        为站点 {site_id} 筛选 {target_date} 的召回候选骑手：
        
        1. 获取站点所有活跃骑手的基础信息和历史表现数据
        2. 根据目标日期特点（是否节假日/周末）和紧急程度生成理想骑手画像
        3. 基于画像要求筛选符合条件的候选骑手
        4. 计算每个候选人的匹配得分并排序
        5. 返回排序后的候选骑手名单
        
        筛选要求：
        - 需要骑手数量: {required_riders}人
        - 紧急程度: {urgency}
        - 目标日期: {target_date}
        
        筛选标准：
        - 最低接单率: {settings.MIN_ACCEPTANCE_RATE:.0%}
        - 最大响应时间: {settings.MIN_RESPONSE_TIME * 2}秒
        - 最低活跃天数: {settings.ACTIVE_DAYS_THRESHOLD}天
        - 最大距离: 5公里
        
        请确保返回结果包含：
        - 候选骑手列表（按得分排序）
        - 每个候选人的详细信息和得分
        - 筛选统计信息
        """,
        agent=agent,
        expected_output="""
        返回JSON格式的筛选结果，包含以下字段：
        {
            "total_evaluated": "评估的骑手总数",
            "total_qualified": "符合条件的骑手数",
            "selected_count": "最终选择的候选人数",
            "candidates": [
                {
                    "rider_id": "骑手ID",
                    "name": "姓名",
                    "phone": "电话",
                    "score": "匹配得分",
                    "distance": "距离",
                    "priority": "优先级",
                    "acceptance_rate": "接单率",
                    "response_time": "响应时间",
                    "completion_rate": "完成率"
                }
            ],
            "avg_score": "平均得分"
        }
        """
    )

class RiderProfilerService:
    """骑手画像服务类"""
    
    def __init__(self):
        self.agent = create_rider_profiler_agent()
        
    def select_candidates(self, site_id: str, target_date: str, required_riders: int, urgency: str = "medium") -> List[RiderCandidate]:
        """
        筛选候选骑手
        
        Args:
            site_id: 站点ID
            target_date: 目标日期
            required_riders: 需要的骑手数量
            urgency: 紧急程度 (high/medium/low)
            
        Returns:
            List[RiderCandidate]: 候选骑手列表
        """
        try:
            # 创建筛选任务
            task = create_profiler_task(self.agent, site_id, target_date, required_riders, urgency)
            
            # 创建Crew并执行
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                verbose=True
            )
            
            # 执行筛选
            result = crew.kickoff()
            
            # 解析结果
            if isinstance(result, str):
                try:
                    result_data = json.loads(result)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，返回模拟数据
                    result_data = self._generate_mock_candidates(site_id, required_riders)
            else:
                result_data = result
                
            # 转换为RiderCandidate对象列表
            candidates = []
            for candidate_data in result_data.get("candidates", []):
                candidate = RiderCandidate(
                    rider_id=candidate_data.get("rider_id", ""),
                    name=candidate_data.get("name", ""),
                    phone=candidate_data.get("phone", ""),
                    score=candidate_data.get("score", 0.0),
                    distance=candidate_data.get("distance", 0.0),
                    availability=candidate_data.get("availability", True),
                    priority=candidate_data.get("priority", "medium")
                )
                candidates.append(candidate)
                
            return candidates
            
        except Exception as e:
            # 返回模拟候选人数据
            return self._generate_mock_candidates(site_id, required_riders)
    
    def _generate_mock_candidates(self, site_id: str, required_riders: int) -> List[RiderCandidate]:
        """生成模拟候选人数据"""
        import random
        
        candidates = []
        for i in range(min(required_riders * 2, 20)):  # 生成2倍数量的候选人
            candidate = RiderCandidate(
                rider_id=f"rider_{site_id}_{i:03d}",
                name=f"骑手{i:03d}",
                phone=f"138{random.randint(10000000, 99999999)}",
                score=random.uniform(60, 95),
                distance=random.uniform(0.5, 5.0),
                availability=True,
                priority=random.choice(["high", "medium", "low"])
            )
            candidates.append(candidate)
            
        # 按得分排序
        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates

# 使用示例
if __name__ == "__main__":
    # 创建骑手画像服务
    service = RiderProfilerService()
    
    # 筛选候选骑手
    candidates = service.select_candidates(
        site_id="site_001",
        target_date="2024-02-14",  # 情人节
        required_riders=8,
        urgency="high"
    )
    
    print(f"筛选结果: 共找到 {len(candidates)} 个候选骑手")
    print("\n前5名候选人:")
    for i, candidate in enumerate(candidates[:5], 1):
        print(f"{i}. {candidate.name} (ID: {candidate.rider_id})")
        print(f"   得分: {candidate.score:.1f}, 距离: {candidate.distance:.1f}km, 优先级: {candidate.priority}")
        print(f"   电话: {candidate.phone}")
        print() 