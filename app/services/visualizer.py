"""matplotlib 图表渲染，返回 base64 PNG，供模板 <img src=> 直接使用。"""
from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")  # 服务端无 GUI
import matplotlib.pyplot as plt
import pandas as pd

# 中文字体兜底：从 matplotlib 已注册字体里挑一个能渲染中文的
from matplotlib import font_manager as _fm

_PREFERRED = [
    "PingFang SC", "PingFang HK", "Heiti SC", "Heiti TC", "STHeiti",
    "Songti SC", "Arial Unicode MS", "Microsoft YaHei", "Noto Sans CJK SC",
]
_available = {f.name for f in _fm.fontManager.ttflist}
_chosen = next((name for name in _PREFERRED if name in _available), "DejaVu Sans")
plt.rcParams["font.sans-serif"] = [_chosen]
plt.rcParams["axes.unicode_minus"] = False


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def bar_department_score(dept_summary: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(dept_summary["department"], dept_summary["avg_score"], color="#4C72B0")
    ax.set_title("各部门平均绩效分")
    ax.set_xlabel("部门")
    ax.set_ylabel("平均分")
    ax.set_ylim(0, 100)
    for i, v in enumerate(dept_summary["avg_score"]):
        ax.text(i, v + 1, f"{v}", ha="center")
    return _fig_to_base64(fig)


def line_monthly_attendance(trend: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(trend["month"].dt.strftime("%Y-%m"), trend["avg_work_hours"],
            marker="o", color="#55A868")
    ax.set_title("月度平均工时趋势")
    ax.set_xlabel("月份")
    ax.set_ylabel("平均工时（小时/天）")
    ax.grid(True, linestyle="--", alpha=0.5)
    return _fig_to_base64(fig)


def line_monthly_performance(trend: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(trend["month"].dt.strftime("%Y-%m"), trend["avg_score"],
            marker="s", color="#C44E52")
    ax.set_title("月度平均绩效趋势")
    ax.set_xlabel("月份")
    ax.set_ylabel("平均绩效分")
    ax.set_ylim(0, 100)
    ax.grid(True, linestyle="--", alpha=0.5)
    return _fig_to_base64(fig)


def pie_attendance_status(status: pd.DataFrame) -> str:
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(status["count"], labels=status["status"], autopct="%1.1f%%",
           colors=["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"])
    ax.set_title("考勤状态分布")
    return _fig_to_base64(fig)
