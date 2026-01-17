import pandas as pd
from typing import Optional


class DataProcessingService:
    """数据处理服务"""
    
    @staticmethod
    def process_trend_data(df, filters: dict) -> pd.DataFrame:
        """处理趋势数据筛选"""
        filtered_df = df.copy()
        
        # 应用省市筛选
        if filters.get("province") and filters["province"] != "全部":
            filtered_df = filtered_df[filtered_df["省"] == filters["province"]]
        if filters.get("city") and filters["city"] != "全部":
            filtered_df = filtered_df[filtered_df["市"] == filters["city"]]
        
        # 应用上传人筛选
        if filters.get("uploader") and filters["uploader"] != "全部" and "上传人姓名" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["上传人姓名"] == filters["uploader"]]
        
        # 应用日期筛选
        if "日期" in filtered_df.columns and filters.get("start_date") and filters.get("end_date"):
            filtered_df = filtered_df[
                (filtered_df["日期"] >= pd.Timestamp(filters["start_date"])) &
                (filtered_df["日期"] <= pd.Timestamp(filters["end_date"]))
            ]
        
        return filtered_df
    
    @staticmethod
    def calculate_uploader_stats(df, top_n: int = 10) -> pd.DataFrame:
        """计算上传人统计数据"""
        if "上传人姓名" not in df.columns or "完成" not in df.columns or "通过" not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df["完成+通过"] = df["完成"] + df["通过"]
        
        # 按上传人计算平均值
        uploader_avg = df.groupby("上传人姓名")["完成+通过"].mean().reset_index()
        uploader_avg = uploader_avg.sort_values("完成+通过", ascending=False).head(top_n)
        uploader_avg["排名"] = range(1, len(uploader_avg) + 1)
        
        return uploader_avg
    
    @staticmethod
    def calculate_city_trends(df, max_cities: int = 10) -> pd.DataFrame:
        """计算城市趋势数据"""
        if "完成" not in df.columns or "通过" not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df["完成+通过"] = df["完成"] + df["通过"]
        
        if "市" in df.columns:
            # 按城市和日期计算平均值
            cities = df["市"].dropna().unique()
            if len(cities) > max_cities:
                main_cities = cities[:max_cities]
                city_df = df[df["市"].isin(main_cities)]
            else:
                city_df = df
            
            avg_df = city_df.groupby(["市", "日期"])["完成+通过"].mean().reset_index()
            return avg_df
        else:
            # 按日期计算平均值
            avg_df = df.groupby("日期")["完成+通过"].mean().reset_index()
            return avg_df
    
    @staticmethod
    def get_trend_summary(df) -> pd.DataFrame:
        """获取趋势数据汇总"""
        status_cols = ["待执行", "完成", "通过", "未知"]
        
        if "市" in df.columns:
            # 按日期和城市分组汇总
            trend_summary = df.groupby(["日期", "市"])[status_cols].sum().reset_index()
        else:
            # 只按日期分组汇总
            trend_summary = df.groupby("日期")[status_cols].sum().reset_index()
        
        return trend_summary


class FilterService:
    """筛选器服务"""
    
    @staticmethod
    def get_filter_options(df, current_filters: dict) -> dict:
        """获取筛选器选项"""
        options = {}
        
        # 省份选项
        options["provinces"] = ["全部"] + sorted(df["省"].dropna().unique()) if "省" in df.columns else ["全部"]
        
        # 城市选项
        if current_filters.get("province") and current_filters["province"] != "全部" and "市" in df.columns:
            options["cities"] = ["全部"] + sorted(
                df[df["省"] == current_filters["province"]]["市"].dropna().unique()
            )
        else:
            options["cities"] = ["全部"] + sorted(df["市"].dropna().unique()) if "市" in df.columns else ["全部"]
        
        # 上传人选项
        if "上传人姓名" in df.columns:
            if current_filters.get("province") and current_filters["province"] != "全部":
                uploaders = ["全部"] + sorted(
                    df[
                        (df["省"] == current_filters["province"]) &
                        (df["市"] == current_filters["city"] if current_filters.get("city") != "全部" else True)
                    ]["上传人姓名"].dropna().unique()
                )
            elif current_filters.get("city") and current_filters["city"] != "全部":
                uploaders = ["全部"] + sorted(
                    df[df["市"] == current_filters["city"]]["上传人姓名"].dropna().unique()
                )
            else:
                uploaders = ["全部"] + sorted(df["上传人姓名"].dropna().unique())
            options["uploaders"] = uploaders
        else:
            options["uploaders"] = ["全部"]
        
        return options


class DataValidationService:
    """数据验证服务"""
    
    @staticmethod
    def validate_dataframe(df, required_cols: list) -> tuple:
        """验证DataFrame是否包含必需的列"""
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return False, f"缺少必需的列: {missing_cols}"
        return True, None
    
    @staticmethod
    def check_empty_data(df, message: str = "没有符合条件的数据") -> bool:
        """检查数据是否为空"""
        return len(df) == 0