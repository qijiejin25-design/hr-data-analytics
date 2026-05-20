"""Web 路由：上传、仪表盘、筛选、月报下载。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.utils import secure_filename

from .services import analyzer, cleaner, data_loader, reporter, visualizer

bp = Blueprint("main", __name__)

DATASETS = ("employees", "attendance", "performance")


def _data_paths() -> dict[str, Path | None]:
    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    paths: dict[str, Path | None] = {}
    for name in DATASETS:
        stored = session.get(f"path_{name}")
        if stored and (upload_dir / stored).exists():
            paths[name] = upload_dir / stored
        else:
            sample = Path(__file__).resolve().parent.parent / "data" / f"sample_{name}.xlsx"
            paths[name] = sample if sample.exists() else None
    return paths


def _load_clean() -> dict[str, pd.DataFrame] | None:
    paths = _data_paths()
    if not all(paths.values()):
        return None
    emp, _ = cleaner.clean_employees(data_loader.load_employees(paths["employees"]))
    att, _ = cleaner.clean_attendance(data_loader.load_attendance(paths["attendance"]))
    perf, _ = cleaner.clean_performance(data_loader.load_performance(paths["performance"]))
    return {"employees": emp, "attendance": att, "performance": perf}


@bp.route("/")
def index():
    paths = _data_paths()
    return render_template("index.html", paths={k: v.name if v else None for k, v in paths.items()})


@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        upload_dir = Path(current_app.config["UPLOAD_DIR"])
        for name in DATASETS:
            file = request.files.get(name)
            if file and file.filename:
                safe = secure_filename(file.filename)
                dest = upload_dir / f"{name}__{safe}"
                file.save(dest)
                session[f"path_{name}"] = dest.name
        flash("上传完成，刷新仪表盘查看结果。", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("upload.html")


@bp.route("/dashboard")
def dashboard():
    bundle = _load_clean()
    if bundle is None:
        flash("尚未提供完整数据，请先上传或检查 data/ 下的示例文件。", "warning")
        return redirect(url_for("main.upload"))

    dept = analyzer.department_summary(bundle["employees"], bundle["performance"])
    att_trend = analyzer.monthly_attendance_trend(bundle["attendance"])
    perf_trend = analyzer.monthly_performance_trend(bundle["performance"])
    status = analyzer.attendance_status_summary(bundle["attendance"])
    top = analyzer.top_performers(bundle["employees"], bundle["performance"], top_n=10)

    charts = {
        "dept_score": visualizer.bar_department_score(dept),
        "att_trend": visualizer.line_monthly_attendance(att_trend),
        "perf_trend": visualizer.line_monthly_performance(perf_trend),
        "status": visualizer.pie_attendance_status(status),
    }

    return render_template(
        "dashboard.html",
        dept=dept.to_dict(orient="records"),
        top=top.to_dict(orient="records"),
        charts=charts,
    )


@bp.route("/filter", methods=["GET", "POST"])
def filter_view():
    bundle = _load_clean()
    if bundle is None:
        flash("尚未提供完整数据。", "warning")
        return redirect(url_for("main.upload"))

    department = request.values.get("department") or None
    start = request.values.get("start_date") or None
    end = request.values.get("end_date") or None
    emp_id = request.values.get("emp_id") or None

    start_ts = pd.to_datetime(start) if start else None
    end_ts = pd.to_datetime(end) if end else None

    att = bundle["attendance"].merge(
        bundle["employees"][["emp_id", "department", "name"]], on="emp_id", how="left"
    )
    filtered = analyzer.filter_records(
        att, department=department, start_date=start_ts, end_date=end_ts,
        emp_id=emp_id, date_col="date",
    )

    departments = sorted(bundle["employees"]["department"].dropna().unique().tolist())
    return render_template(
        "filter.html",
        departments=departments,
        records=filtered.head(200).to_dict(orient="records"),
        total=len(filtered),
        form={"department": department or "", "start_date": start or "",
              "end_date": end or "", "emp_id": emp_id or ""},
    )


@bp.route("/export")
def export_report():
    bundle = _load_clean()
    if bundle is None:
        flash("尚未提供完整数据。", "warning")
        return redirect(url_for("main.upload"))

    path = reporter.build_monthly_report(
        bundle["employees"], bundle["attendance"], bundle["performance"],
        output_dir=current_app.config["EXPORT_DIR"],
    )
    return send_file(path, as_attachment=True, download_name=path.name)
