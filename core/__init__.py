"""
核心模块包 - 提供统一的数据处理接口
"""

from .vehicle_data_processor import (
    DataChecker as VehicleDataChecker,
    get_default_config as get_vehicle_default_config,
)

from .task_data_processor import (
    merge_personnel_files,
    process_vehicle_attendance,
    process_task_progress,
    merge_vehicle_with_tasks,
)

__all__ = [
    "VehicleDataChecker",
    "get_vehicle_default_config",
    "merge_personnel_files",
    "process_vehicle_attendance",
    "process_task_progress",
    "merge_vehicle_with_tasks",
]
