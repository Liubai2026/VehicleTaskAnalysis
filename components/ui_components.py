import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
from core.data_services import FilterService


class FilterComponents:
    """筛选器组件"""
    
    @staticmethod
    def create_trend_filters(df, key_prefix="trend") -> Dict[str, Any]:
        """创建趋势分析筛选器"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        filters = {}
        
        with col1:
            provinces = FilterService.get_filter_options(df, {})["provinces"]
            filters["province"] = st.selectbox(
                "选择省份", options=provinces, key=f"{key_prefix}_province"
            )
        
        with col2:
            options = FilterService.get_filter_options(df, {"province": filters["province"]})
            filters["city"] = st.selectbox(
                "选择城市", options=options["cities"], key=f"{key_prefix}_city"
            )
        
        with col3:
            options = FilterService.get_filter_options(df, {
                "province": filters["province"],
                "city": filters["city"]
            })
            filters["uploader"] = st.selectbox(
                "选择上传人", options=options["uploaders"], key=f"{key_prefix}_uploader"
            )
        
        with col4:
            # 日期范围选择器
            if "日期" in df.columns:
                date_min = df["日期"].min() if not df["日期"].isna().all() else pd.Timestamp("2024-01-01")
                date_max = df["日期"].max() if not df["日期"].isna().all() else pd.Timestamp("2024-12-31")
                
                selected_dates = st.date_input(
                    "选择日期范围",
                    value=(date_min.date(), date_max.date()),
                    key=f"{key_prefix}_date_range"
                )
                
                if len(selected_dates) == 2:
                    filters["start_date"], filters["end_date"] = selected_dates
        
        with col5:
            filters["top_n"] = st.number_input(
                "显示TOP数量",
                min_value=1,
                max_value=50,
                value=10,
                step=1,
                key=f"{key_prefix}_top_n"
            )
        
        return filters
    
    @staticmethod
    def create_simple_filters(df, filter_types: List[str], key_prefix="filter") -> Dict[str, Any]:
        """创建简单筛选器"""
        cols = st.columns(len(filter_types))
        filters = {}
        
        for i, filter_type in enumerate(filter_types):
            with cols[i]:
                if filter_type == "province":
                    options = ["全部"] + sorted(df["省"].dropna().unique()) if "省" in df.columns else ["全部"]
                    filters["province"] = st.selectbox(
                        "选择省份", options=options, key=f"{key_prefix}_province"
                    )
                elif filter_type == "city":
                    options = FilterService.get_filter_options(df, filters)["cities"]
                    filters["city"] = st.selectbox(
                        "选择城市", options=options, key=f"{key_prefix}_city"
                    )
                elif filter_type == "date_range":
                    if "日期" in df.columns:
                        date_min = df["日期"].min() if not df["日期"].isna().all() else pd.Timestamp("2024-01-01")
                        date_max = df["日期"].max() if not df["日期"].isna().all() else pd.Timestamp("2024-12-31")
                        
                        selected_dates = st.date_input(
                            "选择日期范围",
                            value=(date_min.date(), date_max.date()),
                            key=f"{key_prefix}_date_range"
                        )
                        
                        if len(selected_dates) == 2:
                            filters["start_date"], filters["end_date"] = selected_dates
        
        return filters


class ChartComponents:
    """图表显示组件"""
    
    @staticmethod
    def display_trend_chart(fig, title: str = "趋势图"):
        """显示趋势图表"""
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("无法生成图表")
    
    @staticmethod
    def display_dataframe(df, title: str = "数据详情", expanded: bool = False):
        """显示数据表格"""
        with st.expander(title, expanded=expanded):
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("暂无数据")
    
    @staticmethod
    def display_metrics(df, metric_configs: List[Dict]):
        """显示指标卡片"""
        cols = st.columns(len(metric_configs))
        for i, config in enumerate(metric_configs):
            with cols[i]:
                value = config["calculator"](df)
                st.metric(label=config["label"], value=value)


class FileUploadComponents:
    """文件上传组件"""
    
    @staticmethod
    def create_file_uploaders():
        """创建文件上传器"""
        col1, col2 = st.columns(2)
        uploaded_files = {}
        
        with col1:
            st.markdown("#### 📋 人员信息文件")
            uploaded_files["personnel"] = st.file_uploader(
                "选择人员明细信息文件 (Excel)",
                type=["xlsx"],
                key="personnel_file"
            )
            uploaded_files["employee"] = st.file_uploader(
                "选择员工资源文件 (Excel)",
                type=["xlsx"],
                key="employee_file"
            )
        
        with col2:
            st.markdown("#### 🚗 车辆与任务文件")
            uploaded_files["vehicle"] = st.file_uploader(
                "选择车辆出勤记录文件 (Excel)",
                type=["xlsx"],
                key="vehicle_file"
            )
            uploaded_files["task"] = st.file_uploader(
                "选择工单履行率文件 (Excel)",
                type=["xlsx"],
                key="task_file"
            )
        
        return uploaded_files
    
    @staticmethod
    def validate_uploaded_files(uploaded_files: Dict) -> bool:
        """验证上传的文件"""
        missing_files = []
        for file_type, file_obj in uploaded_files.items():
            if not file_obj:
                missing_files.append(file_type)
        
        if missing_files:
            st.warning(f"请上传以下文件: {', '.join(missing_files)}")
            return False
        return True


class LayoutComponents:
    """布局组件"""
    
    @staticmethod
    def create_section_header(title: str, description: str = "", icon: str = ""):
        """创建区域标题"""
        if icon:
            st.markdown(f"### {icon} {title}")
        else:
            st.markdown(f"### {title}")
        
        if description:
            st.markdown(description)
        st.markdown("---")
    
    @staticmethod
    def create_tabs(tab_names: List[str]) -> Dict:
        """创建标签页"""
        tabs = st.tabs([f"📁 {name}" if i == 0 else f"📊 {name}" for i, name in enumerate(tab_names)])
        return {name: tab for name, tab in zip(tab_names, tabs)}
    
    @staticmethod
    def create_info_message(message: str, message_type: str = "info"):
        """创建信息提示"""
        if message_type == "success":
            st.success(message)
        elif message_type == "warning":
            st.warning(message)
        elif message_type == "error":
            st.error(message)
        else:
            st.info(message)


class DataSummaryComponents:
    """数据汇总组件"""
    
    @staticmethod
    def display_data_preview(df, num_rows: int = 10):
        """显示数据预览"""
        st.markdown("### 📋 数据预览")
        st.dataframe(df.head(num_rows), use_container_width=True)
    
    @staticmethod
    def display_basic_metrics(df):
        """显示基础指标"""
        st.markdown("### 📊 数据统计")
        cols = st.columns(4)
        
        with cols[0]:
            st.metric("总记录数", len(df))
        
        with cols[1]:
            date_count = df["日期"].nunique() if "日期" in df.columns else 0
            st.metric("日期范围", f"{date_count} 天")
        
        with cols[2]:
            person_count = df["Uniportal账号"].nunique() if "Uniportal账号" in df.columns else 0
            st.metric("涉及人员", person_count)
        
        with cols[3]:
            vehicle_count = df["车牌号"].nunique() if "车牌号" in df.columns else "N/A"
            st.metric("涉及车辆", vehicle_count)