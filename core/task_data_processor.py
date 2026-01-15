import pandas as pd


def merge_personnel_files(personnel_file: str, employee_file: str) -> pd.DataFrame:
    """合并人员信息"""
    df1 = pd.read_excel(personnel_file, header=1, engine="calamine")
    df1 = df1[["u_uid", "员工编号", "员工姓名", "身份证号"]].drop_duplicates()

    df2 = pd.read_excel(employee_file, header=0, engine="calamine")
    df2 = df2[["*资源姓名", "Uniportal账号", "*ID编码"]]
    df2 = df2.rename(
        columns={"*资源姓名": "资源姓名", "*ID编码": "ID编码"}
    ).drop_duplicates()

    df1["身份证号"] = df1["身份证号"].astype(str).str.strip()
    df2["ID编码"] = df2["ID编码"].astype(str).str.strip()

    # 使用映射方法添Uniportal账号列（类似第32-45行的逻辑）
    id_mapping = df2.set_index("ID编码")["Uniportal账号"].to_dict()
    df1["Uniportal账号"] = df1["身份证号"].map(id_mapping)

    return df1


def process_vehicle_attendance(
    vehicle_file: str, personnel_df: pd.DataFrame
) -> pd.DataFrame:
    """处理车辆出勤记录，添加Uniportal账号"""
    df = pd.read_excel(vehicle_file, header=1, engine="calamine", parse_dates=["日期"])
    df["日期"] = pd.to_datetime(df["日期"]).dt.date.astype(str)

    # 确保类型正确
    df["上传人id"] = (
        df["上传人id"].astype(str).str.strip()
    )  # 转换上传人ID为字符串并去除空格
    personnel_df["u_uid"] = (
        personnel_df["u_uid"].astype(str).str.strip()
    )  # 转换人员表UUID为字符串并去除空格

    account_mapping = personnel_df.set_index("u_uid")[
        "Uniportal账号"
    ].to_dict()  # 创建UUID到账号的映射字典
    df["Uniportal账号"] = df["上传人id"].map(
        account_mapping
    )  # 根据映射将上传人ID转换为Uniportal账号

    # 清理Uniportal账号
    df["Uniportal账号"] = df["Uniportal账号"].astype(str).str.strip()

    return df


def process_task_progress(task_file: str) -> pd.DataFrame:
    """处理任务进展，任务状态作为列名"""
    df = pd.read_excel(task_file, header=0, engine="calamine", parse_dates=["工单日期"])
    df = df[df["工单类别"] != "后台工单"]

    status_mapping = {
        "测试中": "待执行",
        "待执行": "待执行",
        "第三方上传完成": "完成",
        "分析失败": "完成",
        "分析中": "完成",
        "评审不通过": "完成",
        "评审中": "完成",
        "审核不通过": "完成",
        "审核通过": "通过",
        "已分配": "待执行",
        "已关闭": "通过",
        "已接纳": "待执行",
        "已开始": "待执行",
        "已完成": "通过",
        "已指派": "待执行",
        "执行中": "待执行",
    }

    df["任务进展"] = df["任务状态"].map(status_mapping).fillna("未知")
    df["工单日期"] = pd.to_datetime(df["工单日期"]).dt.date.astype(str)

    # 任务进展作为列名
    result = df.pivot_table(
        index=["责任人账号", "责任人姓名", "工单日期"],
        columns="任务进展",
        aggfunc="size",
        fill_value=0,
    ).reset_index()
    result.columns.name = None

    # 清理账号列
    result["责任人账号"] = result["责任人账号"].astype(str).str.strip()

    return result


def merge_vehicle_with_tasks(
    vehicle_df: pd.DataFrame, task_df: pd.DataFrame
) -> pd.DataFrame:
    """合并车辆记录和任务进展"""

    # 确保账号类型一致
    vehicle_df["Uniportal账号"] = vehicle_df["Uniportal账号"].astype(str).str.strip()
    task_df["责任人账号"] = task_df["责任人账号"].astype(str).str.strip()

    # 创建复合键映射（账号 + 日期）
    task_df["复合键"] = task_df["责任人账号"] + "_" + task_df["工单日期"].astype(str)
    vehicle_df["复合键"] = (
        vehicle_df["Uniportal账号"] + "_" + vehicle_df["日期"].astype(str)
    )

    # 使用映射方法添加任务进展列
    task_mapping = {}
    for _, row in task_df.iterrows():
        key = row["复合键"]
        task_mapping[key] = {
            "待执行": row.get("待执行", 0),
            "完成": row.get("完成", 0),
            "通过": row.get("通过", 0),
            "未知": row.get("未知", 0),
        }

    # 为车辆记录添加任务进展相关的列
    for column in ["待执行", "完成", "通过", "未知"]:
        vehicle_df[column] = vehicle_df["复合键"].map(
            lambda x: task_mapping.get(x, {}).get(column, 0)
        )

    # 清理临时列
    vehicle_df = vehicle_df.drop(columns=["复合键"])

    return vehicle_df


if __name__ == "__main__":
    # 文件路径
    personnel_file = r"D:\WenJianfeng\桌面\车辆\人员明细信息.xlsx"
    employee_file = r"D:\WenJianfeng\桌面\车辆\IResourceEmployee20260112135936.xlsx"
    vehicle_file = r"D:\WenJianfeng\桌面\车辆\车辆出勤记录信息.xlsx"
    task_file = (
        r"D:\WenJianfeng\桌面\车辆\前后台工单履行率明细_original_20260112101759.xlsx"
    )

    # 1. 合并人员信息
    print("1. 合并人员信息...")
    personnel_df = merge_personnel_files(personnel_file, employee_file)

    # 2. 处理车辆出勤记录
    print("2. 处理车辆出勤记录...")
    vehicle_df = process_vehicle_attendance(vehicle_file, personnel_df)

    # 3. 处理任务进展
    print("3. 处理任务进展...")
    task_df = process_task_progress(task_file)

    # 4. 合并车辆和任务数据
    print("4. 合并车辆和任务数据...")
    final_df = merge_vehicle_with_tasks(vehicle_df, task_df)

    # 保存结果
    final_df.to_excel("结果.xlsx", index=False)
    print("\n结果已保存到: 结果.xlsx")

    # 显示结果
    print("\n前5行结果:")

    print(final_df.head())
