"""
即时物流骑手智能召回系统 - Web界面
基于Streamlit的可视化界面
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from typing import Dict, Any

from main import LogisticsWorkflow
from agents.prediction_agent import PredictionService, PredictionRequest
from agents.decision_agent import DecisionService
from agents.rider_profiler_agent import RiderProfilerService
from config.settings import settings

# 页面配置
st.set_page_config(
    page_title="即时物流骑手智能召回系统",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """初始化会话状态"""
    if 'workflow_result' not in st.session_state:
        st.session_state.workflow_result = None
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []

def create_sidebar():
    """创建侧边栏"""
    st.sidebar.title("🚚 系统控制台")
    
    # 系统状态
    st.sidebar.subheader("📊 系统状态")
    st.sidebar.success("✅ 系统运行正常")
    st.sidebar.info(f"📅 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 快速操作
    st.sidebar.subheader("⚡ 快速操作")
    
    if st.sidebar.button("🔄 刷新页面"):
        st.experimental_rerun()
    
    if st.sidebar.button("🗑️ 清除历史"):
        st.session_state.workflow_history = []
        st.session_state.workflow_result = None
        st.success("历史记录已清除")
    
    # 系统配置
    st.sidebar.subheader("⚙️ 系统配置")
    st.sidebar.text(f"预测阈值: {settings.PREDICTION_THRESHOLD:.1%}")
    st.sidebar.text(f"目标成功率: {settings.SUCCESS_RATE_TARGET:.1%}")
    st.sidebar.text(f"最大召回数: {settings.RECALL_BATCH_SIZE}")

def create_prediction_section():
    """创建预测分析区域"""
    st.subheader("🔮 运力缺口预测")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        site_id = st.selectbox(
            "选择站点",
            ["site_001", "site_002", "site_003", "site_004", "site_005"],
            help="选择要分析的站点"
        )
    
    with col2:
        target_date = st.date_input(
            "目标日期",
            value=date.today() + timedelta(days=3),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=30),
            help="选择需要预测的日期"
        )
    
    with col3:
        include_weather = st.checkbox(
            "包含天气因素",
            value=True,
            help="是否在预测中考虑天气影响"
        )
    
    if st.button("🚀 开始预测", type="primary"):
        with st.spinner("正在分析运力需求..."):
            try:
                # 创建预测服务
                prediction_service = PredictionService()
                
                # 执行预测
                request = PredictionRequest(
                    site_id=site_id,
                    target_date=target_date.strftime('%Y-%m-%d'),
                    include_weather=include_weather
                )
                
                result = prediction_service.predict_demand(request)
                
                # 显示预测结果
                st.success("✅ 预测分析完成")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "预测订单量",
                        f"{result.predicted_orders}",
                        delta=f"+{result.predicted_orders - 100}"
                    )
                
                with col2:
                    st.metric(
                        "当前运力",
                        f"{result.current_capacity}人",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "缺口比例",
                        f"{result.gap_ratio:.1%}",
                        delta=f"{'⚠️' if result.has_gap else '✅'}"
                    )
                
                with col4:
                    st.metric(
                        "预测置信度",
                        f"{result.confidence:.1%}",
                        delta=None
                    )
                
                # 显示建议
                if result.has_gap:
                    st.warning(f"⚠️ 检测到运力缺口，建议召回 {result.required_riders} 名骑手")
                    st.info(f"💡 {result.suggestion}")
                else:
                    st.success("✅ 运力充足，无需召回")
                
                # 保存结果到会话状态
                st.session_state.prediction_result = result
                
            except Exception as e:
                st.error(f"❌ 预测失败: {str(e)}")

def create_workflow_section():
    """创建完整工作流区域"""
    st.subheader("🔄 完整召回工作流")
    
    col1, col2 = st.columns(2)
    
    with col1:
        site_id = st.selectbox(
            "站点ID",
            ["site_001", "site_002", "site_003", "site_004", "site_005"],
            key="workflow_site"
        )
        
        target_date = st.date_input(
            "目标日期",
            value=date.today() + timedelta(days=3),
            min_value=date.today(),
            max_value=date.today() + timedelta(days=30),
            key="workflow_date"
        )
    
    with col2:
        manager_feedback = st.selectbox(
            "站长反馈",
            ["自动决策", "同意召回", "拒绝召回"],
            help="选择站长对召回的反馈"
        )
        
        # 转换反馈为布尔值
        feedback_map = {
            "自动决策": None,
            "同意召回": True,
            "拒绝召回": False
        }
        feedback_value = feedback_map[manager_feedback]
    
    if st.button("🚀 启动完整工作流", type="primary", key="start_workflow"):
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 创建工作流实例
            workflow = LogisticsWorkflow()
            
            # 执行工作流
            status_text.text("正在执行工作流...")
            result = asyncio.run(workflow.run_complete_workflow(
                site_id=site_id,
                target_date=target_date.strftime('%Y-%m-%d'),
                manager_feedback=feedback_value
            ))
            
            progress_bar.progress(100)
            status_text.text("工作流执行完成")
            
            # 保存结果
            st.session_state.workflow_result = result
            st.session_state.workflow_history.append({
                "timestamp": datetime.now(),
                "site_id": site_id,
                "target_date": target_date.strftime('%Y-%m-%d'),
                "result": result
            })
            
            # 显示结果
            display_workflow_result(result)
            
        except Exception as e:
            st.error(f"❌ 工作流执行失败: {str(e)}")
            progress_bar.progress(0)
            status_text.text("执行失败")

def display_workflow_result(result: Dict[str, Any]):
    """显示工作流执行结果"""
    if not result:
        return
    
    st.subheader("📋 执行结果")
    
    # 结果状态
    if result["status"] == "completed":
        if result["result"] == "召回成功":
            st.success(f"✅ {result['message']}")
        elif result["result"] == "无需召回":
            st.info(f"ℹ️ {result['message']}")
        else:
            st.warning(f"⚠️ {result['message']}")
    else:
        st.error(f"❌ {result['message']}")
    
    # 详细信息
    if "prediction" in result:
        st.subheader("🔮 预测结果")
        pred = result["prediction"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("预测订单", pred["predicted_orders"])
        with col2:
            st.metric("当前运力", pred["current_capacity"])
        with col3:
            st.metric("缺口比例", f"{pred['gap_ratio']:.1%}")
    
    # 候选骑手信息
    if "candidates" in result and result["candidates"]:
        st.subheader("👥 候选骑手")
        
        candidates_df = pd.DataFrame(result["candidates"])
        st.dataframe(
            candidates_df[["name", "score", "distance", "priority"]],
            column_config={
                "name": "姓名",
                "score": st.column_config.NumberColumn("得分", format="%.1f"),
                "distance": st.column_config.NumberColumn("距离(km)", format="%.1f"),
                "priority": "优先级"
            }
        )
    
    # 召回结果
    if "recall_results" in result:
        st.subheader("📞 召回结果")
        recall = result["recall_results"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("拨打总数", recall["total_calls"])
        with col2:
            st.metric("接通数量", recall["connected_calls"])
        with col3:
            st.metric("同意数量", recall["agreed_calls"])
        with col4:
            st.metric("成功率", f"{recall['success_rate']:.1%}")

def create_analytics_section():
    """创建分析报告区域"""
    st.subheader("📊 分析报告")
    
    if not st.session_state.workflow_history:
        st.info("暂无历史数据，请先执行工作流")
        return
    
    # 历史数据统计
    history = st.session_state.workflow_history
    
    # 成功率趋势
    success_data = []
    for record in history:
        if "recall_results" in record["result"]:
            success_data.append({
                "日期": record["timestamp"].strftime('%m-%d %H:%M'),
                "站点": record["site_id"],
                "成功率": record["result"]["recall_results"]["success_rate"]
            })
    
    if success_data:
        df = pd.DataFrame(success_data)
        
        # 成功率趋势图
        fig = px.line(
            df, 
            x="日期", 
            y="成功率", 
            color="站点",
            title="召回成功率趋势",
            markers=True
        )
        fig.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig, use_container_width=True)
        
        # 站点对比
        avg_by_site = df.groupby("站点")["成功率"].mean().reset_index()
        fig2 = px.bar(
            avg_by_site,
            x="站点",
            y="成功率",
            title="各站点平均成功率对比"
        )
        fig2.update_layout(yaxis_tickformat='.1%')
        st.plotly_chart(fig2, use_container_width=True)

def create_demo_section():
    """创建演示区域"""
    st.subheader("🎮 演示模式")
    
    st.info("演示模式将运行预设的多个场景，展示系统的完整功能")
    
    demo_scenarios = [
        {"name": "情人节高峰", "site_id": "site_001", "date": "2024-02-14", "description": "节假日高峰期，预计订单激增"},
        {"name": "劳动节假期", "site_id": "site_002", "date": "2024-05-01", "description": "法定节假日，需要提前准备"},
        {"name": "普通工作日", "site_id": "site_003", "date": "2024-06-15", "description": "正常工作日，测试基础功能"},
    ]
    
    selected_scenario = st.selectbox(
        "选择演示场景",
        options=range(len(demo_scenarios)),
        format_func=lambda x: f"{demo_scenarios[x]['name']} - {demo_scenarios[x]['description']}"
    )
    
    scenario = demo_scenarios[selected_scenario]
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**站点**: {scenario['site_id']}")
        st.write(f"**日期**: {scenario['date']}")
    with col2:
        st.write(f"**场景**: {scenario['name']}")
        st.write(f"**描述**: {scenario['description']}")
    
    if st.button("🎯 运行演示", type="primary"):
        with st.spinner("正在运行演示场景..."):
            try:
                workflow = LogisticsWorkflow()
                result = asyncio.run(workflow.run_complete_workflow(
                    site_id=scenario["site_id"],
                    target_date=scenario["date"],
                    manager_feedback=None  # 自动决策
                ))
                
                st.success("✅ 演示完成")
                display_workflow_result(result)
                
            except Exception as e:
                st.error(f"❌ 演示失败: {str(e)}")

def main():
    """主函数"""
    # 初始化
    init_session_state()
    
    # 页面标题
    st.markdown('<h1 class="main-header">🚚 即时物流骑手智能召回系统</h1>', unsafe_allow_html=True)
    
    # 侧边栏
    create_sidebar()
    
    # 主要内容区域
    tab1, tab2, tab3, tab4 = st.tabs(["🔮 预测分析", "🔄 完整工作流", "📊 分析报告", "🎮 演示模式"])
    
    with tab1:
        create_prediction_section()
    
    with tab2:
        create_workflow_section()
    
    with tab3:
        create_analytics_section()
    
    with tab4:
        create_demo_section()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"即时物流骑手智能召回系统 v{settings.VERSION} | "
        f"基于 CrewAI 多Agent框架构建"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 