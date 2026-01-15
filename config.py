# config.py
from datetime import time
from typing import Dict, Any, List

# 默认配置
DEFAULT_CONFIG: Dict[str, Any] = {
    "work_time": {
        "min_hours": 8.0,
        "max_hours": 12.0,
        "work_time_threshold": time(9, 15, 0),
        "allow_overtime": True,
        "max_overtime_hours": 2.0,
        "is_work_verdict": False,
    },
    "mileage": {
        "min_mileage": 50,
        "max_mileage": 300,
        "allow_zero_mileage": False,
        "max_daily_mileage": 500,
    },
    "toll_fee": {
        "max_fee": 100,
        "allow_zero_fee": True,
        "daily_max_fee": 200,
    },
    "overtime_fee": {
        "max_fee": 20,
        "allow_zero_fee": True,
        "overtime_rate": 1.5,
    },
    "data_quality": {
        "max_missing_rate": 0.05,  # 5%
        "max_duplicate_rate": 0.01,  # 1%
        "require_date_consistency": True,
    },
    "export": {
        "default_format": "excel",
        "include_summary": True,
        "compress_files": False,
    },
}

# 页面配置
PAGES_CONFIG = {
    "车辆分析": {
        "icon": "🚗",
        "file": "vehicle_analysis.py",
        "description": "车辆出勤数据核查与分析",
        "requires_files": 1,
    },
    "工单分析": {
        "icon": "📋",
        "file": "task_analysis.py",
        "description": "工单与出勤数据匹配分析",
        "requires_files": 4,
    },
    "系统设置": {
        "icon": "⚙️",
        "file": "settings.py",
        "description": "系统参数配置",
        "requires_files": 0,
    },
}

# 图表颜色配置
CHART_COLORS = {
    "primary": "#1E88E5",  # 蓝色
    "secondary": "#43A047",  # 绿色
    "warning": "#FB8C00",  # 橙色
    "error": "#E53935",  # 红色
    "success": "#43A047",  # 绿色
    "info": "#1E88E5",  # 蓝色
    "light_blue": "#90CAF9",
    "light_green": "#A5D6A7",
    "light_orange": "#FFCC80",
    "light_red": "#EF9A9A",
}

# 数据验证规则
VALIDATION_RULES = {
    "work_duration": {
        "min": 0,
        "max": 24,
        "unit": "小时",
        "description": "工作时长应在合理范围内",
    },
    "mileage": {
        "min": 0,
        "max": 1000,
        "unit": "公里",
        "description": "行驶里程应在合理范围内",
    },
    "fee": {"min": 0, "max": 10000, "unit": "元", "description": "费用应在合理范围内"},
    "date": {"min_year": 2020, "max_year": 2030, "description": "日期应在合理范围内"},
}

# 核查项配置
CHECK_ITEMS = {
    "工作时长核查": {
        "key": "work_time",
        "description": "检查工作时长是否在正常范围内",
        "severity": "high",
        "enabled": True,
    },
    "公里数核查": {
        "key": "mileage",
        "description": "检查行驶里程是否合理",
        "severity": "medium",
        "enabled": True,
    },
    "路桥费核查": {
        "key": "toll_fee",
        "description": "检查路桥费是否异常",
        "severity": "medium",
        "enabled": True,
    },
    "加班费核查": {
        "key": "overtime_fee",
        "description": "检查加班费是否合理",
        "severity": "low",
        "enabled": True,
    },
}

# 异常级别颜色
SEVERITY_COLORS = {
    "high": "#E53935",  # 红色
    "medium": "#FB8C00",  # 橙色
    "low": "#FFD600",  # 黄色
    "info": "#1E88E5",  # 蓝色
}

# 数据列映射
COLUMN_MAPPINGS = {
    "required_columns": ["开始时间", "结束时间", "车牌号码", "驾驶员名称"],
    "optional_columns": ["省", "市", "行驶里程", "路桥费", "加班费", "备注"],
    "date_columns": ["日期", "开始时间", "结束时间"],
    "numeric_columns": ["工作时长", "行驶里程", "路桥费", "加班费"],
}

# 系统常量
SYSTEM_CONSTANTS = {
    "APP_NAME": "内控管理分析系统",
    "VERSION": "1.2.0",
    "SUPPORT_EMAIL": "support@example.com",
    "MAX_FILE_SIZE_MB": 50,  # 最大文件大小50MB
    "MAX_RECORDS": 100000,  # 最大记录数
    "DEFAULT_PAGE_SIZE": 20,
    "DATE_FORMAT": "%Y-%m-%d",
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# 导出配置
EXPORT_CONFIG = {
    "formats": ["excel", "csv", "json"],
    "default_format": "excel",
    "include_timestamp": True,
    "timestamp_format": "%Y%m%d_%H%M%S",
    "compress_large_files": True,
    "large_file_threshold_mb": 10,
}
