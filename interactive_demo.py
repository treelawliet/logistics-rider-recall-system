#!/usr/bin/env python3
"""
即时物流骑手智能召回系统 - 交互式演示
支持用户自定义参数的演示程序
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from simple_demo import LogisticsWorkflow, PredictionResult, RiderCandidate, CallResult

def print_banner():
    """打印欢迎横幅"""
    print("=" * 70)
    print("🚚 即时物流骑手智能召回系统 - 交互式演示")
    print("=" * 70)
    print("欢迎使用多Agent协同调度系统！")
    print("这个系统可以帮助你智能预测运力需求，自动召回骑手。")
    print()

def get_user_input():
    """获取用户输入的参数"""
    print("📝 请设置演示参数:")
    print()
    
    # 选择站点
    sites = {
        "1": ("site_001", "北京朝阳站"),
        "2": ("site_002", "上海浦东站"), 
        "3": ("site_003", "广州天河站"),
        "4": ("site_004", "深圳南山站"),
        "5": ("site_005", "杭州西湖站")
    }
    
    print("🏢 选择站点:")
    for key, (site_id, name) in sites.items():
        print(f"  {key}. {name} ({site_id})")
    
    while True:
        choice = input("请输入站点编号 (1-5): ").strip()
        if choice in sites:
            site_id, site_name = sites[choice]
            break
        print("❌ 无效选择，请重新输入")
    
    print(f"✅ 已选择: {site_name}")
    print()
    
    # 选择日期
    print("📅 选择目标日期:")
    dates = []
    for i in range(1, 8):
        date = datetime.now() + timedelta(days=i)
        dates.append(date)
        day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        print(f"  {i}. {date.strftime('%Y-%m-%d')} ({day_name})")
    
    while True:
        try:
            choice = int(input("请输入日期编号 (1-7): ").strip())
            if 1 <= choice <= 7:
                target_date = dates[choice-1].strftime('%Y-%m-%d')
                break
            print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入数字")
    
    print(f"✅ 已选择: {target_date}")
    print()
    
    # 选择场景
    print("🎭 选择演示场景:")
    scenarios = {
        "1": ("normal", "正常场景 - 轻微缺口"),
        "2": ("busy", "繁忙场景 - 中等缺口"),
        "3": ("crisis", "危机场景 - 严重缺口"),
        "4": ("sufficient", "充足场景 - 无需召回"),
        "5": ("random", "随机场景 - 系统随机生成")
    }
    
    for key, (scenario_id, description) in scenarios.items():
        print(f"  {key}. {description}")
    
    while True:
        choice = input("请输入场景编号 (1-5): ").strip()
        if choice in scenarios:
            scenario_id, scenario_name = scenarios[choice]
            break
        print("❌ 无效选择，请重新输入")
    
    print(f"✅ 已选择: {scenario_name}")
    print()
    
    return site_id, site_name, target_date, scenario_id

def create_scenario_workflow(scenario_id: str) -> LogisticsWorkflow:
    """根据场景创建定制的工作流"""
    workflow = LogisticsWorkflow()
    
    # 根据场景调整预测逻辑
    original_predict = workflow.prediction_agent.predict_demand
    
    def custom_predict(site_id: str, target_date: str) -> PredictionResult:
        print(f"🔮 {workflow.prediction_agent.name}正在分析站点 {site_id} 在 {target_date} 的运力需求...")
        time.sleep(1)
        
        if scenario_id == "normal":
            # 正常场景：轻微缺口
            predicted_orders = random.randint(100, 120)
            current_capacity = random.randint(85, 95)
        elif scenario_id == "busy":
            # 繁忙场景：中等缺口
            predicted_orders = random.randint(130, 160)
            current_capacity = random.randint(80, 100)
        elif scenario_id == "crisis":
            # 危机场景：严重缺口
            predicted_orders = random.randint(180, 220)
            current_capacity = random.randint(70, 90)
        elif scenario_id == "sufficient":
            # 充足场景：无需召回
            predicted_orders = random.randint(80, 100)
            current_capacity = random.randint(100, 120)
        else:
            # 随机场景
            predicted_orders = random.randint(80, 200)
            current_capacity = random.randint(60, 120)
        
        gap_ratio = max(0, (predicted_orders - current_capacity) / predicted_orders)
        has_gap = gap_ratio > 0.1
        required_riders = max(0, int((predicted_orders - current_capacity) * 0.8))
        confidence = random.uniform(0.75, 0.95)
        
        suggestion = f"建议提前{random.randint(2, 4)}小时开始召回" if has_gap else "运力充足，无需召回"
        
        result = PredictionResult(
            site_id=site_id,
            target_date=target_date,
            predicted_orders=predicted_orders,
            current_capacity=current_capacity,
            gap_ratio=gap_ratio,
            has_gap=has_gap,
            required_riders=required_riders,
            confidence=confidence,
            suggestion=suggestion
        )
        
        print(f"✅ 预测完成: 预计订单{predicted_orders}单，当前运力{current_capacity}人")
        print(f"   缺口比例: {gap_ratio:.1%}, 需要召回: {required_riders}人")
        
        return result
    
    workflow.prediction_agent.predict_demand = custom_predict
    return workflow

def show_detailed_analysis(result: Dict[str, Any]):
    """显示详细的分析结果"""
    print("\n" + "=" * 60)
    print("📊 详细分析报告")
    print("=" * 60)
    
    prediction = result.get('prediction', {})
    analysis = result.get('analysis', {})
    
    print(f"📈 预测分析:")
    print(f"   站点: {prediction.get('site_id', 'N/A')}")
    print(f"   日期: {prediction.get('target_date', 'N/A')}")
    print(f"   预计订单: {prediction.get('predicted_orders', 0)}单")
    print(f"   当前运力: {prediction.get('current_capacity', 0)}人")
    print(f"   缺口比例: {prediction.get('gap_ratio', 0):.1%}")
    print(f"   预测置信度: {prediction.get('confidence', 0):.1%}")
    print()
    
    if analysis:
        print(f"📞 召回执行:")
        print(f"   拨打总数: {analysis.get('total_calls', 0)}次")
        print(f"   接通率: {analysis.get('connection_rate', 0):.1%}")
        print(f"   成功率: {analysis.get('success_rate', 0):.1%}")
        print(f"   同意率: {analysis.get('agreement_rate', 0):.1%}")
        print(f"   目标完成: {'✅ 是' if analysis.get('target_met', False) else '❌ 否'}")
        print(f"   覆盖率: {analysis.get('coverage_rate', 0):.1%}")
        print()
    
    # 给出改进建议
    print("💡 改进建议:")
    if analysis:
        success_rate = analysis.get('success_rate', 0)
        connection_rate = analysis.get('connection_rate', 0)
        
        if success_rate < 0.5:
            print("   • 成功率偏低，建议优化骑手筛选标准")
            print("   • 考虑提高召回激励或改善工作条件")
        
        if connection_rate < 0.8:
            print("   • 接通率偏低，建议优化拨打时间段")
            print("   • 考虑使用多种联系方式（短信、微信等）")
        
        if not analysis.get('target_met', False):
            print("   • 未达到召回目标，建议扩大候选人范围")
            print("   • 考虑分批次召回或启用备用方案")
    
    print("   • 建立骑手反馈机制，了解拒绝原因")
    print("   • 定期更新骑手画像和偏好设置")

def main():
    """主函数"""
    print_banner()
    
    while True:
        # 获取用户输入
        site_id, site_name, target_date, scenario_id = get_user_input()
        
        # 创建定制工作流
        workflow = create_scenario_workflow(scenario_id)
        
        # 确认开始
        print("🚀 准备开始演示...")
        input("按回车键开始执行工作流...")
        print()
        
        # 运行工作流
        result = workflow.run_complete_workflow(site_id, target_date)
        
        # 显示详细分析
        show_detailed_analysis(result)
        
        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'demo_result_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细结果已保存到 {filename}")
        
        # 询问是否继续
        print("\n" + "=" * 60)
        while True:
            choice = input("是否继续演示其他场景？(y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                print("\n" * 2)
                break
            elif choice in ['n', 'no', '否']:
                print("\n🎉 感谢使用即时物流骑手智能召回系统演示！")
                return
            else:
                print("❌ 请输入 y 或 n")

if __name__ == "__main__":
    main() 