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

    # 创建异常占比数据表
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

        # 创建异常占比柱状图
        fig = go.Figure(
            data=[
                go.Bar(
                    x=abnormal_df["核查项目"],
                    y=abnormal_df["异常占比"],
                    text=[f"{rate:.1f}%" for rate in abnormal_df["异常占比"]],
                    textposition="outside",
                    marker_color=px.colors.qualitative.Set3[: len(abnormal_df)],
                    hovertemplate="%{x}<br>异常占比: %{y:.1f}%<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=dict(
                text="各项核查异常占比对比",
                font=dict(size=16, color="#1E293B"),
                x=0.5,
                xanchor="center",
            ),
            xaxis=dict(title="核查项目", tickfont=dict(size=12)),
            yaxis=dict(
                title="异常占比 (%)",
                gridcolor="lightgray",
                range=[
                    0,
                    max(abnormal_df["异常占比"]) * 1.5 if len(abnormal_df) > 0 else 100,
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
            )


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

    col1, col2, col3 = st.columns(3)
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
            selected_date = st.date_input(
                label="📆 选择日期",
                value=None,  # 默认为空，表示选择全部
                min_value=min_date,
                max_value=max_date,
                format="YYYY-MM-DD",
            )
        else:
            st.info("数据中没有日期列")
            selected_date = None

    # 根据选择的条件筛选数据
    filtered_df = df.copy()

    # 省份筛选
    if selected_province != "全部":
        filtered_df = filtered_df[filtered_df["省"] == selected_province]

    # 城市筛选
    if selected_city != "全部":
        filtered_df = filtered_df[filtered_df["市"] == selected_city]

    # 日期筛选
    if selected_date and "日期" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["日期"].dt.date == selected_date]

    if selected_province == "全部" and selected_city == "全部":
        st.info(f"📈 当前: {len(filtered_df)} 条记录。")
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
            f"📈 当前筛选结果: {len(filtered_df)} 条记录，异常记录{len(abnormal_all_df)}条。"
        )

        with st.expander("异常记录详情", expanded=False):
            st.dataframe(abnormal_all_df, hide_index=True)

    # 如果没有数据，显示提示
    if len(filtered_df) == 0:
        st.warning("没有找到符合条件的记录")
        return

    # 创建4个图表，每个核查项一个
    for check_col in available_checks:
        chart_title = check_col.replace("核查", "")

        # 创建子标题
        st.markdown(f"### 📊 {chart_title}异常分析")

        # 筛选异常数据
        abnormal_df = filtered_df[filtered_df[check_col] != "正常"].copy()

        if abnormal_df.empty:
            st.write(f"✅ 当前筛选条件下没有{chart_title}异常记录")
            st.divider()
            continue

        # 按省份和异常类别分组统计
        if selected_city != "全部":
            # 如果选择了具体城市，按城市分组
            group_col = "市"
        elif selected_province != "全部":
            # 如果选择了具体省份，按城市分组
            group_col = "市"
        else:
            # 如果选择"全部"，按省份分组
            group_col = "省"

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
            yaxis=dict(
                title="异常数量", gridcolor="rgba(211, 211, 211, 0.5)", gridwidth=1
            ),
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

        # 显示图表
        st.plotly_chart(fig, use_container_width=True)
        default_columns = [
            "日期",
            "车牌号码",
            "驾驶员名称",
            "路桥费",
            "停车费",
            "加班费",
            # "只打卡不出车",
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
            # 只显示关键列
            # display_cols = ['日期', '省', '市'] if '日期' in abnormal_df.columns else ['省', '市']
            # display_cols.append(check_col)

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

    # 创建主标签页：数据导入和数据看板
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

            # 异常占比分析
            st.markdown("### 📈 异常占比分析")
            abnormal_data_view()
            st.markdown("---")

            # 部门维度分析（合并到数据总览后面）
            st.markdown("### 🔍 部门维度分析")
            display_province_category_analysis()
        else:
            st.info("请先导入数据以查看分析结果")


if __name__ == "__main__":
    main()
