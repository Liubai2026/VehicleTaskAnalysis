# pages/task_analysis.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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


# ==================== 图表创建函数 ====================


def create_trend_chart(df, date_col="日期"):
    """创建任务进展趋势图 - 显示完成+通过总和"""
    if "完成" not in df.columns or "通过" not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title="工单完成量（完成+通过）",
            xaxis_title="日期",
            yaxis_title="工单完成量",
            height=400,
        )
        return fig

    df["完成+通过"] = df["完成"] + df["通过"]

    if "市" in df.columns:
        city_date_grouped = (
            df.groupby(["市", date_col])["完成+通过"].sum().reset_index()
        )
        city_date_grouped[date_col] = pd.to_datetime(city_date_grouped[date_col])

        fig = go.Figure()
        colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

        for i, city in enumerate(city_date_grouped["市"].unique()):
            city_data = city_date_grouped[city_date_grouped["市"] == city].sort_values(
                date_col
            )
            fig.add_trace(
                go.Scatter(
                    x=city_data[date_col],
                    y=city_data["完成+通过"],
                    mode="lines+markers+text",
                    name=city,
                    line=dict(
                        color=colors[i % len(colors)],
                        width=2,
                        shape="spline",
                        smoothing=1.3,
                    ),
                    marker=dict(size=8),
                    text=city_data["完成+通过"],
                    textposition="top center",
                    textfont=dict(size=10),
                )
            )
    else:
        date_grouped = df.groupby(date_col)["完成+通过"].sum().reset_index()
        date_grouped[date_col] = pd.to_datetime(date_grouped[date_col])
        date_grouped = date_grouped.sort_values(date_col)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=date_grouped[date_col],
                y=date_grouped["完成+通过"],
                mode="lines+markers+text",
                name="完成+通过",
                line=dict(color="#2ca02c", width=3, shape="spline", smoothing=1.3),
                marker=dict(size=8, color="#2ca02c"),
                text=date_grouped["完成+通过"],
                textposition="top center",
                textfont=dict(size=10),
            )
        )

    fig.update_layout(
        title="📈 工单完成量（完成+通过）",
        xaxis_title="日期",
        yaxis_title="完成+通过总和",
        hovermode="x unified",
        showlegend=("市" in df.columns),
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=-45, tickfont=dict(size=10)),
        legend=(
            dict(
                yanchor="top",
                y=-0.3,
                xanchor="center",
                x=0.5,
                orientation="h",
                font=dict(size=10),
            )
            if "市" in df.columns
            else None
        ),
        height=500,
    )
    return fig


def create_grouped_bar_chart(df, group_cols):
    """创建分组柱状图"""
    status_cols = ["待执行", "完成", "通过", "未知"]
    required_cols = group_cols + status_cols
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, f"缺少列: {missing_cols}"

    grouped_df = df.groupby(group_cols)[status_cols].sum().reset_index()
    grouped_df["分组标签"] = grouped_df[group_cols[0]]
    for col in group_cols[1:]:
        grouped_df["分组标签"] = (
            grouped_df["分组标签"] + " - " + grouped_df[col].astype(str)
        )

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
    required_cols = group_cols + status_cols + ["日期"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return None, f"缺少列: {missing_cols}"

    filter_condition = df["日期"].notna()
    for col in group_cols:
        filter_condition &= df[col].notna()

    valid_df = df[filter_condition].copy()
    valid_df["任务总数"] = valid_df[status_cols].sum(axis=1)

    group_cols_with_date = group_cols + ["日期"]
    daily_stats = valid_df.groupby(group_cols_with_date)["任务总数"].sum().reset_index()
    daily_stats["为零天数"] = (daily_stats["任务总数"] == 0).astype(int)

    result = daily_stats.groupby(group_cols)["为零天数"].sum().reset_index()
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


# ==================== 数据处理函数 ====================


def process_uploaded_files(personnel_file, employee_file, vehicle_file, task_file):
    """处理上传的文件，返回处理后的数据"""
    personnel_df = merge_personnel_files(personnel_file, employee_file)
    vehicle_df = process_vehicle_attendance(vehicle_file, personnel_df)
    task_df = process_task_progress(task_file, employee_file)
    final_df = merge_vehicle_with_tasks(vehicle_df, task_df)
    return final_df, task_df


def filter_data_by_criteria(
    df, province=None, city=None, uploader=None, start_date=None, end_date=None
):
    """根据筛选条件过滤数据"""
    filtered_df = df.copy()

    if province and province != "全部":
        filtered_df = filtered_df[filtered_df["省"] == province]
    if city and city != "全部":
        filtered_df = filtered_df[filtered_df["市"] == city]
    if uploader and uploader != "全部" and "上传人姓名" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["上传人姓名"] == uploader]
    if start_date and end_date and "日期" in filtered_df.columns:
        # 确保日期列是datetime类型
        if filtered_df["日期"].dtype != "datetime64[ns]":
            filtered_df["日期"] = pd.to_datetime(filtered_df["日期"], errors="coerce")
        filtered_df = filtered_df[
            (filtered_df["日期"] >= pd.Timestamp(start_date))
            & (filtered_df["日期"] <= pd.Timestamp(end_date))
        ].copy()

    return filtered_df


def calculate_uploader_stats(df, top_n=10):
    """计算上传人平均值统计"""
    if (
        "上传人姓名" not in df.columns
        or "完成" not in df.columns
        or "通过" not in df.columns
    ):
        return pd.DataFrame()

    df = df.copy()
    df["完成+通过"] = df["完成"] + df["通过"]

    uploader_avg = df.groupby("上传人姓名")["完成+通过"].mean().reset_index()
    uploader_avg = uploader_avg.sort_values("完成+通过", ascending=False).head(top_n)
    uploader_avg["排名"] = range(1, len(uploader_avg) + 1)

    return uploader_avg


def calculate_city_trends(df, max_cities=10):
    """计算城市趋势数据"""
    if "完成" not in df.columns or "通过" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["完成+通过"] = df["完成"] + df["通过"]

    if "市" in df.columns:
        cities = df["市"].dropna().unique()
        if len(cities) > max_cities:
            main_cities = cities[:max_cities]
            city_df = df[df["市"].isin(main_cities)]
        else:
            city_df = df

        avg_df = city_df.groupby(["市", "日期"])["完成+通过"].mean().reset_index()
        return avg_df
    else:
        avg_df = df.groupby("日期")["完成+通过"].mean().reset_index()
        return avg_df


def create_uploader_bar_chart(uploader_stats):
    """创建上传人平均值条形图"""
    if uploader_stats.empty:
        return None

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=uploader_stats["上传人姓名"],
            y=uploader_stats["完成+通过"],
            marker_color=px.colors.qualitative.Set3[: len(uploader_stats)],
            text=uploader_stats["完成+通过"].round(2),
            textposition="auto",
        )
    )

    fig.update_layout(
        title="📊 平均人效Top-n呈现",
        xaxis_title="工程师姓名",
        yaxis_title="平均人效",
        xaxis_tickangle=-45,
        showlegend=False,
        height=400,
    )
    return fig


def create_city_trend_chart(df, title="平均人效（完成+通过）（按城市）"):
    """创建城市趋势折线图"""
    if df.empty or "完成" not in df.columns or "通过" not in df.columns:
        return None

    df = df.copy()
    df["完成+通过"] = df["完成"] + df["通过"]

    if "市" not in df.columns:
        return None

    cities = df["市"].dropna().unique()

    if len(cities) > 10:
        main_cities = cities[:10]
        city_df = df[df["市"].isin(main_cities)]
    else:
        city_df = df

    avg_df = city_df.groupby(["市", "日期"])["完成+通过"].mean().reset_index()

    fig = go.Figure()
    colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

    for i, city in enumerate(avg_df["市"].unique()):
        city_data = avg_df[avg_df["市"] == city]
        fig.add_trace(
            go.Scatter(
                x=city_data["日期"],
                y=city_data["完成+通过"],
                mode="lines+markers+text",
                name=city,
                line=dict(
                    color=colors[i % len(colors)],
                    width=2,
                    shape="spline",
                    smoothing=1.3,
                ),
                marker=dict(size=8),
                text=city_data["完成+通过"].round(2),
                textposition="top center",
                textfont=dict(size=10),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="日期",
        yaxis_title="平均值",
        hovermode="x unified",
        showlegend=True,
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=-45, tickfont=dict(size=10)),
        height=500,
        legend=dict(
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            orientation="h",
            font=dict(size=10),
        ),
    )
    return fig


def get_trend_summary(df):
    """获取趋势数据汇总"""
    status_cols = ["待执行", "完成", "通过", "未知"]

    if "市" in df.columns:
        trend_summary = df.groupby(["日期", "市"])[status_cols].sum().reset_index()
    else:
        trend_summary = df.groupby("日期")[status_cols].sum().reset_index()

    return trend_summary


# ==================== 页面组件函数 ====================


def render_file_upload_section():
    """渲染文件上传区域"""
    with st.expander("### 📁 数据文件配置", expanded=True):
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

    return personnel_file, employee_file, vehicle_file, task_file


def render_trend_filters(df, date_min, date_max):
    """渲染趋势分析筛选器"""
    col_filter1, col_filter2, col_filter3, col_filter4, col_filter5 = st.columns(5)

    filters = {}

    with col_filter1:
        provinces = (
            ["全部"] + sorted(df["省"].dropna().unique())
            if "省" in df.columns
            else ["全部"]
        )
        filters["province"] = st.selectbox(
            "选择省份", options=provinces, key="trend_province"
        )

    with col_filter2:
        if filters["province"] != "全部" and "市" in df.columns:
            cities = ["全部"] + sorted(
                df[df["省"] == filters["province"]]["市"].dropna().unique()
            )
        else:
            cities = (
                ["全部"] + sorted(df["市"].dropna().unique())
                if "市" in df.columns
                else ["全部"]
            )
        filters["city"] = st.selectbox("选择城市", options=cities, key="trend_city")

    with col_filter3:
        if filters["province"] != "全部" and "上传人姓名" in df.columns:
            uploaders = ["全部"] + sorted(
                df[
                    (df["省"] == filters["province"])
                    & (
                        df["市"] == filters["city"]
                        if filters["city"] != "全部"
                        else True
                    )
                ]["上传人姓名"]
                .dropna()
                .unique()
            )
        elif filters["city"] != "全部" and "上传人姓名" in df.columns:
            uploaders = ["全部"] + sorted(
                df[df["市"] == filters["city"]]["上传人姓名"].dropna().unique()
            )
        else:
            uploaders = (
                ["全部"] + sorted(df["上传人姓名"].dropna().unique())
                if "上传人姓名" in df.columns
                else ["全部"]
            )
        filters["uploader"] = st.selectbox(
            "选择上传人", options=uploaders, key="trend_uploader"
        )

    with col_filter4:
        filters["date_range"] = st.date_input(
            "选择日期范围",
            value=(date_min.date(), date_max.date()),
            key="trend_date_range",
        )

    with col_filter5:
        filters["top_n"] = st.number_input(
            "显示TOP数量", min_value=1, max_value=50, value=10, step=1, key="top_n"
        )

    return filters


def render_group_filters(df):
    """渲染分组统计筛选器"""
    col_province, col_city = st.columns(2)
    filters = {}

    with col_province:
        provinces = (
            ["全部"] + sorted(df["省"].dropna().unique())
            if "省" in df.columns
            else ["全部"]
        )
        filters["province"] = st.selectbox(
            "选择省份", options=provinces, key="group_province"
        )

    with col_city:
        if filters["province"] != "全部" and "市" in df.columns:
            cities = ["全部"] + sorted(
                df[df["省"] == filters["province"]]["市"].dropna().unique()
            )
        else:
            cities = (
                ["全部"] + sorted(df["市"].dropna().unique())
                if "市" in df.columns
                else ["全部"]
            )
        filters["city"] = st.selectbox("选择城市", options=cities, key="group_city")

    return filters


def render_zero_filters(df, date_min, date_max):
    """渲染零任务天数筛选器"""
    col_province, col_city, col_dates = st.columns(3)
    filters = {}

    with col_province:
        provinces = (
            ["全部"] + sorted(df["省"].dropna().unique())
            if "省" in df.columns
            else ["全部"]
        )
        filters["province"] = st.selectbox(
            "选择省份", options=provinces, key="zero_province"
        )

    with col_city:
        if filters["province"] != "全部" and "市" in df.columns:
            cities = ["全部"] + sorted(
                df[df["省"] == filters["province"]]["市"].dropna().unique()
            )
        else:
            cities = (
                ["全部"] + sorted(df["市"].dropna().unique())
                if "市" in df.columns
                else ["全部"]
            )
        filters["city"] = st.selectbox("选择城市", options=cities, key="zero_city")

    with col_dates:
        filters["date_range"] = st.date_input(
            "选择日期范围",
            value=(date_min.date(), date_max.date()),
            key="zero_date_range",
        )

    return filters


def render_data_preview(data):
    """渲染数据预览"""
    with st.expander("📋 工单明细详情", expanded=False):
        st.dataframe(data, hide_index=True)


# ==================== 主功能模块 ====================


def setup_data_processing_tab():
    """设置数据处理标签页"""
    personnel_file, employee_file, vehicle_file, task_file = (
        render_file_upload_section()
    )

    st.markdown("---")

    col_btn1, col_btn2 = st.columns([1, 2])

    with col_btn1:
        process_btn = st.button(
            "🚀 一键处理数据",
            type="primary",
            use_container_width=True,
            help="点击开始处理所有数据文件",
        )

    if "processed_data" not in st.session_state:
        st.session_state.processed_data = None

    if process_btn:
        if not personnel_file:
            create_info_box("请上传人员明细信息文件", "warning")
            return
        if not employee_file:
            create_info_box("请上传员工资源文件", "warning")
            return
        if not vehicle_file:
            create_info_box("请上传车辆出勤记录文件", "warning")
            return
        if not task_file:
            create_info_box("请上传工单履行率文件", "warning")
            return

        with st.spinner("正在处理数据，请稍候..."):
            try:
                final_df, task_df = process_uploaded_files(
                    personnel_file, employee_file, vehicle_file, task_file
                )

                st.session_state.processed_data = final_df
                st.session_state.task_data = task_df
                st.session_state.final_df = final_df
                st.session_state.processing_success = True

                create_info_box(
                    f"数据处理完成！共处理 {len(final_df)} 条记录。", "success"
                )

            except Exception as e:
                st.session_state.processing_success = False
                create_info_box(f"数据处理失败: {str(e)}", "error")


def setup_visualization_tab():
    """设置可视化分析标签页"""
    if st.session_state.processed_data is None:
        st.warning(
            "⚠️ 请先在【数据文件选择】Tab中处理数据，然后切换到此Tab查看可视化结果。"
        )
        st.markdown("或者，点击下方按钮使用示例数据进行演示：")
        if st.button("📥 加载示例数据并展示图表"):
            st.info("示例数据功能开发中，请先处理实际数据。")
        return

    df = st.session_state.task_data

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

    # 趋势分析部分
    st.markdown("### 📈 任务进展趋势分析")
    st.markdown("显示全部数据的任务状态按日期变化趋势")

    filters = render_trend_filters(df, date_min, date_max)

    # 应用筛选
    if len(filters["date_range"]) == 2:
        trend_df = filter_data_by_criteria(
            df,
            filters["province"],
            filters["city"],
            filters["uploader"],
            filters["date_range"][0],
            filters["date_range"][1],
        )
    else:
        trend_df = df.copy()

    # 上传人平均值分析
    st.markdown("### 📊 平均人效Top-n分析")

    if len(trend_df) > 0:
        uploader_stats = calculate_uploader_stats(trend_df, filters.get("top_n", 10))

        if not uploader_stats.empty:
            fig_uploader = create_uploader_bar_chart(uploader_stats)
            if fig_uploader:
                st.plotly_chart(fig_uploader, use_container_width=True)

            with st.expander("📋 工程师平均人效数据", expanded=False):
                st.dataframe(uploader_stats, use_container_width=True, hide_index=True)

    # 趋势图表
    st.markdown("### 📊 工单完成量（完成+通过）")
    fig_trend = create_trend_chart(trend_df)
    st.plotly_chart(fig_trend, use_container_width=True)

    # 趋势数据汇总
    with st.expander("📋 趋势数据汇总", expanded=False):
        trend_summary = get_trend_summary(trend_df)
        st.dataframe(trend_summary, use_container_width=True, hide_index=True)

    with st.expander("📋 详细数据预览", expanded=False):
        st.dataframe(trend_df, hide_index=True)

    # 城市趋势分析
    st.markdown("### 📈 平均人效（完成+通过）（按城市）")

    fig_city = create_city_trend_chart(trend_df)
    if fig_city:
        st.plotly_chart(fig_city, use_container_width=True)

    # 详细数据预览
    with st.expander("📋 详细数据预览", expanded=False):
        st.dataframe(trend_df, hide_index=True)

    st.markdown("---")

    # 分组统计分析
    st.markdown("### 📊 分组数据统计分析")

    group_filters = render_group_filters(df)
    group_df = filter_data_by_criteria(
        df, group_filters["province"], group_filters["city"]
    )
    group_cols = []

    if group_filters["province"] != "全部":
        group_cols.append("省")
    if group_filters["city"] != "全部":
        group_cols.append("市")
    if not group_cols:
        if "省" in df.columns:
            group_cols.append("省")
        if "市" in df.columns:
            group_cols.append("市")

    if group_cols:
        fig, error = create_grouped_bar_chart(group_df, group_cols)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("📋 分组数据汇总")
            status_cols = ["待执行", "完成", "通过", "未知"]
            group_summary = group_df.groupby(group_cols)[status_cols].sum()
            st.dataframe(group_summary, use_container_width=True)
        else:
            st.error(error)
    else:
        st.warning("数据中缺少省、市列，无法进行分组统计")

    st.markdown("---")

    # 零任务天数分析
    st.markdown("### ⚠️ 零任务天数统计分析")

    if not hasattr(st.session_state, "final_df") or st.session_state.final_df is None:
        st.warning("⚠️ 没有零工单出车的情况")
        return

    zero_filters = render_zero_filters(df, date_min, date_max)
    zero_df = filter_data_by_criteria(
        st.session_state.final_df,
        zero_filters["province"],
        zero_filters["city"],
        None,
        zero_filters["date_range"][0] if len(zero_filters["date_range"]) == 2 else None,
        zero_filters["date_range"][1] if len(zero_filters["date_range"]) == 2 else None,
    )

    zero_group_cols = []
    if zero_filters["province"] != "全部":
        zero_group_cols.append("省")
    if zero_filters["city"] != "全部":
        zero_group_cols.append("市")
    if not zero_group_cols:
        if "省" in df.columns:
            zero_group_cols.append("省")
        if "市" in df.columns:
            zero_group_cols.append("市")

    if zero_group_cols:
        fig, error = create_zero_days_chart(zero_df, zero_group_cols)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("📋 零任务天数汇总")
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
                daily_stats.groupby(zero_group_cols)["为零天数"].sum().reset_index()
            )

            st.dataframe(zero_summary, use_container_width=True)
        else:
            st.error(error)
    else:
        st.warning("数据中缺少省、市列，无法进行分组统计")


def main():
    """工单分析页面"""
    if st.session_state.get("return_to_home", False):
        st.session_state.return_to_home = False
        st.rerun()

    setup_page("工单分析")
    create_sidebar_navigation()
    create_header("工单分析", "车辆出勤与工单履行率分析", "📋")

    tab1, tab2 = st.tabs(["📁 数据文件选择", "📊 数据可视化分析"])

    with tab1:
        setup_data_processing_tab()

    with tab2:
        setup_visualization_tab()


if __name__ == "__main__":
    main()
