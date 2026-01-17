import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, time
from typing import Dict, Any
from core import VehicleDataChecker, get_vehicle_default_config
from components import (
    create_sidebar_navigation,
    setup_page,
    create_header,
    create_info_box,
    create_simple_metric,
)


# setup_page() 函数已从 layout_components 导入，此处不再定义


def update_config():
    """更新配置的回调函数"""

    config = {
        "work_time": {
            "min_hours": st.session_state.min_hours,
            "max_hours": st.session_state.max_hours,
            "work_time_threshold": st.session_state.work_time_threshold,
            "is_work_verdict": st.session_state.is_work_verdict,
        },
        "mileage": {
            "min_mileage": st.session_state.min_mileage,
            "max_mileage": st.session_state.max_mileage,
        },
        "toll_fee": {"max_fee": st.session_state.toll_fee},
        "overtime_fee": {"max_fee": st.session_state.overtime_fee},
    }
    st.session_state.config = config


def configView_set():
    col1, col2, col3 = st.columns(3)

    with col1:
        min_hours = st.number_input(
            "最小工作时长(小时)",
            min_value=0.0,
            max_value=24.0,
            value=st.session_state.config["work_time"]["min_hours"],
            step=0.5,
            key="min_hours",
            on_change=update_config,  # 添加回调
        )
        min_mileage = st.number_input(
            "最小行驶里程(公里)",
            min_value=0,
            value=st.session_state.config["mileage"]["min_mileage"],
            step=10,
            key="min_mileage",
            on_change=update_config,
        )
        toll_fee = st.number_input(
            "路桥费门限(元)",
            min_value=0,
            value=st.session_state.config["toll_fee"]["max_fee"],
            step=10,
            key="toll_fee",
            on_change=update_config,
        )

    with col2:
        max_hours = st.number_input(
            "最大工作时长(小时)",
            min_value=0.0,
            max_value=24.0,
            value=st.session_state.config["work_time"]["max_hours"],
            step=0.5,
            key="max_hours",
            on_change=update_config,
        )
        max_mileage = st.number_input(
            "最大行驶里程(公里)",
            min_value=0,
            value=st.session_state.config["mileage"]["max_mileage"],
            step=50,
            key="max_mileage",
            on_change=update_config,
        )
        overtime_fee = st.number_input(
            "加班费门限(元)",
            min_value=0,
            value=st.session_state.config["overtime_fee"]["max_fee"],
            step=20,
            key="overtime_fee",
            on_change=update_config,
        )
    with col3:
        work_time_threshold = st.time_input(
            "出车打卡时间",
            value=time(9, 15, 00),
            key="work_time_threshold",
            on_change=update_config,
        )

    col1, col2, col3 = st.columns([1, 2, 7])
    with col1:
        is_work_verdict = st.checkbox(
            "是否检查打卡车辆",
            key="is_work_verdict",
            on_change=update_config,
        )
    with col2:
        # 添加保存按钮
        if st.button("💾 保存配置"):
            update_config()
            st.success("✅ 配置已保存！")

    return st.session_state.config


def init_data():
    # 在页面顶部初始化配置
    if "config" not in st.session_state:
        # 设置默认配置
        st.session_state.config = {
            "work_time": {
                "min_hours": 8.0,
                "max_hours": 12.0,
                "work_time_threshold": time(9, 15, 0),
                "is_work_verdict": False,
            },
            "mileage": {"min_mileage": 50, "max_mileage": 300},
            "toll_fee": {"max_fee": 100},
            "overtime_fee": {"max_fee": 20},
        }

    # 初始化session状态
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
    if "df" not in st.session_state:
        st.session_state.df = None
    if "checker" not in st.session_state:
        st.session_state.checker = None
    if "stats" not in st.session_state:
        st.session_state.stats = None


# 数据看板界面
def data_board_view():

    if not st.session_state.stats:
        return

    stats = st.session_state.stats
    df = st.session_state.df

    # 获取总的记录数
    total_records = len(df)

    # 创建指标卡片
    cols = st.columns(5)

    with cols[0]:
        st.metric("总记录数", total_records)

    # 检查各项核查是否存在
    if "工作时长核查" in stats:
        with cols[1]:
            work_time_abnormal = stats["工作时长核查"]["abnormal"]
            work_time_rate = (
                (work_time_abnormal / total_records * 100) if total_records > 0 else 0
            )
            st.metric(
                label="工作时长异常",
                value=work_time_abnormal,
                delta=f"{work_time_rate:.1f}%",
            )

    if "公里数核查" in stats:
        with cols[2]:
            mileage_abnormal = stats["公里数核查"]["abnormal"]
            mileage_rate = (
                (mileage_abnormal / total_records * 100) if total_records > 0 else 0
            )
            st.metric(
                label="公里数异常", value=mileage_abnormal, delta=f"{mileage_rate:.1f}%"
            )

    if "路桥费核查" in stats:
        with cols[3]:
            toll_fee_abnormal = stats["路桥费核查"]["abnormal"]
            toll_fee_rate = (
                (toll_fee_abnormal / total_records * 100) if total_records > 0 else 0
            )
            st.metric(
                label="路桥费异常",
                value=toll_fee_abnormal,
                delta=f"{toll_fee_rate:.1f}%",
            )

    if "加班费核查" in stats:
        with cols[4]:
            overtime_fee_abnormal = stats["加班费核查"]["abnormal"]
            overtime_fee_rate = (
                (overtime_fee_abnormal / total_records * 100)
                if total_records > 0
                else 0
            )
            st.metric(
                label="加班费异常",
                value=overtime_fee_abnormal,
                delta=f"{overtime_fee_rate:.1f}%",
            )


def abnormal_data_view():

    if not st.session_state.stats:
        return
    df = st.session_state.df
    stats = st.session_state.stats
    # 获取总的记录数
    total_records = len(df)

    # 创建异常数量数据表
    abnormal_data = []

    if "工作时长核查" in stats:
        abnormal_data.append(
            {
                "核查项目": "工作时长",
                "总记录数": total_records,
                "异常数量": stats["工作时长核查"]["abnormal"],
                "异常占比": (
                    (stats["工作时长核查"]["abnormal"] / total_records * 100)
                    if total_records > 0
                    else 0
                ),
            }
        )

    if "公里数核查" in stats:
        abnormal_data.append(
            {
                "核查项目": "公里数",
                "总记录数": total_records,
                "异常数量": stats["公里数核查"]["abnormal"],
                "异常占比": (
                    (stats["公里数核查"]["abnormal"] / total_records * 100)
                    if total_records > 0
                    else 0
                ),
            }
        )

    if "路桥费核查" in stats:
        abnormal_data.append(
            {
                "核查项目": "路桥费",
                "总记录数": total_records,
                "异常数量": stats["路桥费核查"]["abnormal"],
                "异常占比": (
                    (stats["路桥费核查"]["abnormal"] / total_records * 100)
                    if total_records > 0
                    else 0
                ),
            }
        )

    if "加班费核查" in stats:
        abnormal_data.append(
            {
                "核查项目": "加班费",
                "总记录数": total_records,
                "异常数量": stats["加班费核查"]["abnormal"],
                "异常占比": (
                    (stats["加班费核查"]["abnormal"] / total_records * 100)
                    if total_records > 0
                    else 0
                ),
            }
        )

    if abnormal_data:
        abnormal_df = pd.DataFrame(abnormal_data)
        abnormal_df = abnormal_df.sort_values("异常数量", ascending=False)

        # 创建异常数量柱状图
        fig = go.Figure(
            data=[
                go.Bar(
                    x=abnormal_df["核查项目"],
                    y=abnormal_df["异常数量"],
                    text=[str(num) for num in abnormal_df["异常数量"]],
                    textposition="outside",
                    marker_color=px.colors.qualitative.Set3[: len(abnormal_df)],
                    hovertemplate="%{y}",
                )
            ]
        )

        fig.update_layout(
            title=dict(
                text="各项核查异常数量",
                font=dict(size=16, color="#1E293B"),
                x=0.5,
                xanchor="center",
            ),
            xaxis=dict(title="核查项目", tickfont=dict(size=12)),
            yaxis=dict(
                title="异常数量",
                gridcolor="lightgray",
                range=[
                    0,
                    max(abnormal_df["异常数量"]) * 1.5 if len(abnormal_df) > 0 else 100,
                ],
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            height=400,
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📈 显示详细数据", expanded=False):
            st.dataframe(
                abnormal_df,
                use_container_width=True,
                column_config={
                    "核查项目": "核查项目",
                    "异常数量": st.column_config.NumberColumn("异常数量"),
                    "总记录数": st.column_config.NumberColumn("总记录数"),
                    "异常占比": st.column_config.NumberColumn(
                        "异常占比 (%)", format="%.1f%%"
                    ),
                },
                hide_index=True,
            )

        with st.expander("📊 核查明细详情", expanded=False):
            st.dataframe(st.session_state.df, hide_index=True)


#  数据导入
def data_import_view():

    # 数据上传功能
    uploaded_file = st.file_uploader("📁 数据导入", type=["xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file, header=1, engine="calamine")
            if st.button("📥 执行核查", type="primary", use_container_width=True):
                try:
                    with st.spinner("正在导入数据并执行核查..."):
                        # 创建核查器实例
                        checker = VehicleDataChecker(st.session_state.config)

                        # 使用上传的文件对象（不需要保存到本地）
                        df = checker.import_data(uploaded_file)

                        # 获取统计信息
                        stats = checker.get_statistics(df)

                        # 保存到session状态
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                        st.session_state.checker = checker
                        st.session_state.stats = stats

                        # 显示异常情况
                        abnormal_count = (df["异常数量"] > 0).sum()

                        st.success(f"✅ 数据导入和核查完成！共处理 {len(df)} 条记录。")
                        st.warning(f"⚠️ 发现 {abnormal_count} 条异常记录。")

                        st.subheader("📊 车辆核查明细")
                        st.dataframe(df, hide_index=False)

                except Exception as e:
                    st.error(f"❌ 导入数据时出错: {str(e)}")
                    st.exception(e)  # 显示详细错误信息


def display_province_category_analysis1():
    """显示按省份和异常类别的分析"""
    df = st.session_state.df

    # 检查核查列是否存在
    check_columns = ["工作时长核查", "公里数核查", "路桥费核查", "加班费核查"]
    available_checks = [col for col in check_columns if col in df.columns]

    # 检查核查列是否存在
    check_columns = ["工作时长核查", "公里数核查", "路桥费核查", "加班费核查"]
    available_checks = [col for col in check_columns if col in df.columns]

    if not available_checks:
        st.warning("数据中未找到核查列")
        return

    # 检查省份列是否存在
    province_columns = ["省"]
    province_col = None

    for col in province_columns:
        if col in df.columns:
            province_col = col
            break

    if not province_col:
        st.warning("数据中未找到省份信息，无法进行省份维度分析")
        return

    # 检查城市列是否存在
    city_columns = ["市"]
    city_col = None
    for col in city_columns:
        if col in df.columns:
            city_col = col
            break

    col1, col2, col3 = st.columns(3)
    with col1:
        # 获取所有省份
        all_provinces = df["省"].dropna().unique().tolist()
        province_options = ["全部"] + all_provinces
        selected_province = st.selectbox("选择省份", province_options, index=0)
    with col2:
        # 获取所有城市
        province_cities = (
            df[df["省"] == selected_province]["市"].dropna().unique().tolist()
        )
        city_options = ["全部"] + province_cities
        selected_city = st.selectbox("选择城市", city_options, index=0)
    with col3:
        selected_date = st.date_input(
            label="📆 请选择日期",  # 标签文本，支持emoji
            value=date.today(),  # 默认值
            min_value=date(1990, 1, 1),  # 最小可选日期
            format="YYYY-MM-DD",  # 日期格式
        )

    # 创建4个图表，每个核查项一个
    for check_col in available_checks:
        chart_title = check_col.replace("核查", "")
        with st.text(f"📊 {chart_title}异常"):
            abnormal_df = df[df[check_col] != "正常"].copy()
            if abnormal_df.empty:
                return
            # 按省份和异常类别分组统计
            category_stats = (
                abnormal_df.groupby([province_col, check_col])
                .size()
                .reset_index(name="数量")
            )

            # 获取所有异常类别
            categories = abnormal_df[check_col].unique()

            # 创建分组柱状图
            fig = go.Figure()

            # 为每个异常类别添加一个柱状图系列
            colors = px.colors.qualitative.Set3[: len(categories)]
            for i, category in enumerate(categories):
                category_data = category_stats[category_stats[check_col] == category]
                fig.add_trace(
                    go.Bar(
                        name=category,
                        x=category_data[province_col],
                        y=category_data["数量"],
                        text=category_data["数量"],
                        textposition="auto",
                        marker_color=colors[i],
                        hovertemplate=f"省份: %{{x}}<br>类别: {category}<br>数量: %{{y}}条<extra></extra>",
                    )
                )

            fig.update_layout(
                title=dict(
                    text=f"{chart_title} 异常类别分布",
                    font=dict(size=16, color="#1E293B"),
                    x=0.5,
                    xanchor="center",
                ),
                xaxis=dict(title="省份", tickangle=-45, tickfont=dict(size=12)),
                yaxis=dict(title="数量", gridcolor="lightgray"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                height=500,
                margin=dict(l=50, r=50, t=100, b=150),
                barmode="group",
                legend=dict(
                    yanchor="top",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    orientation="h",
                    font=dict(size=11),
                ),
            )
            # 显示图表
            st.plotly_chart(fig, use_container_width=True)


def compare_abnormal_types(df1, df2, start1, end1, start2, end2):
    """对比两个时间段的异常类型分布"""
    # 获取两个时间段的异常统计数据
    stats1 = {
        "工作时长": (df1["工作时长核查"] != "正常").sum(),
        "公里数": (df1["公里数核查"] != "正常").sum(),
        "路桥费": (df1["路桥费核查"] != "正常").sum(),
        "加班费": (df1["加班费核查"] != "正常").sum(),
    }

    stats2 = {
        "工作时长": (df2["工作时长核查"] != "normal").sum(),
        "公里数": (df2["公里数核查"] != "normal").sum(),
        "路桥费": (df2["路桥费核查"] != "normal").sum(),
        "加班费": (df2["加班费核查"] != "normal").sum(),
    }

    # 创建对比图表
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=list(stats1.keys()),
            y=list(stats1.values()),
            name=f"{start1}至{end1}",
            marker_color="#636EFA",
        )
    )
    fig.add_trace(
        go.Bar(
            x=list(stats2.keys()),
            y=list(stats2.values()),
            name=f"{start2}至{end2}",
            marker_color="#EF553B",
        )
    )

    fig.update_layout(
        title="异常类型对比",
        xaxis_title="异常类型",
        yaxis_title="异常数量",
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


def create_province_comparison_chart(df1, df2, start1, end1, start2, end2):
    """创建省份对比图表"""
    if "省" not in df1.columns or "省" not in df2.columns:
        return None

    # 使用更简洁的方法计算异常数量
    prov_stats = (
        df1[df1["异常数量"] > 0]
        .groupby("省")
        .size()
        .reset_index(name=f"{start1}_{end1}")
        .merge(
            df2[df2["异常数量"] > 0]
            .groupby("省")
            .size()
            .reset_index(name=f"{start2}_{end2}"),
            on="省",
            how="outer",
        )
        .fillna(0)
    )

    # 使用更简洁的图表创建方式
    fig = px.bar(
        prov_stats.melt(id_vars="省", var_name="时间段", value_name="异常数量"),
        x="省",
        y="异常数量",
        color="时间段",
        barmode="group",
        title="各省份异常数量对比",
        labels={"异常数量": "异常数量", "省": "省份"},
        color_discrete_map={
            f"{start1}_{end1}": "#636EFA",
            f"{start2}_{end2}": "#EF553B",
        },
    )

    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=-45, height=400
    )

    return fig


def create_abnormal_type_comparison_chart(df1, df2, start1, end1, start2, end2):
    """创建异常类型对比图表"""
    # 定义检查项目
    check_items = ["工作时长", "公里数", "路桥费", "加班费"]
    check_columns = [f"{item}核查" for item in check_items]

    # 使用列表推导式计算异常统计数据
    stats1 = {
        item: (df1[col] != "正常").sum()
        for item, col in zip(check_items, check_columns)
        if col in df1.columns
    }

    stats2 = {
        item: (df2[col] != "正常").sum()
        for item, col in zip(check_items, check_columns)
        if col in df2.columns
    }

    # 创建数据框用于绘图
    comparison_data = []
    for item in stats1.keys():
        comparison_data.append(
            {"异常类型": item, "异常数量": stats1[item], "时间段": f"{start1}至{end1}"}
        )
        comparison_data.append(
            {"异常类型": item, "异常数量": stats2[item], "时间段": f"{start2}至{end2}"}
        )

    if not comparison_data:
        return None

    comparison_df = pd.DataFrame(comparison_data)

    # 使用简洁的Plotly Express创建图表
    fig = px.bar(
        comparison_df,
        x="异常类型",
        y="异常数量",
        color="时间段",
        barmode="group",
        title="异常类型对比",
        labels={"异常数量": "异常数量", "异常类型": "异常类型"},
        color_discrete_map={
            f"{start1}至{end1}": "#636EFA",
            f"{start2}至{end2}": "#EF553B",
        },
    )

    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=400)

    return fig


def create_category_bar_chart(
    abnormal_df,
    check_col,
    group_col,
    chart_title,
    selected_province,
    selected_city,
    selected_date,
):
    """创建异常类别的分组柱状图"""
    # 按省份和异常类别分组统计
    category_stats = (
        abnormal_df.groupby([group_col, check_col]).size().reset_index(name="数量")
    )

    # 获取所有异常类别
    categories = abnormal_df[check_col].unique()

    # 如果类别太多，可以合并其他类别
    if len(categories) > 10:
        main_categories = categories[:8]
        other_df = abnormal_df[~abnormal_df[check_col].isin(main_categories)]
        if len(other_df) > 0:
            categories = list(main_categories) + ["其他"]
            other_df = other_df.copy()
            other_df[check_col] = "其他"
            abnormal_df = pd.concat(
                [
                    abnormal_df[abnormal_df[check_col].isin(main_categories)],
                    other_df,
                ]
            )
            category_stats = (
                abnormal_df.groupby([group_col, check_col])
                .size()
                .reset_index(name="数量")
            )

    # 创建分组柱状图
    fig = go.Figure()

    # 为每个异常类别添加一个柱状图系列
    colors = px.colors.qualitative.Set3[: len(categories)]

    for i, category in enumerate(categories):
        category_data = category_stats[category_stats[check_col] == category]

        # 如果没有数据，跳过
        if len(category_data) == 0:
            continue

        fig.add_trace(
            go.Bar(
                name=category,
                x=category_data[group_col],
                y=category_data["数量"],
                text=category_data["数量"],
                textposition="auto",
                marker_color=colors[i],
                hovertemplate=f"{group_col}: %{{x}}<br>类别: {category}<br>数量: %{{y}}条<extra></extra>",
            )
        )

    # 设置图表标题，包含筛选条件
    title_parts = [f"{chart_title}异常分布"]
    if selected_province != "全部":
        title_parts.append(f"省份: {selected_province}")
    if selected_city != "全部":
        title_parts.append(f"城市: {selected_city}")
    if selected_date:
        title_parts.append(f"日期: {selected_date}")

    fig.update_layout(
        title=dict(
            text=" | ".join(title_parts),
            font=dict(size=14, color="#1E293B"),
            x=0.5,
            xanchor="center",
        ),
        xaxis=dict(
            title=group_col, tickangle=-45, tickfont=dict(size=11), showgrid=False
        ),
        yaxis=dict(title="异常数量", gridcolor="rgba(211, 211, 211, 0.5)", gridwidth=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=400,
        margin=dict(l=50, r=50, t=80, b=120),
        barmode="group",
        legend=dict(
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            orientation="h",
            font=dict(size=10),
        ),
        showlegend=True,
    )
    return fig


def display_province_category_analysis():
    """显示按省份和异常类别的分析"""
    df = st.session_state.df

    # 检查核查列是否存在
    check_columns = ["工作时长核查", "公里数核查", "路桥费核查", "加班费核查"]
    available_checks = [col for col in check_columns if col in df.columns]

    if not available_checks:
        st.warning("数据中未找到核查列")
        return

    # 检查省份列是否存在
    province_columns = ["省"]
    province_col = None

    for col in province_columns:
        if col in df.columns:
            province_col = col
            break

    if not province_col:
        st.warning("数据中未找到省份信息，无法进行省份维度分析")
        return

    # 检查城市列是否存在
    city_columns = ["市"]
    city_col = None
    for col in city_columns:
        if col in df.columns:
            city_col = col
            break

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # 获取所有省份
        all_provinces = df["省"].dropna().unique().tolist()
        province_options = ["全部"] + all_provinces
        selected_province = st.selectbox("选择省份", province_options, index=0)

    with col2:
        # 根据选择的省份获取城市
        if selected_province != "全部":
            province_cities = (
                df[df["省"] == selected_province]["市"].dropna().unique().tolist()
            )
        else:
            province_cities = df["市"].dropna().unique().tolist()

        city_options = ["全部"] + province_cities
        selected_city = st.selectbox("选择城市", city_options, index=0)

    with col3:
        # 检查是否有日期列
        if "日期" in df.columns:
            # 获取最小和最大日期
            min_date = df["日期"].min().date()
            max_date = df["日期"].max().date()

            # 时间段1选择器
            date_range1 = st.date_input(
                "选择时间段1",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="date_range1",
            )

            if len(date_range1) == 2:
                start_date1, end_date1 = date_range1
            else:
                start_date1, end_date1 = min_date, max_date
        else:
            st.info("数据中没有日期列")
            start_date1, end_date1 = None, None

    with col4:
        # 时间段2选择器
        if "日期" in df.columns:
            date_range2 = st.date_input(
                "选择时间段2",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="date_range2",
            )

            if len(date_range2) == 2:
                start_date2, end_date2 = date_range2
            else:
                start_date2, end_date2 = min_date, max_date
        else:
            st.info("数据中没有日期列")
            start_date2, end_date2 = None, None

    # 单独一行显示时间段2应用开关
    apply_period2 = st.checkbox(
        "📊 应用时间段2数据进行对比分析",
        key="apply_period2",
        help="勾选后将使用时间段2数据进行对比分析",
    )

    # 根据选择的条件筛选数据
    filtered_df = df.copy()
    filtered_df2 = df.copy()

    # 省份筛选
    if selected_province != "全部":
        filtered_df = filtered_df[filtered_df["省"] == selected_province]
        filtered_df2 = filtered_df2[filtered_df2["省"] == selected_province]

    # 城市筛选
    if selected_city != "全部":
        filtered_df = filtered_df[filtered_df["市"] == selected_city]
        filtered_df2 = filtered_df2[filtered_df2["市"] == selected_city]

    # 日期筛选 - 时间段1
    if start_date1 and end_date1 and "日期" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["日期"].dt.date >= start_date1)
            & (filtered_df["日期"].dt.date <= end_date1)
        ]

    # 日期筛选 - 时间段2（如果启用）
    if apply_period2 and start_date2 and end_date2 and "日期" in filtered_df2.columns:
        filtered_df2 = filtered_df2[
            (filtered_df2["日期"].dt.date >= start_date2)
            & (filtered_df2["日期"].dt.date <= end_date2)
        ]
    elif apply_period2:
        filtered_df2 = pd.DataFrame()  # 如果没有时间段2数据，设置为空

    # 显示筛选结果统计
    if selected_province == "全部" and selected_city == "全部":
        st.info(f"📈 时间段1: {len(filtered_df)} 条记录。")
        if apply_period2:
            st.info(f"📈 时间段2: {len(filtered_df2)} 条记录。")
    else:
        # 筛选出4列都不为"正常"的数据
        condition = (
            (filtered_df["工作时长核查"] != "正常")
            | (filtered_df["公里数核查"] != "正常")
            | (filtered_df["路桥费核查"] != "正常")
            | (filtered_df["加班费核查"] != "正常")
        )
        abnormal_all_df = filtered_df[condition].copy()

        # 显示筛选后的数据统计
        st.info(
            f"📈 时间段1: {len(filtered_df)} 条记录，异常记录{len(abnormal_all_df)}条。"
        )

        if apply_period2:
            condition2 = (
                (filtered_df2["工作时长核查"] != "正常")
                | (filtered_df2["公里数核查"] != "正常")
                | (filtered_df2["路桥费核查"] != "正常")
                | (filtered_df2["加班费核查"] != "正常")
            )
            abnormal_all_df2 = filtered_df2[condition2].copy()
            st.info(
                f"📈 时间段2: {len(filtered_df2)} 条记录，异常记录{len(abnormal_all_df2)}条。"
            )

        with st.expander("异常记录详情", expanded=False):
            st.dataframe(abnormal_all_df, hide_index=True)

    # 如果没有数据，显示提示
    if len(filtered_df) == 0:
        st.warning("没有找到时间段1符合条件的记录")
        return

    # 确定分组列
    if selected_city != "全部":
        group_col = "市"
    elif selected_province != "全部":
        group_col = "市"
    else:
        group_col = "省"
    # ========== 小计平均值分析（在工作时长异常分析前） ==========
    if "小计" in df.columns:
        st.markdown("### 💰 平均车辆费用对比分析")
        st.markdown(
            f"**筛选条件 - 省份: {selected_province} | 城市: {selected_city} | "
            f"时间段1: {start_date1} 至 {end_date1} | "
            f"时间段2: {start_date2} 至 {end_date2}**"
        )

        # 筛选小计不为0的数据
        valid_df1 = filtered_df[filtered_df["小计"] != 0].copy()

        # 时间段1的小计平均值按省市分组
        if not valid_df1.empty:
            period1_stats = (
                valid_df1.groupby([group_col, "日期"])["小计"].mean().reset_index()
            )

            # 按省市汇总平均值
            period1_summary = (
                period1_stats.groupby(group_col)["小计"].mean().reset_index()
            )
            period1_summary.columns = [group_col, "时间段1小计平均值"]

            # 创建时间段1的折线图
            fig1 = go.Figure()
            fig1.add_trace(
                go.Scatter(
                    x=period1_summary[group_col],
                    y=period1_summary["时间段1小计平均值"],
                    mode="lines+markers+text",
                    name=f"时间段1 ({start_date1} 至 {end_date1})",
                    line=dict(color="#636EFA", width=3, shape="spline", smoothing=1.3),
                    marker=dict(size=8, color="#636EFA"),
                    text=period1_summary["时间段1小计平均值"].round(2),
                    textposition="top center",
                    textfont=dict(size=10),
                )
            )
            fig1.update_layout(
                title=f"时间段1 ({start_date1} 至 {end_date1}) 小计平均值",
                xaxis_title="地区",
                yaxis_title="小计平均值",
                xaxis_tickangle=-45,
                height=400,
                plot_bgcolor="white",
                paper_bgcolor="white",
                hovermode="x unified",
            )

        # 时间段2的小计平均值
        if apply_period2 and len(filtered_df2) > 0:
            valid_df2 = filtered_df2[filtered_df2["小计"] != 0].copy()

            if not valid_df2.empty:
                period2_stats = (
                    valid_df2.groupby([group_col, "日期"])["小计"].mean().reset_index()
                )
                period2_summary = (
                    period2_stats.groupby(group_col)["小计"].mean().reset_index()
                )
                period2_summary.columns = [group_col, "时间段2小计平均值"]

                # 合并两个时间段的数据
                combined_summary = pd.merge(
                    period1_summary, period2_summary, on=group_col, how="outer"
                ).fillna(0)
                # 创建双折线图对比
                fig_combined = go.Figure()

                fig_combined.add_trace(
                    go.Scatter(
                        x=combined_summary[group_col],
                        y=combined_summary["时间段1小计平均值"],
                        mode="lines+markers+text",
                        name=f"时间段1 ({start_date1} 至 {end_date1})",
                        line=dict(
                            color="#636EFA", width=3, shape="spline", smoothing=1.3
                        ),
                        marker=dict(size=8, color="#636EFA"),
                        text=combined_summary["时间段1小计平均值"].round(2),
                        textposition="top center",
                        textfont=dict(size=10),
                    )
                )

                fig_combined.add_trace(
                    go.Scatter(
                        x=combined_summary[group_col],
                        y=combined_summary["时间段2小计平均值"],
                        mode="lines+markers+text",
                        name=f"时间段2 ({start_date2} 至 {end_date2})",
                        line=dict(
                            color="#EF553B", width=3, shape="spline", smoothing=1.3
                        ),
                        marker=dict(size=8, color="#EF553B"),
                        text=combined_summary["时间段2小计平均值"].round(2),
                        textposition="top center",
                        textfont=dict(size=10),
                    )
                )

                fig_combined.update_layout(
                    title="📊 平均车辆费用对比分析",
                    xaxis_title="地区",
                    yaxis_title="小计平均值",
                    xaxis_tickangle=-45,
                    height=500,
                    plot_bgcolor="white",
                    paper_bgcolor="white",
                    hovermode="x unified",
                    legend=dict(
                        yanchor="top", y=-0.25, xanchor="center", x=0.5, orientation="h"
                    ),
                )

                st.plotly_chart(fig_combined, use_container_width=True)

            else:
                st.info("时间段2无有效数据")
        else:
            # 只显示时间段1的图表
            if not valid_df1.empty:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("时间段1无有效数据")

        # 显示汇总数据表
        with st.expander("📋 小计平均值汇总数据", expanded=False):
            if apply_period2 and len(filtered_df2) > 0 and not valid_df2.empty:
                st.dataframe(
                    combined_summary, use_container_width=True, hide_index=True
                )
            elif not valid_df1.empty:
                st.dataframe(period1_summary, use_container_width=True, hide_index=True)

        st.markdown("---")

    # 创建4个图表，每个核查项一个
    for check_col in available_checks:
        chart_title = check_col.replace("核查", "")

        # 创建子标题
        st.markdown(f"### 📊 {chart_title}异常分析")

        if apply_period2 and len(filtered_df2) > 0:
            # ========== 时间段对比模式 ==========
            st.markdown(
                f"**时间段1 ({start_date1} 至 {end_date1}) vs 时间段2 ({start_date2} 至 {end_date2})**"
            )

            # 筛选两个时间段的异常数据
            abnormal_df1 = filtered_df[filtered_df[check_col] != "正常"].copy()
            abnormal_df2 = filtered_df2[filtered_df2[check_col] != "正常"].copy()

            # 创建双列布局显示两个时间段
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"#### 时间段1")
                if not abnormal_df1.empty:
                    # 按省市分组统计
                    stats1 = (
                        abnormal_df1.groupby([group_col, check_col])
                        .size()
                        .reset_index(name="数量")
                    )

                    categories1 = abnormal_df1[check_col].unique()

                    fig1 = go.Figure()
                    colors = px.colors.qualitative.Set3[: len(categories1)]

                    for i, category in enumerate(categories1):
                        cat_data = stats1[stats1[check_col] == category]
                        if len(cat_data) > 0:
                            fig1.add_trace(
                                go.Bar(
                                    name=category,
                                    x=cat_data[group_col],
                                    y=cat_data["数量"],
                                    text=cat_data["数量"],
                                    textposition="auto",
                                    marker_color=colors[i],
                                )
                            )

                    fig1.update_layout(
                        title=f"{chart_title}异常分布",
                        xaxis_title=group_col,
                        yaxis_title="异常数量",
                        barmode="group",
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        xaxis_tickangle=-45,
                        height=350,
                    )
                    st.plotly_chart(
                        fig1,
                        use_container_width=True,
                        key=f"period1_{check_col}_{group_col}",
                    )

            with col2:
                st.markdown(f"#### 时间段2")
                if not abnormal_df2.empty:
                    # 按省市分组统计
                    stats2 = (
                        abnormal_df2.groupby([group_col, check_col])
                        .size()
                        .reset_index(name="数量")
                    )

                    categories2 = abnormal_df2[check_col].unique()

                    fig2 = go.Figure()
                    colors = px.colors.qualitative.Set3[: len(categories2)]

                    for i, category in enumerate(categories2):
                        cat_data = stats2[stats2[check_col] == category]
                        if len(cat_data) > 0:
                            fig2.add_trace(
                                go.Bar(
                                    name=category,
                                    x=cat_data[group_col],
                                    y=cat_data["数量"],
                                    text=cat_data["数量"],
                                    textposition="auto",
                                    marker_color=colors[i],
                                )
                            )

                    fig2.update_layout(
                        title=f"{chart_title}异常分布",
                        xaxis_title=group_col,
                        yaxis_title="异常数量",
                        barmode="group",
                        plot_bgcolor="white",
                        paper_bgcolor="white",
                        xaxis_tickangle=-45,
                        height=350,
                    )
                    st.plotly_chart(
                        fig2,
                        use_container_width=True,
                        key=f"period2_{check_col}_{group_col}",
                    )
                else:
                    st.info("该时间段无异常记录")

            # 合并时间段1和时间段2的数据
            abnormal_df1["时间段"] = f"{start_date1} 至 {end_date1}"
            abnormal_df2["时间段"] = f"{start_date2} 至 {end_date2}"
            combined_abnormal_df = pd.concat([abnormal_df1, abnormal_df2])

            with st.expander(f"{chart_title}异常详细数据 (合并显示)"):
                st.dataframe(combined_abnormal_df.sort_index(), hide_index=True)

            # 添加汇总对比表
            st.markdown("#### 📊 汇总对比")
            summary_data = []

            # 时间段1汇总
            if selected_city != "全部":
                period1_by_region = (
                    abnormal_df1.groupby("市").size().reset_index(name="时间段1异常数")
                )
            elif selected_province != "全部":
                period1_by_region = (
                    abnormal_df1.groupby("市").size().reset_index(name="时间段1异常数")
                )
            else:
                period1_by_region = (
                    abnormal_df1.groupby("省").size().reset_index(name="时间段1异常数")
                )

            # 时间段2汇总
            if selected_city != "全部":
                period2_by_region = (
                    abnormal_df2.groupby("市").size().reset_index(name="时间段2异常数")
                )
            elif selected_province != "全部":
                period2_by_region = (
                    abnormal_df2.groupby("市").size().reset_index(name="时间段2异常数")
                )
            else:
                period2_by_region = (
                    abnormal_df2.groupby("省").size().reset_index(name="时间段2异常数")
                )

            # 合并汇总
            if selected_city != "全部":
                region_col = "市"
            elif selected_province != "全部":
                region_col = "市"
            else:
                region_col = "省"

            summary_df = pd.merge(
                period1_by_region.rename(columns={region_col: region_col}),
                period2_by_region.rename(columns={region_col: region_col}),
                on=region_col,
                how="outer",
            ).fillna(0)
            summary_df["时间段1异常数"] = summary_df["时间段1异常数"].astype(int)
            summary_df["时间段2异常数"] = summary_df["时间段2异常数"].astype(int)

            st.dataframe(summary_df, use_container_width=True)

        else:
            # ========== 单时间段模式 ==========
            # 筛选异常数据
            abnormal_df = filtered_df[filtered_df[check_col] != "正常"].copy()

            if abnormal_df.empty:
                st.write(f"✅ 当前筛选条件下没有{chart_title}异常记录")
                st.divider()
                continue

            # 按省份和异常类别分组统计
            category_stats = (
                abnormal_df.groupby([group_col, check_col])
                .size()
                .reset_index(name="数量")
            )

            # 获取所有异常类别
            categories = abnormal_df[check_col].unique()

            # 如果类别太多，可以合并其他类别
            if len(categories) > 10:
                main_categories = categories[:8]
                other_df = abnormal_df[~abnormal_df[check_col].isin(main_categories)]
                if len(other_df) > 0:
                    categories = list(main_categories) + ["其他"]
                    other_df = other_df.copy()
                    other_df[check_col] = "其他"
                    abnormal_df = pd.concat(
                        [
                            abnormal_df[abnormal_df[check_col].isin(main_categories)],
                            other_df,
                        ]
                    )
                    category_stats = (
                        abnormal_df.groupby([group_col, check_col])
                        .size()
                        .reset_index(name="数量")
                    )

            # 使用函数创建图表
            fig = create_category_bar_chart(
                abnormal_df,
                check_col,
                group_col,
                chart_title,
                selected_province,
                selected_city,
                f"{start_date1} 至 {end_date1}",
            )

            # 显示图表
            st.plotly_chart(fig, use_container_width=True)
            default_columns = [
                "日期",
                "车牌号码",
                "驾驶员名称",
                "路桥费",
                "停车费",
                "加班费",
                "开始时间",
                "结束时间",
                "行驶里程",
                "开始公里数",
                "结束公里数",
                "小计",
                "上传人姓名",
                "供应商名称",
                "省",
                "市",
                "一级项目名称",
                "二级项目名称",
                "工作时长",
                "工作时长核查",
                "公里数核查",
                "路桥费核查",
                "加班费核查",
            ]
            # 显示详细数据表格
            with st.expander(f"📋 查看{chart_title}异常详细数据"):
                st.dataframe(abnormal_df[default_columns], hide_index=True)

        st.divider()


# 创建筛选项
def create_filters():
    pass


# 应用筛选项
def apply_filters():
    pass


def main():
    # 检查是否需要返回首页
    if st.session_state.get("return_to_home", False):
        st.session_state.return_to_home = False
        st.rerun()  # 确保页面完全刷新

    # 页面配置
    setup_page("车辆分析")

    # 使用组件中的侧边栏导航
    create_sidebar_navigation()

    # 初始化配置
    init_data()

    # 页面头部
    create_header("车辆出勤分析", "数据核查与异常检测", "🚗")

    # 创建主标签页：数据导入、数据分析和时间对比
    tab1, tab2 = st.tabs(["📁 数据导入", "📈 数据分析"])

    # ========== Tab 1: 数据导入 ==========
    with tab1:
        with st.expander("### ⚙️ 门限设置", expanded=False):
            configView_set()
        st.markdown("---")
        st.markdown("### 📁 数据导入")
        data_import_view()

    # ========== Tab 2: 数据分析 ==========
    with tab2:
        if st.session_state.data_loaded and st.session_state.df is not None:
            # 数据总览部分
            st.markdown("### 📊 数据总览")
            data_board_view()
            st.markdown("---")

            # 异常数据分析
            st.markdown("### 📈 异常数据分析")
            abnormal_data_view()
            st.markdown("---")

            # 部门维度分析（合并到数据总览后面）
            st.markdown("### 🔍 详细分析")
            display_province_category_analysis()
        else:
            st.info("请先导入数据以查看分析结果")


if __name__ == "__main__":
    main()
