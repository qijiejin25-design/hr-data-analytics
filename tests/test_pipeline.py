"""端到端冒烟测试：跑一遍完整数据流，确保各模块没有低级错误。"""
from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")
from app.services import analyzer, cleaner, data_loader, reporter

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_full_pipeline(tmp_path):
    emp_path = DATA_DIR / "sample_employees.xlsx"
    att_path = DATA_DIR / "sample_attendance.xlsx"
    perf_path = DATA_DIR / "sample_performance.xlsx"
    if not emp_path.exists():
        pytest.skip("示例数据未生成，请先运行 scripts/generate_sample_data.py")

    emp, emp_rep = cleaner.clean_employees(data_loader.load_employees(emp_path))
    att, _ = cleaner.clean_attendance(data_loader.load_attendance(att_path))
    perf, _ = cleaner.clean_performance(data_loader.load_performance(perf_path))

    assert emp_rep.duplicates_removed >= 1
    assert not emp.empty and not att.empty and not perf.empty

    dept = analyzer.department_summary(emp, perf)
    assert "avg_score" in dept.columns

    report_path = reporter.build_monthly_report(emp, att, perf, output_dir=tmp_path)
    assert report_path.exists() and report_path.stat().st_size > 0
