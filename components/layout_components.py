# components/layout_components.py
import streamlit as st
from typing import Dict, Any, Optional, Union, List
from config import PAGES_CONFIG, SYSTEM_CONSTANTS


def setup_page(
    title: str = "内控管理分析系统",
    layout: str = "wide",
    initial_sidebar_state: str = "expanded",
):
    """设置页面配置"""
    page_title = (
        f"{SYSTEM_CONSTANTS['APP_NAME']} - {title}"
        if title
        else SYSTEM_CONSTANTS["APP_NAME"]
    )

    st.set_page_config(
        page_title=page_title,
        page_icon="🚗",
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
        menu_items={
            "Get Help": f'mailto:{SYSTEM_CONSTANTS["SUPPORT_EMAIL"]}',
            "Report a bug": f'mailto:{SYSTEM_CONSTANTS["SUPPORT_EMAIL"]}',
            "About": f"""
            ## {SYSTEM_CONSTANTS['APP_NAME']}
            版本: {SYSTEM_CONSTANTS['VERSION']}
            
            数据驱动的车辆管理与工单分析平台
            
            © 2024 技术支持: {SYSTEM_CONSTANTS['SUPPORT_EMAIL']}
            """,
        },
    )

    # 添加自定义CSS
    st.markdown(
        """
    <style>
        /* 主容器样式 */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* 按钮样式 */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* 指标卡片样式 */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
        }
        
        /* 表格样式 */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* 侧边栏样式 */
        section[data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        /* 进度条样式 */
        .stProgress > div > div > div > div {
            background-color: #1E88E5;
        }
        
        /* 警告框样式 */
        .stAlert {
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 12px 24px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def create_sidebar_navigation():
    """创建侧边栏导航"""
    # 隐藏默认导航
    st.markdown(
        """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("🔧 导航菜单", text_alignment="center")
        st.markdown("---")

        # 动态生成导航按钮
        for page_name, page_info in PAGES_CONFIG.items():
            icon = page_info.get("icon", "📄")
            page_file = page_info.get("file")

            # 直接使用按钮，不使用 HTML
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                # help=f"跳转到{page_name}",
            ):
                try:
                    st.switch_page(f"pages/{page_file}")
                except Exception as e:
                    st.error(f"页面跳转失败: {e}")

        st.markdown("---")

        # 返回首页
        if st.button("🏠 返回首页", use_container_width=True):
            st.switch_page("app.py")


def create_header(
    title: str, subtitle: str = "", icon: str = "🚗", show_breadcrumb: bool = True
):
    """创建页面头部"""
    # 标题行
    col1, col2 = st.columns([1, 20])
    with col1:
        st.markdown(f"# {icon}")
    with col2:
        st.markdown(f"# {title}")

    # 副标题
    if subtitle:
        st.markdown(f"*{subtitle}*")


def create_metric_card(
    title: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,
    icon: str = "📈",
    color: str = "blue",
    help_text: Optional[str] = None,
    use_container: bool = True,
):
    """创建指标卡片"""
    if use_container:
        with st.container():
            _display_metric(title, value, delta, icon, color, help_text)
    else:
        _display_metric(title, value, delta, icon, color, help_text)


def _display_metric(title, value, delta, icon, color, help_text):
    """显示单个指标"""
    col1, col2 = st.columns([4, 1])

    with col1:
        if help_text:
            st.markdown(f"**{icon} {title}**")
            st.caption(help_text)
        else:
            st.markdown(f"**{icon} {title}**")

        st.markdown(
            f"<h2 style='margin-top: 5px; margin-bottom: 5px;'>{value}</h2>",
            unsafe_allow_html=True,
        )

    with col2:
        if delta:
            delta_color = (
                "green"
                if delta.startswith("+")
                else "red" if delta.startswith("-") else "gray"
            )
            st.markdown(
                f"<div style='text-align: center; padding: 10px 0; color: {delta_color}; font-weight: bold;'>{delta}</div>",
                unsafe_allow_html=True,
            )


def create_simple_metric(
    label: str,
    value: Union[str, int, float],
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
):
    """使用 Streamlit 原生的 metric 组件"""
    return st.metric(label=label, value=value, delta=delta, help=help_text)


def create_info_box(message: str, type: str = "info", icon: str = None):
    """创建信息提示框"""
    # 设置默认图标
    if icon is None:
        icon_map = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        icon = icon_map.get(type, "ℹ️")

    # 使用对应的Streamlit组件
    if type == "info":
        st.info(f"{icon} {message}")
    elif type == "success":
        st.success(f"{icon} {message}")
    elif type == "warning":
        st.warning(f"{icon} {message}")
    elif type == "error":
        st.error(f"{icon} {message}")
    else:
        st.info(f"{icon} {message}")


def create_card(title: str, content: str, icon: str = "📦", expanded: bool = True):
    """创建卡片"""
    with st.expander(f"{icon} {title}", expanded=expanded):
        st.markdown(content)


def create_feature_card(title: str, items: List[str], icon: str = "✓"):
    """创建功能卡片"""
    with st.container():
        st.markdown(f"**{icon} {title}**")
        for item in items:
            st.markdown(f"- {item}")
        st.markdown("---")


def create_navigation_buttons():
    """创建导航按钮组"""
    st.markdown("### 🚀 快速导航")

    cols = st.columns(len(PAGES_CONFIG))

    for idx, (page_name, page_info) in enumerate(PAGES_CONFIG.items()):
        with cols[idx]:
            icon = page_info.get("icon", "📄")
            page_file = page_info.get("file")
            description = page_info.get("description", "")

            if st.button(
                f"{icon}\n**{page_name}**",
                key=f"quick_nav_{page_name}",
                use_container_width=True,
                help=description,
            ):
                st.switch_page(f"pages/{page_file}")


def create_stats_dashboard(show_demo_data: bool = True):
    """创建统计仪表板"""
    st.markdown("### 📊 系统统计")

    # 使用多列布局显示统计指标
    cols = st.columns(4)

    if show_demo_data:
        # 演示数据
        stats = [
            {"label": "总记录数", "value": "12,345", "icon": "📊", "delta": "+5.2%"},
            {"label": "异常记录", "value": "234", "icon": "⚠️", "delta": "-2.1%"},
            {"label": "处理完成", "value": "98.5%", "icon": "✅", "delta": "+0.5%"},
            {"label": "活跃用户", "value": "156", "icon": "👥", "delta": "+12"},
        ]
    else:
        # 实际数据（可以从session state获取）
        stats = [
            {"label": "总记录数", "value": "0", "icon": "📊"},
            {"label": "异常记录", "value": "0", "icon": "⚠️"},
            {"label": "处理完成", "value": "0%", "icon": "✅"},
            {"label": "今日处理", "value": "0", "icon": "🚀"},
        ]

    for idx, stat in enumerate(stats):
        with cols[idx]:
            create_simple_metric(
                label=f"{stat['icon']} {stat['label']}",
                value=stat["value"],
                delta=stat.get("delta"),
            )


def create_loading_spinner(text: str = "处理中..."):
    """创建加载动画"""
    with st.spinner(text):
        pass


def create_progress_bar(total: int, current: int, label: str = "进度"):
    """创建进度条"""
    progress = current / total if total > 0 else 0
    st.progress(progress, text=f"{label}: {current}/{total} ({progress:.1%})")


def create_column_layout(num_columns: int = 2, ratios: List[float] = None):
    """创建列布局"""
    if ratios and len(ratios) == num_columns:
        return st.columns(ratios)
    else:
        return st.columns(num_columns)


def create_tab_layout(tab_names: List[str], default_tab: int = 0):
    """创建标签页布局"""
    return st.tabs(tab_names)


def create_footer():
    """创建页脚"""
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #666; padding: 20px; font-size: 0.9rem;">
            <p>© 2024 {SYSTEM_CONSTANTS['APP_NAME']} | 版本 {SYSTEM_CONSTANTS['VERSION']}</p>
            <p>技术支持: {SYSTEM_CONSTANTS['SUPPORT_EMAIL']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
