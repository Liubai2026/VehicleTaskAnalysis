import streamlit as st
import pandas as pd
from core import (
    merge_personnel_files,
    process_vehicle_attendance,
    process_task_progress,
    merge_vehicle_with_tasks,
)
from components import (
    setup_page,
    create_sidebar_navigation,
    create_header,
    create_info_box,
    create_simple_metric,
)
from core.data_services import (
    DataProcessingService,
    FilterService,
    DataValidationService,
)
from core.chart_generators import (
    TaskTrendChartGenerator,
    GroupedBarChartGenerator,
    ZeroDaysChartGenerator,
)
from components.ui_components import (
    FilterComponents,
    ChartComponents,
    FileUploadComponents,
    LayoutComponents,
    DataSummaryComponents,
)


def setup_data_processing_tab():
    """设置数据处理标签页"""
    st.markdown("### 📁 数据文件配置")
    st.markdown("请选择或确认以下数据文件的路径：")
    st.markdown("---")

    # 文件上传
    uploaded_files = FileUploadComponents.create_file_uploaders()

    st.markdown("---")

    # 数据处理按钮
    col_btn1, col_btn2 = st.columns([1, 2])
    with col_btn1:
        process_btn = st.button(
            "🚀 一键处理数据",
            type="primary",
            use_container_width=True,
            help="点击开始处理所有数据文件",
        )

    # 处理状态和结果
    if "processed_data" not in st.session_state:
        st.session_state.processed_data = None

    if process_btn:
        if not FileUploadComponents.validate_uploaded_files(uploaded_files):
            return

        with st.spinner("正在处理数据，请稍候..."):
            try:
                # 处理数据
                personnel_df = merge_personnel_files(
                    uploaded_files["personnel"], uploaded_files["employee"]
                )
                vehicle_df = process_vehicle_attendance(
                    uploaded_files["vehicle"], personnel_df
                )
                task_df = process_task_progress(
                    uploaded_files["task"], uploaded_files["employee"]
                )
                final_df = merge_vehicle_with_tasks(vehicle_df, task_df)

                # 保存到session state
                st.session_state.processed_data = final_df
                st.session_state.task_data = task_df
                st.session_state.processing_success = True

                create_info_box(
                    f"数据处理完成！共处理 {len(final_df)} 条记录。", "success"
                )

            except Exception as e:
                st.session_state.processing_success = False
                create_info_box(f"数据处理失败: {str(e)}", "error")

    # 显示处理结果
    if st.session_state.processed_data is not None:
        DataSummaryComponents.display_data_preview(st.session_state.processed_data)
        DataSummaryComponents.display_basic_metrics(st.session_state.processed_data)


def setup_visualization_tab():
    """设置可视化分析标签页"""
    if st.session_state.processed_data is None:
        st.warning(
            "⚠️ 请先在【数据文件选择】Tab中处理数据，然后切换到此Tab查看可视化结果。"
        )
        return

    df = st.session_state.task_data

    # 转换为日期类型
    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")

    LayoutComponents.create_section_header("数据分析面板", "车辆出勤与工单履行率分析")

    # 趋势分析部分
    LayoutComponents.create_section_header(
        "任务进展趋势分析", "显示全部数据的任务状态按日期变化趋势", "📈"
    )

    # 创建筛选器
    filters = FilterComponents.create_trend_filters(df)

    # 处理筛选数据
    trend_df = DataProcessingService.process_trend_data(df, filters)

    if DataValidationService.check_empty_data(trend_df):
        st.warning("没有符合条件的数据")
        return

    # 显示趋势图表
    trend_fig = TaskTrendChartGenerator.create_trend_chart(
        trend_df, "日期", "📈 平均人效（完成+通过）"
    )
    ChartComponents.display_trend_chart(trend_fig)

    # 显示趋势数据汇总
    trend_summary = DataProcessingService.get_trend_summary(trend_df)
    ChartComponents.display_dataframe(trend_summary, "📋 趋势数据汇总")

    # 上传人平均值分析
    LayoutComponents.create_section_header(
        "平均人效分析", "按上传人统计任务完成情况", "📊"
    )

    uploader_stats = DataProcessingService.calculate_uploader_stats(
        trend_df, filters.get("top_n", 10)
    )
    if not uploader_stats.empty:
        uploader_fig = TaskTrendChartGenerator.create_uploader_bar_chart(
            uploader_stats, "📊 平均人效（完成+通过）"
        )
        ChartComponents.display_trend_chart(uploader_fig)
        ChartComponents.display_dataframe(uploader_stats, "📋 工程师平均人效数据")

    # 城市趋势分析
    LayoutComponents.create_section_header(
        "城市趋势分析", "各城市任务完成情况趋势", "🏙️"
    )

    city_trends = DataProcessingService.calculate_city_trends(trend_df)
    if not city_trends.empty:
        city_fig = TaskTrendChartGenerator.create_trend_chart(
            trend_df, "日期", "📊 平均人效（完成+通过）（按城市）"
        )
        ChartComponents.display_trend_chart(city_fig)
        ChartComponents.display_dataframe(city_trends, "📋 各城市平均值数据")

    # 分组统计分析
    LayoutComponents.create_section_header(
        "分组统计分析", "按省、市统计各任务状态的数量", "📊"
    )

    group_filters = FilterComponents.create_simple_filters(
        df, ["province", "city"], "group"
    )
    group_df = DataProcessingService.process_trend_data(df, group_filters)

    group_cols = []
    if group_filters.get("province") and group_filters["province"] != "全部":
        group_cols.append("省")
    if group_filters.get("city") and group_filters["city"] != "全部":
        group_cols.append("市")

    if group_cols:
        group_fig, error = GroupedBarChartGenerator.create_grouped_bar_chart(
            group_df, group_cols, "📊 数据统计分组柱状图"
        )
        if group_fig:
            ChartComponents.display_trend_chart(group_fig)
            group_summary = group_df.groupby(group_cols)[
                ["待执行", "完成", "通过", "未知"]
            ].sum()
            ChartComponents.display_dataframe(group_summary, "📋 分组数据汇总")
        else:
            st.error(error)

    # 零任务天数分析
    LayoutComponents.create_section_header(
        "零任务天数分析", "按省、市统计任务完成度为零的天数", "⚠️"
    )

    zero_filters = FilterComponents.create_simple_filters(
        df, ["province", "city", "date_range"], "zero"
    )
    zero_df = DataProcessingService.process_trend_data(df, zero_filters)

    zero_group_cols = []
    if zero_filters.get("province") and zero_filters["province"] != "全部":
        zero_group_cols.append("省")
    if zero_filters.get("city") and zero_filters["city"] != "全部":
        zero_group_cols.append("市")

    if zero_group_cols:
        zero_fig, error = ZeroDaysChartGenerator.create_zero_days_chart(
            zero_df, zero_group_cols, "⚠️ 任务完成度为零的天数统计"
        )
        if zero_fig:
            ChartComponents.display_trend_chart(zero_fig)
            # 显示零任务天数汇总数据
            zero_summary = zero_df.groupby(zero_group_cols)[
                "待执行", "完成", "通过"
            ].sum()
            ChartComponents.display_dataframe(zero_summary, "📋 零任务天数汇总")
        else:
            st.error(error)


def main():
    """主应用"""
    # 页面设置
    setup_page("工单分析")
    create_sidebar_navigation()
    create_header("工单分析", "车辆出勤与工单履行率分析", "📋")

    # 创建标签页
    tabs = LayoutComponents.create_tabs(["数据文件选择", "数据可视化分析"])

    # 数据处理标签页
    with tabs["数据文件选择"]:
        setup_data_processing_tab()

    # 可视化分析标签页
    with tabs["数据可视化分析"]:
        setup_visualization_tab()


if __name__ == "__main__":
    main()
