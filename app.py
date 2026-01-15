# app.py
import streamlit as st
from components import (
    setup_page,
    create_sidebar_navigation,
    create_navigation_buttons,
    create_simple_metric,
)


def main():
    """主页面 - 完全使用 Streamlit 原生组件"""
    # 检查是否需要返回首页
    if st.session_state.get("return_to_home", False):
        st.session_state.return_to_home = False
        st.rerun()  # 确保页面完全刷新

    # 页面设置
    setup_page("内控管理分析系统")
    # 使用组件中的侧边栏导航
    create_sidebar_navigation()

    # 页面头部
    st.markdown("# 内控管理分析系统")
    st.markdown("*数据驱动的车辆管理与工单分析平台*")
    st.markdown("---")

    # 欢迎信息
    st.markdown(
        """
    ## 🎯 欢迎使用内控管理分析系统
    
    本系统提供专业的车辆出勤数据分析和工单管理功能，帮助您实现高效的内控管理。
    """
    )

    # 功能特性
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚗 车辆分析功能")
        st.markdown(
            """
        - **智能数据核查**：自动检查数据完整性和准确性
        - **异常检测**：识别异常出勤记录和费用
        - **多维分析**：按时间、地区、车辆等多维度分析
        - **可视化报告**：生成直观的数据图表和报告
        - **数据导出**：支持多种格式的数据导出
        """
        )

    with col2:
        st.markdown("### 📋 工单分析功能")
        st.markdown(
            """
        - **数据整合**：合并车辆出勤和工单数据
        - **任务跟踪**：实时监控工单完成状态
        - **绩效评估**：分析员工工作效率和质量
        - **智能匹配**：自动匹配车辆和工单记录
        - **统计分析**：生成工单完成率分析报告
        """
        )

    st.markdown("---")

    # 快速导航
    create_navigation_buttons()

    st.markdown("---")

    # 使用指南
    with st.expander("📖 使用指南", expanded=True):
        tab1, tab2, tab3 = st.tabs(["车辆分析", "工单分析", "系统设置"])

        with tab1:
            st.markdown(
                """
            ### 🚗 车辆分析使用步骤：
            
            1. **准备数据**
               - 准备车辆出勤数据Excel文件
               - 确保数据格式正确（从第2行开始）
               - 必需列：开始时间、结束时间、车牌号码等
            
            2. **导入分析**
               - 进入【车辆分析】页面
               - 上传数据文件
               - 系统自动执行数据核查
            
            3. **查看结果**
               - 查看统计指标和异常分布
               - 使用筛选功能查看特定数据
               - 导出分析报告
            
            4. **配置参数**
               - 根据业务需求调整核查阈值
               - 保存配置后重新导入数据生效
            """
            )

        with tab2:
            st.markdown(
                """
            ### 📋 工单分析使用步骤：
            
            1. **准备文件**
               - DTSP人员明细表
               - IResource人员明细表
               - 车辆出勤记录表
               - ISDP工单履行率明细表
            
            2. **上传文件**
               - 进入【工单分析】页面
               - 依次上传所有必需文件
               - 确保文件格式正确
            
            3. **数据处理**
               - 点击"一键处理数据"按钮
               - 系统自动合并和分析数据
               - 查看匹配率和完成情况
            
            4. **分析结果**
               - 查看工单状态分布
               - 分析员工工作效率
               - 导出分析报告
            """
            )

        with tab3:
            st.markdown(
                """
            ### ⚙️ 系统设置说明：
            
            1. **参数配置**
               - 工作时间阈值设置
               - 行驶里程范围设置
               - 费用上限设置
            
            2. **注意事项**
               - 修改配置后需重新导入数据
               - 参数应根据实际业务调整
               - 保存配置后立即生效
            """
            )

    # 系统状态
    st.markdown("---")
    st.markdown("### 🔧 系统状态")

    status_cols = st.columns(4)
    with status_cols[0]:
        create_simple_metric("系统版本", "1.2.0")
    with status_cols[1]:
        create_simple_metric("运行状态", "正常")
    with status_cols[2]:
        create_simple_metric("数据更新", "实时")
    with status_cols[3]:
        create_simple_metric("支持格式", "Excel/CSV")

    # 技术支持
    st.markdown("---")
    with st.expander("📞 技术支持", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                ### 联系方式
                - **服务热线**: 9090-980
                """
            )
        with col2:
            st.markdown(
                """
                ### 服务时间
                - 抽时间支持
                """
            )

    # 底部信息
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; padding: 20px;">
        <p>© 2024 内控管理分析系统 | 版本 1.2.0</p>
        <p>技术支持: support@example.com | 服务热线: 9090-980</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
