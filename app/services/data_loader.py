"""Excel 数据导入。读取员工、考勤、绩效三类表并返回 pandas DataFrame。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

EMPLOYEE_COLUMNS = ["emp_id", "name", "department", "position", "hire_date", "gender"]
ATTENDANCE_COLUMNS = ["emp_id", "date", "check_in", "check_out", "work_hours", "status"]
PERFORMANCE_COLUMNS = ["emp_id", "month", "score", "rating"]


def _read_excel(path: str | Path, required: list[str]) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Excel 缺少必要字段: {missing}（文件: {path}）")
    return df


def load_employees(path: str | Path) -> pd.DataFrame:
    df = _read_excel(path, EMPLOYEE_COLUMNS)
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")
    return df


def load_attendance(path: str | Path) -> pd.DataFrame:
    df = _read_excel(path, ATTENDANCE_COLUMNS)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["work_hours"] = pd.to_numeric(df["work_hours"], errors="coerce")
    return df


def load_performance(path: str | Path) -> pd.DataFrame:
    df = _read_excel(path, PERFORMANCE_COLUMNS)
    df["month"] = pd.to_datetime(df["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    return df


def load_bundle(
    employees_path: str | Path,
    attendance_path: Optional[str | Path] = None,
    performance_path: Optional[str | Path] = None,
) -> dict[str, pd.DataFrame]:
    """一次性加载三类表，便于路由层调用。允许只有员工表。"""
    bundle: dict[str, pd.DataFrame] = {"employees": load_employees(employees_path)}
    if attendance_path:
        bundle["attendance"] = load_attendance(attendance_path)
    if performance_path:
        bundle["performance"] = load_performance(performance_path)
    return bundle
