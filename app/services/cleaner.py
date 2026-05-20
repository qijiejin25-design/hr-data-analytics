"""数据清洗：缺失值、重复行、字段校验、异常值。"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class CleanReport:
    """记录清洗过程的统计信息，用于在前端展示。"""
    duplicates_removed: int = 0
    missing_filled: dict[str, int] = field(default_factory=dict)
    invalid_dropped: int = 0
    notes: list[str] = field(default_factory=list)


def clean_employees(df: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    report = CleanReport()

    before = len(df)
    df = df.drop_duplicates(subset=["emp_id"], keep="first")
    report.duplicates_removed = before - len(df)

    for col in ["name", "department", "position"]:
        miss = int(df[col].isna().sum())
        if miss:
            df[col] = df[col].fillna("未填写")
            report.missing_filled[col] = miss

    if df["hire_date"].isna().any():
        miss = int(df["hire_date"].isna().sum())
        report.missing_filled["hire_date"] = miss
        df = df.dropna(subset=["hire_date"])
        report.invalid_dropped += miss
        report.notes.append("入职日期为空的员工已剔除")

    return df.reset_index(drop=True), report


def clean_attendance(df: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    report = CleanReport()

    before = len(df)
    df = df.drop_duplicates(subset=["emp_id", "date"], keep="last")
    report.duplicates_removed = before - len(df)

    miss = int(df["work_hours"].isna().sum())
    if miss:
        df["work_hours"] = df["work_hours"].fillna(0)
        report.missing_filled["work_hours"] = miss

    # 异常工时：负数或大于 24
    invalid_mask = (df["work_hours"] < 0) | (df["work_hours"] > 24)
    invalid_count = int(invalid_mask.sum())
    if invalid_count:
        df = df.loc[~invalid_mask]
        report.invalid_dropped += invalid_count
        report.notes.append(f"剔除异常工时记录 {invalid_count} 条（<0 或 >24 小时）")

    df = df.dropna(subset=["date"])
    return df.reset_index(drop=True), report


def clean_performance(df: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    report = CleanReport()

    before = len(df)
    df = df.drop_duplicates(subset=["emp_id", "month"], keep="last")
    report.duplicates_removed = before - len(df)

    miss = int(df["score"].isna().sum())
    if miss:
        df["score"] = df["score"].fillna(df["score"].mean().round(1))
        report.missing_filled["score"] = miss
        report.notes.append("缺失绩效分数使用整体均值填充")

    invalid_mask = (df["score"] < 0) | (df["score"] > 100)
    invalid_count = int(invalid_mask.sum())
    if invalid_count:
        df = df.loc[~invalid_mask]
        report.invalid_dropped += invalid_count
        report.notes.append(f"剔除越界绩效分 {invalid_count} 条（应在 0–100）")

    df = df.dropna(subset=["month"])
    return df.reset_index(drop=True), report
