import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


class ChartGenerator:
    """图表生成器基类"""
    
    @staticmethod
    def create_trend_chart(df, date_col="日期", chart_title="趋势图"):
        """创建基础趋势图表"""
        raise NotImplementedError("子类必须实现此方法")
    
    @staticmethod
    def create_bar_chart(df, x_col, y_col, title="柱状图"):
        """创建基础柱状图"""
        raise NotImplementedError("子类必须实现此方法")


class TaskTrendChartGenerator(ChartGenerator):
    """任务趋势图表生成器"""
    
    @staticmethod
    def create_trend_chart(df, date_col="日期", chart_title="任务趋势"):
        """创建任务完成+通过总和趋势图"""
        if "完成" not in df.columns or "通过" not in df.columns:
            fig = go.Figure()
            fig.update_layout(title=chart_title, height=400)
            return fig

        df = df.copy()
        df["完成+通过"] = df["完成"] + df["通过"]
        
        if "市" in df.columns:
            # 多城市趋势图
            city_date_grouped = df.groupby(["市", date_col])["完成+通过"].sum().reset_index()
            city_date_grouped[date_col] = pd.to_datetime(city_date_grouped[date_col])
            
            fig = go.Figure()
            colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel
            
            for i, city in enumerate(city_date_grouped["市"].unique()):
                city_data = city_date_grouped[city_date_grouped["市"] == city].sort_values(date_col)
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
            # 单趋势图
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
                    line=dict(
                        color="#2ca02c",
                        width=3,
                        shape="spline",
                        smoothing=1.3,
                    ),
                    marker=dict(size=8, color="#2ca02c"),
                    text=date_grouped["完成+通过"],
                    textposition="top center",
                    textfont=dict(size=10),
                )
            )

        fig.update_layout(
            title=chart_title,
            xaxis_title="日期",
            yaxis_title="完成+通过总和",
            hovermode="x unified",
            showlegend=("市" in df.columns),
            xaxis=dict(
                tickformat="%Y-%m-%d",
                tickangle=-45,
                tickfont=dict(size=10),
            ),
            legend=dict(
                yanchor="top",
                y=-0.3,
                xanchor="center",
                x=0.5,
                orientation="h",
                font=dict(size=10),
            ) if "市" in df.columns else None,
            height=500,
        )
        return fig

    @staticmethod
    def create_uploader_bar_chart(uploader_stats, title="上传人平均值"):
        """创建上传人平均值条形图"""
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=uploader_stats["上传人姓名"],
                y=uploader_stats["完成+通过"],
                marker_color=px.colors.qualitative.Set3[:len(uploader_stats)],
                text=uploader_stats["完成+通过"].round(2),
                textposition="auto",
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="上传人姓名",
            yaxis_title="平均值",
            xaxis_tickangle=-45,
            showlegend=False,
            height=400,
        )
        return fig


class GroupedBarChartGenerator(ChartGenerator):
    """分组柱状图生成器"""
    
    @staticmethod
    def create_grouped_bar_chart(df, group_cols, title="分组柱状图"):
        """创建分组柱状图"""
        status_cols = ["待执行", "完成", "通过", "未知"]
        
        required_cols = group_cols + status_cols
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return None, f"缺少列: {missing_cols}"

        grouped_df = df.groupby(group_cols)[status_cols].sum().reset_index()
        grouped_df["分组标签"] = grouped_df[group_cols[0]]
        for col in group_cols[1:]:
            grouped_df["分组标签"] = grouped_df["分组标签"] + " - " + grouped_df[col].astype(str)

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
            title=title,
            xaxis_title="分组",
            yaxis_title="数量",
            barmode="group",
            hovermode="x unified",
            showlegend=True,
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        )
        return fig, None


class ZeroDaysChartGenerator(ChartGenerator):
    """零任务天数图表生成器"""
    
    @staticmethod
    def create_zero_days_chart(df, group_cols, title="零任务天数统计"):
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
            title=title,
            xaxis_title="地区",
            yaxis_title="天数",
            hovermode="x unified",
            showlegend=False,
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
        )
        return fig, None