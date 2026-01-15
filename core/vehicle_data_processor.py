import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import time, datetime


class DataChecker:
    """数据核查器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化核查器配置"""
        self.config = {
            "work_time": {
                "min_hours": 8,
                "max_hours": 12,
                "overtime_threshold": 12,
                "work_time_threshold": "9:15:00",
                "is_work_verdict": False,
            },
            "mileage": {"min_mileage": 50, "max_mileage": 300},
            "toll_fee": {"max_fee": 100},
            "overtime_fee": {"max_fee": 20},
        }

        if config:
            self.config.update(config)

    def import_data(self, file_path: str) -> pd.DataFrame:
        """导入并清洗数据"""
        try:
            df = pd.read_excel(file_path, header=1, engine="calamine")

            # 标准化列名（去除空格和特殊字符）
            df.columns = df.columns.str.strip()

            # 日期列转换
            if "日期" in df.columns:
                df["日期"] = pd.to_datetime(df["日期"], errors="coerce")

            # 执行所有核查
            df = self.perform_all_checks(df)

            return df

        except Exception as e:
            raise Exception(f"数据导入失败: {str(e)}")

    def perform_all_checks(self, df: pd.DataFrame) -> pd.DataFrame:
        """执行所有核查"""
        # 记录原始列名
        original_columns = df.columns.tolist()

        # 按顺序执行核查
        df = self.check_work_time(df)
        df = self.check_mileage(df)
        df = self.check_toll_fee(df)
        df = self.check_overtime_fee(df)

        # 添加核查摘要
        df = self.add_check_summary(df, original_columns)

        return df

    def check_work_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """核查工作时长"""
        required_columns = ["开始时间", "结束时间"]

        if all(col in df.columns for col in required_columns):
            # 转换为datetime类型
            df["开始时间"] = pd.to_datetime(df["开始时间"], errors="coerce")
            df["结束时间"] = pd.to_datetime(df["结束时间"], errors="coerce")

            # 使用向量化操作提高性能
            start_missing = df["开始时间"].isna()
            end_missing = df["结束时间"].isna()

            threshold_str = self.config["work_time"]["work_time_threshold"]
            is_work_verdict = self.config["work_time"]["is_work_verdict"]

            # 处理不同的阈值类型
            if isinstance(threshold_str, str):
                work_time_threshold = datetime.strptime(
                    threshold_str, "%H:%M:%S"
                ).time()
            elif isinstance(threshold_str, time):
                work_time_threshold = threshold_str

            early_start = df["开始时间"].dt.time > work_time_threshold

            # 计算工作时长（小时）
            work_duration = (df["结束时间"] - df["开始时间"]).dt.total_seconds() / 3600

            # 检查跨天
            cross_day = df["开始时间"].dt.date != df["结束时间"].dt.date

            # 假设df['只打卡不出车']是布尔类型，True表示只打卡不出车
            is_punch_only = pd.Series(False, index=df.index)
            if is_work_verdict:
                if "只打卡不出车" in df.columns:
                    is_punch_only = df["只打卡不出车"].astype(bool)

                # 判断是否为正常出车（不是只打卡不出车）
                is_normal_work = ~is_punch_only

                # 生成核查结果
                conditions = [
                    early_start & is_normal_work,
                    start_missing & is_normal_work,
                    end_missing & is_normal_work,
                    cross_day & is_normal_work,
                    (work_duration < self.config["work_time"]["min_hours"])
                    & is_normal_work,
                    work_duration > self.config["work_time"]["max_hours"],
                    work_duration.between(
                        self.config["work_time"]["min_hours"],
                        self.config["work_time"]["max_hours"],
                    )
                    & is_normal_work,
                    is_punch_only,
                ]
                choices = [
                    f"晚于{work_time_threshold}出车",
                    "未开始打卡",
                    "未结束打卡",
                    "跨天打卡",
                    "提前下班",
                    "工作时长超12小时",
                    "正常",
                    "只打卡不出车",
                ]
            else:
                # 生成核查结果
                conditions = [
                    early_start,
                    start_missing,
                    end_missing,
                    cross_day,
                    (work_duration < self.config["work_time"]["min_hours"]),
                    work_duration > self.config["work_time"]["max_hours"],
                    work_duration.between(
                        self.config["work_time"]["min_hours"],
                        self.config["work_time"]["max_hours"],
                    ),
                ]
                choices = [
                    f"晚于{work_time_threshold}出车",
                    "未开始打卡",
                    "未结束打卡",
                    "跨天打卡",
                    "提前下班",
                    "工作时长超12小时",
                    "正常",
                ]

            df["工作时长"] = work_duration.round(1)
            df["工作时长核查"] = np.select(conditions, choices, default="数据错误")

        return df

    def check_mileage(self, df: pd.DataFrame) -> pd.DataFrame:
        """核查公里数"""
        if "行驶里程" in df.columns:
            # 转换为数值类型
            mileage_series = pd.to_numeric(df["行驶里程"], errors="coerce")

            conditions = [
                mileage_series > self.config["mileage"]["max_mileage"],
                mileage_series < self.config["mileage"]["min_mileage"],
                mileage_series.between(0, self.config["mileage"]["max_mileage"]),
                mileage_series.isna(),
            ]

            choices = [
                f'公里数大于{self.config["mileage"]["max_mileage"]}',
                f'公里数小于{self.config["mileage"]["min_mileage"]}',
                "正常",
                "数据缺失或格式错误",
            ]

            df["公里数核查"] = np.select(conditions, choices, default="数据错误")

        return df

    def check_toll_fee(self, df: pd.DataFrame) -> pd.DataFrame:
        """核查路桥费"""
        if "路桥费" in df.columns:
            toll_series = pd.to_numeric(df["路桥费"], errors="coerce")

            conditions = [
                toll_series > self.config["toll_fee"]["max_fee"],
                toll_series < 0,
                toll_series.between(0, self.config["toll_fee"]["max_fee"]),
                toll_series.isna(),
            ]

            choices = [
                f'路桥费大于{self.config["toll_fee"]["max_fee"]}',
                "路桥费小于0",
                "正常",
                "数据缺失或格式错误",
            ]

            df["路桥费核查"] = np.select(conditions, choices, default="数据错误")

        return df

    def check_overtime_fee(self, df: pd.DataFrame) -> pd.DataFrame:
        """核查加班费"""
        if "加班费" in df.columns:
            overtime_series = pd.to_numeric(df["加班费"], errors="coerce")

            conditions = [
                overtime_series > self.config["overtime_fee"]["max_fee"],
                overtime_series < 0,
                overtime_series.between(0, self.config["overtime_fee"]["max_fee"]),
                overtime_series.isna(),
            ]

            choices = [
                f'加班费大于{self.config["overtime_fee"]["max_fee"]}',
                "加班费小于0",
                "正常",
                "数据缺失或格式错误",
            ]

            df["加班费核查"] = np.select(conditions, choices, default="数据错误")

        return df

    def add_check_summary(
        self, df: pd.DataFrame, original_columns: list
    ) -> pd.DataFrame:
        """添加核查摘要"""
        check_columns = [col for col in df.columns if col.endswith("核查")]

        if check_columns:
            # 检查是否存在异常
            def get_summary(row):
                issues = []
                for col in check_columns:
                    if row[col] not in ["正常", ""] and pd.notna(row[col]):
                        issues.append(f"{col}: {row[col]}")

                if issues:
                    return "; ".join(issues)
                return "全部正常"

            df["核查摘要"] = df.apply(get_summary, axis=1)

            # 计算异常数量
            df["异常数量"] = df[check_columns].apply(
                lambda row: sum(
                    1 for val in row if val not in ["正常", ""] and pd.notna(val)
                ),
                axis=1,
            )

        return df

    def get_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """获取核查统计信息"""
        stats = {}
        check_columns = [col for col in df.columns if col.endswith("核查")]
        for col in check_columns:
            if col in df.columns:
                stats[col] = {
                    "total": len(df),
                    "normal": (df[col] == "正常").sum(),
                    "abnormal": (df[col] != "正常").sum(),
                    "distribution": df[col].value_counts().to_dict(),
                }

        return stats


def get_default_config() -> Dict[str, Any]:
    """获取默认配置"""
    return {
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
