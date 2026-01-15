# pages/task_analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

# 默认文件路径已移除，将使用文件上传功能


def create_trend_chart(df, date_col="日期"):
    """创建任务进展趋势图"""
    status_cols = ["待执行", "完成", "通过", "未知"]

    # 按日期分组汇总
    date_grouped = df.groupby(date_col)[status_cols].sum().reset_index()
    date_grouped[date_col] = pd.to_datetime(date_grouped[date_col])
    date_grouped = date_grouped.sort_values(date_col)

    # 颜色配置
    status_colors = {
        "待执行": "blue",
        "完成": "green",
        "通过": "orange",
        "未知": "gray",
    }

    fig = go.Figure()

    for status in status_cols:
        if status in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=date_grouped[date_col],
                    y=date_grouped[status],
                    mode="lines+markers+text",
                    name=status,
                    line=dict(
                        color=status_colors.get(status, "black"),
                        width=2,
                        shape="spline",
                        smoothing=1.3,
                    ),
                    marker=dict(size=6),
                    text=date_grouped[status],
                    textposition="top center",
                )
            )

    fig.update_layout(
        title="📈 任务进展按日期趋势",
        xaxis_title="日期",
        yaxis_title="任务数量",
        hovermode="x unified",
        showlegend=True,
        xaxis=dict(
            tickformat="%Y-%m-%d",
            tickangle=-45,
            tickfont=dict(size=10),
        ),
    )

    return fig


def create_grouped_bar_chart(df, group_cols):
    """创建分组柱状图"""
    status_cols = ["待执行", "完成", "通过", "未知"]

    # 检查列存在性
    required_cols = group_cols + status_cols
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, f"缺少列: {missing_cols}"

    # 按分组汇总
    grouped_df = df.groupby(group_cols)[status_cols].sum().reset_index()

    # 创建复合标签
    grouped_df["分组标签"] = grouped_df[group_cols[0]]
    for col in group_cols[1:]:
        grouped_df["分组标签"] = (
            grouped_df["分组标签"] + " - " + grouped_df[col].astype(str)
        )

    # 颜色配置
    status_colors = {
        "待执行": "#1f77b4",
        "完成": "#2ca02c",
        "通过": "#ff7f0e",
        "未知": "#7f7f7f",
    }

    fig = go.Figure()

    for status in status_cols:
        if status in df.columns:
            fig.add_trace(
                go.Bar(
                    x=grouped_df["分组标签"],
                    y=grouped_df[status],
                    name=status,
                    marker_color=status_colors.get(status, "#d62728"),
                    text=grouped_df[status],
                    textposition="outside",
                )
            )

    fig.update_layout(
        title="📊 数据统计分组柱状图",
        xaxis_title="省市",
        yaxis_title="数量",
        barmode="group",
        hovermode="x unified",
        showlegend=True,
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
    )

    return fig, None


def create_zero_days_chart(df, group_cols):
    """创建零任务天数统计图"""
    status_cols = ["待执行", "完成", "通过"]

    # 检查列存在性
    required_cols = group_cols + status_cols + ["日期"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, f"缺少列: {missing_cols}"

    # 筛选有效数据
    filter_condition = df["日期"].notna()
    for col in group_cols:
        filter_condition &= df[col].notna()

    valid_df = df[filter_condition].copy()

    # 计算每天任务总数
    valid_df["任务总数"] = valid_df[status_cols].sum(axis=1)

    # 按分组和日期统计
    group_cols_with_date = group_cols + ["日期"]
    daily_stats = valid_df.groupby(group_cols_with_date)["任务总数"].sum().reset_index()
    daily_stats["为零天数"] = (daily_stats["任务总数"] == 0).astype(int)

    # 按分组统计零任务天数
    result = daily_stats.groupby(group_cols)["为零天数"].sum().reset_index()

    # 创建复合标签
    result["地区"] = result[group_cols[0]]
    for col in group_cols[1:]:
        result["地区"] = result["地区"] + " - " + result[col].astype(str)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=result["地区"],
            y=result["为零天数"],
            name="任务为零天数",
            marker_color="#ff6b6b",
            text=result["为零天数"],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="⚠️ 任务完成度为零的天数统计",
        xaxis_title="地区",
        yaxis_title="天数",
        hovermode="x unified",
        showlegend=False,
        xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
    )

    return fig, None


def main():
    """工单分析页面"""
    # 检查是否需要返回首页
    if st.session_state.get("return_to_home", False):
        st.session_state.return_to_home = False
        st.rerun()  # 确保页面完全刷新

    # 页面设置
    setup_page("工单分析")

    # 使用组件中的侧边栏导航
    create_sidebar_navigation()

    # 页面头部
    create_header("工单分析", "车辆出勤与工单履行率分析", "📋")

    # 主Tab结构
    tab1, tab2 = st.tabs(["📁 数据文件选择", "📊 数据可视化分析"])

    # ========== Tab 1: 文件选择 ==========
    with tab1:
        st.markdown("### 📁 数据文件配置")
        st.markdown("请选择或确认以下数据文件的路径：")
        st.markdown("---")

        # 使用st.data_editor或文件选择器
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📋 人员信息文件")
            personnel_file = st.file_uploader(
                "选择人员明细信息文件 (Excel)",
                type=["xlsx"],
                key="personnel_file",
                help="人员明细信息表，包含员工编号、姓名、身份证号等",
            )
            if personnel_file:
                st.success(f"已选择: {personnel_file.name}")

            employee_file = st.file_uploader(
                "选择员工资源文件 (Excel)",
                type=["xlsx"],
                key="employee_file",
                help="IResource员工资源表，包含Uniportal账号等",
            )
            if employee_file:
                st.success(f"已选择: {employee_file.name}")

        with col2:
            st.markdown("#### 🚗 车辆与任务文件")
            vehicle_file = st.file_uploader(
                "选择车辆出勤记录文件 (Excel)",
                type=["xlsx"],
                key="vehicle_file",
                help="车辆出勤记录表，包含日期、车牌号、出车状态等",
            )
            if vehicle_file:
                st.success(f"已选择: {vehicle_file.name}")

            task_file = st.file_uploader(
                "选择工单履行率文件 (Excel)",
                type=["xlsx"],
                key="task_file",
                help="前后台工单履行率明细表",
            )
            if task_file:
                st.success(f"已选择: {task_file.name}")

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
            with st.spinner("正在处理数据，请稍候..."):
                try:
                    # 获取文件路径（优先使用上传的文件）
                    if personnel_file:
                        personnel_path = personnel_file
                    else:
                        # 如果没有上传文件，提示用户上传
                        create_info_box("请上传人员明细信息文件", "warning")
                        return

                    if employee_file:
                        employee_path = employee_file
                    else:
                        # 如果没有上传文件，提示用户上传
                        create_info_box("请上传员工资源文件", "warning")
                        return

                    if vehicle_file:
                        vehicle_path = vehicle_file
                    else:
                        # 如果没有上传文件，提示用户上传
                        create_info_box("请上传车辆出勤记录文件", "warning")
                        return

                    if task_file:
                        task_path = task_file
                    else:
                        # 如果没有上传文件，提示用户上传
                        create_info_box("请上传工单履行率文件", "warning")
                        return

                    # 处理数据
                    personnel_df = merge_personnel_files(personnel_path, employee_path)
                    vehicle_df = process_vehicle_attendance(vehicle_path, personnel_df)
                    task_df = process_task_progress(task_path)
                    final_df = merge_vehicle_with_tasks(vehicle_df, task_df)

                    # 保存到session state
                    st.session_state.processed_data = final_df
                    st.session_state.processing_success = True

                    create_info_box(
                        "数据处理完成！共处理 {} 条记录。".format(len(final_df)),
                        "success",
                    )

                except Exception as e:
                    st.session_state.processing_success = False
                    create_info_box(f"数据处理失败: {str(e)}", "error")

        # 显示处理结果预览
        if st.session_state.processed_data is not None:
            st.markdown("### 📋 数据预览")
            st.dataframe(
                st.session_state.processed_data.head(10), use_container_width=True
            )

            # 统计信息
            st.markdown("### 📊 数据统计")
            stats_cols = st.columns(4)
            with stats_cols[0]:
                create_simple_metric("总记录数", len(st.session_state.processed_data))
            with stats_cols[1]:
                create_simple_metric(
                    "日期范围",
                    f"{st.session_state.processed_data['日期'].nunique()} 天",
                )
            with stats_cols[2]:
                create_simple_metric(
                    "涉及人员",
                    st.session_state.processed_data["Uniportal账号"].nunique(),
                )
            with stats_cols[3]:
                create_simple_metric(
                    "涉及车辆",
                    (
                        st.session_state.processed_data.get(
                            "车牌号", pd.Series()
                        ).nunique()
                        if "车牌号" in st.session_state.processed_data.columns
                        else "N/A"
                    ),
                )
    # ========== Tab 2: 数据可视化 ==========
    with tab2:
        if st.session_state.processed_data is None:
            st.warning(
                "⚠️ 请先在【数据文件选择】Tab中处理数据，然后切换到此Tab查看可视化结果。"
            )

            # 提供示例数据选项
            st.markdown("或者，点击下方按钮使用示例数据进行演示：")
            if st.button("📥 加载示例数据并展示图表"):
                st.info("示例数据功能开发中，请先处理实际数据。")
        else:
            df = st.session_state.processed_data

            # 转换为日期类型以便日期选择器使用
            if "日期" in df.columns:
                df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                date_min = (
                    df["日期"].min()
                    if not df["日期"].isna().all()
                    else pd.Timestamp("2024-01-01")
                )
                date_max = (
                    df["日期"].max()
                    if not df["日期"].isna().all()
                    else pd.Timestamp("2024-12-31")
                )

            st.markdown("## 📊 数据分析面板")
            st.markdown("---")
            # ========== 趋势分析图 ==========
            st.markdown("### 📈 任务进展趋势分析")
            st.markdown("显示全部数据的任务状态按日期变化趋势")

            # 默认显示全部数据
            trend_df = df.copy()

            # 联动筛选器：省、市、上传人姓名、日期范围（全部整合在一起）
            st.markdown("#### 筛选条件")

            # 第一行：省、市、上传人
            col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)

            with col_filter1:
                provinces = (
                    ["全部"] + sorted(df["省"].dropna().unique())
                    if "省" in df.columns
                    else ["全部"]
                )
                selected_trend_province = st.selectbox(
                    "选择省份", options=provinces, key="trend_province"
                )

            with col_filter2:
                if selected_trend_province != "全部" and "市" in df.columns:
                    cities = ["全部"] + sorted(
                        df[df["省"] == selected_trend_province]["市"].dropna().unique()
                    )
                else:
                    cities = (
                        ["全部"] + sorted(df["市"].dropna().unique())
                        if "市" in df.columns
                        else ["全部"]
                    )

                selected_trend_city = st.selectbox(
                    "选择城市", options=cities, key="trend_city"
                )

            with col_filter3:
                if selected_trend_province != "全部" and "上传人姓名" in df.columns:
                    uploaders = ["全部"] + sorted(
                        df[
                            (df["省"] == selected_trend_province)
                            & (
                                df["市"] == selected_trend_city
                                if selected_trend_city != "全部"
                                else True
                            )
                        ]["上传人姓名"]
                        .dropna()
                        .unique()
                    )
                elif selected_trend_city != "全部" and "上传人姓名" in df.columns:
                    uploaders = ["全部"] + sorted(
                        df[df["市"] == selected_trend_city]["上传人姓名"]
                        .dropna()
                        .unique()
                    )
                else:
                    uploaders = (
                        ["全部"] + sorted(df["上传人姓名"].dropna().unique())
                        if "上传人姓名" in df.columns
                        else ["全部"]
                    )

                selected_trend_uploader = st.selectbox(
                    "选择上传人", options=uploaders, key="trend_uploader"
                )
            with col_filter4:
                # 第二行：日期范围选择器（时间段）
                selected_dates = st.date_input(
                    "选择日期范围",
                    value=(
                        (
                            date_min.date()
                            if "date_min" in locals()
                            else pd.Timestamp("2024-01-01").date()
                        ),
                        (
                            date_max.date()
                            if "date_max" in locals()
                            else pd.Timestamp("2024-12-31").date()
                        ),
                    ),
                    key="trend_date_range",
                )

            # 自动应用筛选（无需按钮）
            if len(selected_dates) == 2:
                trend_df = df.copy()
                start_date, end_date = selected_dates

                # 应用省市和上传人筛选
                if selected_trend_province != "全部":
                    trend_df = trend_df[trend_df["省"] == selected_trend_province]
                if selected_trend_city != "全部":
                    trend_df = trend_df[trend_df["市"] == selected_trend_city]
                if selected_trend_uploader != "全部" and "上传人姓名" in df.columns:
                    trend_df = trend_df[
                        trend_df["上传人姓名"] == selected_trend_uploader
                    ]

                # 应用日期筛选
                if "日期" in trend_df.columns:
                    trend_df = trend_df[
                        (trend_df["日期"] >= pd.Timestamp(start_date))
                        & (trend_df["日期"] <= pd.Timestamp(end_date))
                    ]

                st.session_state.trend_filtered_df = trend_df
            else:
                # 如果只选择了一个日期或没有选择，使用全部数据
                st.session_state.trend_filtered_df = df.copy()

            # 使用筛选后的数据或默认全部数据
            if "trend_filtered_df" in st.session_state:
                trend_df = st.session_state.trend_filtered_df

            # 显示图表
            if len(trend_df) > 0:
                fig = create_trend_chart(trend_df)
                st.plotly_chart(fig, use_container_width=True)

                # 数据汇总
                with st.expander("#### 📋 趋势数据汇总", expanded=False):
                    status_cols = ["待执行", "完成", "通过", "未知"]
                    trend_summary = trend_df.groupby("日期")[status_cols].sum()
                    st.dataframe(trend_summary, use_container_width=True)
            else:
                st.warning("没有符合条件的数据")

            st.markdown("---")

            # ========== 分组统计图 ==========
            st.markdown("### 📊 分组数据统计分析")
            st.markdown("按省、市统计各任务状态的数量")

            # 默认显示全部数据
            group_df = df.copy()
            group_cols = []
            if "省" in df.columns:
                group_cols.append("省")
            if "市" in df.columns:
                group_cols.append("市")

            # 筛选器（可折叠）
            st.subheader("🔧 省市筛选")
            col_province, col_city = st.columns(2)
            with col_province:
                provinces = (
                    ["全部"] + sorted(df["省"].dropna().unique())
                    if "省" in df.columns
                    else ["全部"]
                )
                selected_province = st.selectbox(
                    "选择省份", options=provinces, key="group_province"
                )

            with col_city:
                if selected_province != "全部" and "市" in df.columns:
                    cities = ["全部"] + sorted(
                        df[df["省"] == selected_province]["市"].dropna().unique()
                    )
                else:
                    cities = (
                        ["全部"] + sorted(df["市"].dropna().unique())
                        if "市" in df.columns
                        else ["全部"]
                    )

                selected_city = st.selectbox(
                    "选择城市", options=cities, key="group_city"
                )

            # 自动应用省市筛选（无需按钮）
            group_df = df.copy()
            if selected_province != "全部":
                group_df = group_df[group_df["省"] == selected_province]
            if selected_city != "全部":
                group_df = group_df[group_df["市"] == selected_city]

            # 重新计算分组维度
            group_cols = []
            if selected_province != "全部":
                group_cols.append("省")
            if selected_city != "全部":
                group_cols.append("市")
            if not group_cols:
                if "省" in df.columns:
                    group_cols.append("省")
                if "市" in df.columns:
                    group_cols.append("市")

            # 显示图表
            if group_cols:
                fig, error = create_grouped_bar_chart(group_df, group_cols)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 数据汇总
                    st.markdown("#### 📋 分组数据汇总")
                    status_cols = ["待执行", "完成", "通过", "未知"]
                    group_summary = group_df.groupby(group_cols)[status_cols].sum()
                    st.dataframe(group_summary, use_container_width=True)
                else:
                    st.error(error)
            else:
                st.warning("数据中缺少省、市列，无法进行分组统计")

            st.markdown("---")

            # ========== 零任务天数统计 ==========
            st.markdown("### ⚠️ 零任务天数统计分析")
            st.markdown("按省、市统计任务完成度为零的天数")

            # 默认显示全部数据
            zero_df = df.copy()
            zero_group_cols = []
            if "省" in df.columns:
                zero_group_cols.append("省")
            if "市" in df.columns:
                zero_group_cols.append("市")

            # 筛选器（可折叠）
            st.subheader("🔧 省市和时间范围筛选")

            col_zero_province, col_zero_city, col_zero_dates = st.columns(3)
            with col_zero_province:
                zero_provinces = (
                    ["全部"] + sorted(df["省"].dropna().unique())
                    if "省" in df.columns
                    else ["全部"]
                )
                selected_zero_province = st.selectbox(
                    "选择省份", options=zero_provinces, key="zero_province"
                )

            with col_zero_city:
                if selected_zero_province != "全部" and "市" in df.columns:
                    zero_cities = ["全部"] + sorted(
                        df[df["省"] == selected_zero_province]["市"].dropna().unique()
                    )
                else:
                    zero_cities = (
                        ["全部"] + sorted(df["市"].dropna().unique())
                        if "市" in df.columns
                        else ["全部"]
                    )

                selected_zero_city = st.selectbox(
                    "选择城市", options=zero_cities, key="zero_city"
                )

            with col_zero_dates:
                # 零任务天数统计日期范围选择器（时间段）
                zero_selected_dates = st.date_input(
                    "选择日期范围",
                    value=(
                        (
                            date_min.date()
                            if "date_min" in locals()
                            else pd.Timestamp("2024-01-01").date()
                        ),
                        (
                            date_max.date()
                            if "date_max" in locals()
                            else pd.Timestamp("2024-12-31").date()
                        ),
                    ),
                    key="zero_date_range",
                )

            # 自动应用筛选到零任务天数统计（无需按钮）
            if len(zero_selected_dates) == 2:
                zero_df = df.copy()
                zero_start_date, zero_end_date = zero_selected_dates

                # 应用省市筛选
                if selected_zero_province != "全部":
                    zero_df = zero_df[zero_df["省"] == selected_zero_province]
                if selected_zero_city != "全部":
                    zero_df = zero_df[zero_df["市"] == selected_zero_city]

                # 应用日期筛选
                if "日期" in zero_df.columns:
                    zero_df = zero_df[
                        (zero_df["日期"] >= pd.Timestamp(zero_start_date))
                        & (zero_df["日期"] <= pd.Timestamp(zero_end_date))
                    ]
            else:
                # 如果只选择了一个日期或没有选择，使用全部数据
                zero_df = df.copy()

            # 重新计算分组维度
            zero_group_cols = []
            if selected_zero_province != "全部":
                zero_group_cols.append("省")
            if selected_zero_city != "全部":
                zero_group_cols.append("市")
            if not zero_group_cols:
                if "省" in df.columns:
                    zero_group_cols.append("省")
                if "市" in df.columns:
                    zero_group_cols.append("市")

            # 显示图表
            if zero_group_cols:
                fig, error = create_zero_days_chart(zero_df, zero_group_cols)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # 数据汇总
                    st.markdown("#### 📋 零任务天数汇总")
                    status_cols = ["待执行", "完成", "通过"]
                    filter_cond = zero_df["日期"].notna()
                    for col in zero_group_cols:
                        filter_cond &= zero_df[col].notna()

                    valid_df = zero_df[filter_cond].copy()
                    valid_df["任务总数"] = valid_df[status_cols].sum(axis=1)

                    daily_stats = (
                        valid_df.groupby(zero_group_cols + ["日期"])["任务总数"]
                        .sum()
                        .reset_index()
                    )
                    daily_stats["为零天数"] = (daily_stats["任务总数"] == 0).astype(int)
                    zero_summary = (
                        daily_stats.groupby(zero_group_cols)["为零天数"]
                        .sum()
                        .reset_index()
                    )

                    st.dataframe(zero_summary, use_container_width=True)
                else:
                    st.error(error)
            else:
                st.warning("数据中缺少省、市列，无法进行分组统计")


if __name__ == "__main__":
    main()
