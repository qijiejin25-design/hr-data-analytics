"""统计分析：部门维度、月度维度、个人排行。"""
from __future__ import annotations

import pandas as pd


def department_summary(employees: pd.DataFrame, performance: pd.DataFrame) -> pd.DataFrame:
    merged = performance.merge(employees[["emp_id", "department"]], on="emp_id", how="left")
    grouped = merged.groupby("department").agg(
        headcount=("emp_id", "nunique"),
        avg_score=("score", "mean"),
        max_score=("score", "max"),
        min_score=("score", "min"),
    ).reset_index()
    grouped["avg_score"] = grouped["avg_score"].round(2)
    return grouped.sort_values("avg_score", ascending=False).reset_index(drop=True)


def monthly_attendance_trend(attendance: pd.DataFrame) -> pd.DataFrame:
    df = attendance.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    grouped = df.groupby("month").agg(
        total_work_hours=("work_hours", "sum"),
        avg_work_hours=("work_hours", "mean"),
        records=("emp_id", "count"),
    ).reset_index()
    grouped["avg_work_hours"] = grouped["avg_work_hours"].round(2)
    return grouped


def monthly_performance_trend(performance: pd.DataFrame) -> pd.DataFrame:
    grouped = performance.groupby("month").agg(
        avg_score=("score", "mean"),
        people_count=("emp_id", "nunique"),
    ).reset_index()
    grouped["avg_score"] = grouped["avg_score"].round(2)
    return grouped


def attendance_status_summary(attendance: pd.DataFrame) -> pd.DataFrame:
    """正常/迟到/早退/缺勤等状态计数。"""
    grouped = attendance.groupby("status").size().reset_index(name="count")
    total = grouped["count"].sum()
    if total:
        grouped["percent"] = (grouped["count"] / total * 100).round(2)
    return grouped


def top_performers(
    employees: pd.DataFrame, performance: pd.DataFrame, top_n: int = 10
) -> pd.DataFrame:
    avg = performance.groupby("emp_id")["score"].mean().reset_index(name="avg_score")
    avg["avg_score"] = avg["avg_score"].round(2)
    merged = avg.merge(employees[["emp_id", "name", "department"]], on="emp_id", how="left")
    return merged.sort_values("avg_score", ascending=False).head(top_n).reset_index(drop=True)


def filter_records(
    df: pd.DataFrame,
    department: str | None = None,
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
    emp_id: str | None = None,
    date_col: str = "date",
) -> pd.DataFrame:
    out = df
    if emp_id:
        out = out[out["emp_id"] == emp_id]
    if department and "department" in out.columns:
        out = out[out["department"] == department]
    if start_date is not None and date_col in out.columns:
        out = out[out[date_col] >= start_date]
    if end_date is not None and date_col in out.columns:
        out = out[out[date_col] <= end_date]
    return out.reset_index(drop=True)
