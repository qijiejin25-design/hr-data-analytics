"""月报导出：把部门汇总、月度趋势、Top 员工写到一个 Excel 文件中。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from . import analyzer


def build_monthly_report(
    employees: pd.DataFrame,
    attendance: pd.DataFrame,
    performance: pd.DataFrame,
    output_dir: str | Path,
    filename: str = "hr_monthly_report.xlsx",
) -> Path:
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dept = analyzer.department_summary(employees, performance)
    att_trend = analyzer.monthly_attendance_trend(attendance)
    perf_trend = analyzer.monthly_performance_trend(performance)
    top = analyzer.top_performers(employees, performance, top_n=20)
    status = analyzer.attendance_status_summary(attendance)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        dept.to_excel(writer, sheet_name="部门汇总", index=False)
        att_trend.to_excel(writer, sheet_name="月度考勤", index=False)
        perf_trend.to_excel(writer, sheet_name="月度绩效", index=False)
        top.to_excel(writer, sheet_name="绩效Top", index=False)
        status.to_excel(writer, sheet_name="考勤状态", index=False)

    return output_path
