# 基于 Python 的人事数据分析与可视化平台

[![CI](https://github.com/qijiejin25-design/hr-data-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/qijiejin25-design/hr-data-analytics/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-black)

一个用 Flask + pandas + matplotlib 搭建的人事数据分析小平台，支持从 Excel 导入员工、考勤、绩效数据，自动完成清洗、统计分析、图表可视化和月度报表导出。

## 功能特性

- **多源 Excel 导入**：员工档案、考勤记录、绩效评分独立表格，自动合并到统一分析视图
- **数据清洗**：缺失值填充、重复记录去重、字段类型校验、异常值（如考勤时长 > 24 小时）检测
- **统计分析**
  - 部门维度：人数、平均绩效、出勤率
  - 时间维度：月度出勤趋势、月度绩效趋势
  - 员工维度：迟到/早退/加班排行
- **图表可视化**：matplotlib 生成柱状图、折线图、饼图，前端直接渲染 PNG
- **报表导出**：一键生成包含图表与汇总表的 Excel 月报
- **筛选查询**：按部门、日期范围、员工编号等维度组合筛选

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Flask 3 |
| 数据处理 | pandas, numpy |
| Excel 读写 | openpyxl |
| 可视化 | matplotlib |
| 前端 | Jinja2 + Bootstrap 5（CDN） |

## 目录结构

```
hr-data-analytics/
├── run.py                  # 启动入口
├── requirements.txt
├── app/
│   ├── __init__.py         # Flask app 工厂
│   ├── routes.py           # 路由
│   ├── services/
│   │   ├── data_loader.py  # Excel 导入
│   │   ├── cleaner.py      # 数据清洗
│   │   ├── analyzer.py     # 统计分析
│   │   ├── visualizer.py   # matplotlib 绘图
│   │   └── reporter.py     # 月报导出
│   └── templates/          # Jinja2 模板
├── data/                   # 示例数据
└── scripts/
    └── generate_sample_data.py   # 生成示例数据
```

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 生成示例数据（已附带，可跳过）
python scripts/generate_sample_data.py

# 4. 启动服务
python run.py
```

打开浏览器访问 http://127.0.0.1:5000 即可。

## 使用流程

1. 首页选择「上传数据」，依次上传 `employees.xlsx`、`attendance.xlsx`、`performance.xlsx`
2. 进入「分析仪表盘」查看部门绩效、月度趋势等图表
3. 在「筛选查询」按部门 / 日期 / 员工筛选
4. 点击「导出月报」下载 Excel 报表

## 示例数据说明

`data/` 下三个示例 Excel 包含 50 名员工、最近 6 个月的考勤与季度绩效，覆盖 5 个部门，故意混入了缺失值、重复行和异常数据用于演示清洗能力。

## 后续可扩展

- 接入 MySQL 做持久化（当前仅会话内存）
- 异步处理大文件上传（Celery）
- 接入图表交互库（ECharts / Plotly）
