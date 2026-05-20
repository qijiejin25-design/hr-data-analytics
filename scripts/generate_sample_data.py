"""生成示例数据：50 名员工 / 6 个月考勤 / 6 个月绩效。
故意混入若干缺失值、重复行、异常工时，用于演示数据清洗能力。"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

DEPARTMENTS = ["研发部", "产品部", "市场部", "人事部", "财务部"]
POSITIONS = {
    "研发部": ["后端工程师", "前端工程师", "测试工程师"],
    "产品部": ["产品经理", "产品助理"],
    "市场部": ["市场专员", "市场经理"],
    "人事部": ["HR 专员", "HR 主管"],
    "财务部": ["会计", "财务主管"],
}
STATUSES = ["正常", "迟到", "早退", "请假", "缺勤"]
RATINGS = ["A", "B", "C", "D"]

OUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_employees(n: int = 50) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        dept = random.choice(DEPARTMENTS)
        rows.append({
            "emp_id": f"E{i:03d}",
            "name": f"员工{i:03d}",
            "department": dept,
            "position": random.choice(POSITIONS[dept]),
            "hire_date": date(2020, 1, 1) + timedelta(days=random.randint(0, 1500)),
            "gender": random.choice(["男", "女"]),
        })
    df = pd.DataFrame(rows)
    # 故意制造脏数据
    df.loc[3, "name"] = None
    df.loc[7, "department"] = None
    df = pd.concat([df, df.iloc[[5]]], ignore_index=True)  # 重复行
    return df


def make_attendance(employees: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    rows = []
    today = date.today()
    start = today - timedelta(days=months * 30)
    days = pd.bdate_range(start, today)  # 工作日
    for _, emp in employees.iterrows():
        for d in days:
            status = random.choices(STATUSES, weights=[80, 8, 5, 5, 2])[0]
            if status == "缺勤":
                check_in, check_out, hours = "", "", 0.0
            else:
                in_h = 9 + (random.random() * 0.5 if status != "迟到" else random.uniform(0.5, 2))
                out_h = 18 - (random.random() * 0.5 if status != "早退" else random.uniform(0.5, 2))
                hours = round(max(0.0, out_h - in_h), 2)
                check_in = f"{int(in_h):02d}:{int((in_h % 1) * 60):02d}"
                check_out = f"{int(out_h):02d}:{int((out_h % 1) * 60):02d}"
            rows.append({
                "emp_id": emp["emp_id"],
                "date": d.date(),
                "check_in": check_in,
                "check_out": check_out,
                "work_hours": hours,
                "status": status,
            })
    df = pd.DataFrame(rows)
    # 异常工时
    df.loc[10, "work_hours"] = 30
    df.loc[20, "work_hours"] = -2
    df.loc[15, "work_hours"] = np.nan
    return df


def make_performance(employees: pd.DataFrame, months: int = 6) -> pd.DataFrame:
    rows = []
    today = date.today().replace(day=1)
    for m in range(months):
        month = (pd.Timestamp(today) - pd.DateOffset(months=m)).normalize()
        for _, emp in employees.iterrows():
            score = max(0, min(100, int(np.random.normal(80, 8))))
            rows.append({
                "emp_id": emp["emp_id"],
                "month": month.date(),
                "score": score,
                "rating": "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D",
            })
    df = pd.DataFrame(rows)
    df.loc[2, "score"] = np.nan
    df.loc[8, "score"] = 150  # 越界
    return df


def main():
    employees = make_employees()
    attendance = make_attendance(employees)
    performance = make_performance(employees)

    employees.to_excel(OUT_DIR / "sample_employees.xlsx", index=False)
    attendance.to_excel(OUT_DIR / "sample_attendance.xlsx", index=False)
    performance.to_excel(OUT_DIR / "sample_performance.xlsx", index=False)
    print(f"已生成示例数据到 {OUT_DIR}")
    print(f"  员工: {len(employees)} 行 / 考勤: {len(attendance)} 行 / 绩效: {len(performance)} 行")


if __name__ == "__main__":
    main()
