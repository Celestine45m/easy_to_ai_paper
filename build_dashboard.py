#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
解析各会议 statistics_summary.txt，生成大屏展示所需的 JSON 数据，
并输出带内嵌数据的 dashboard.html，用浏览器直接打开即可查看。

使用：在项目根目录执行  python build_dashboard.py  ，然后用浏览器打开 dashboard.html 。
"""

import json
import re
from pathlib import Path


def parse_summary_file(filepath: Path) -> dict | None:
    """解析单个 statistics_summary.txt，返回结构化数据。"""
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines()

    # 解析标题行，如 "AAAI 2024 论文统计分析汇总报告"
    title_match = re.search(r'^([A-Za-z]+)\s+(\d{4})\s+论文统计分析汇总报告', text, re.MULTILINE)
    if not title_match:
        return None
    conference = title_match.group(1)
    year = title_match.group(2)

    result = {
        "conference": conference,
        "year": year,
        "total_papers": 0,
        "total_categories": 0,
        "categories": [],
        "total_organizations": 0,
        "organizations": []
    }

    # 找【一、论文类别统计】段
    in_categories = False
    in_orgs = False
    for i, line in enumerate(lines):
        if '【一、论文类别统计】' in line:
            in_categories = True
            in_orgs = False
            continue
        if '【二、论文机构统计】' in line:
            in_categories = False
            in_orgs = True
            continue
        if in_categories and line.strip().startswith('总论文数:'):
            m = re.search(r'总论文数:\s*(\d+)', line)
            if m:
                result["total_papers"] = int(m.group(1))
            continue
        if in_categories and line.strip().startswith('总类别数:'):
            m = re.search(r'总类别数:\s*(\d+)', line)
            if m:
                result["total_categories"] = int(m.group(1))
            continue
        if in_orgs and line.strip().startswith('总论文数:'):
            # 机构段也有总论文数，可覆盖
            m = re.search(r'总论文数:\s*(\d+)', line)
            if m:
                result["total_papers"] = int(m.group(1))
            continue
        if in_orgs and line.strip().startswith('总机构数:'):
            m = re.search(r'总机构数:\s*(\d+)', line)
            if m:
                result["total_organizations"] = int(m.group(1))
            continue

        # 数据行：排名 + 名称 + 数量 + 占比
        if in_categories or in_orgs:
            parts = line.split()
            if len(parts) >= 4 and parts[0].isdigit() and parts[-2].isdigit():
                try:
                    rank = int(parts[0])
                    count = int(parts[-2])
                    pct_str = parts[-1].rstrip('%')
                    pct = float(pct_str) if pct_str.replace('.', '').isdigit() else 0
                    name = ' '.join(parts[1:-2]).strip()
                    if not name:
                        continue
                    row = {"rank": rank, "name": name, "count": count, "percentage": round(pct, 2)}
                    if in_categories:
                        result["categories"].append(row)
                    else:
                        result["organizations"].append(row)
                except (ValueError, IndexError):
                    pass

    return result


def parse_wanted_papers(root: Path) -> dict:
    """解析 WANTED_PAPERS 下 aipapers_with_keywords_*.txt，按关键词返回论文列表。"""
    wanted_dir = root / "WANTED_PAPERS"
    if not wanted_dir.is_dir():
        return {}
    out: dict[str, list[dict]] = {}
    sep = "----------------------------------------------------------------------------------------------------"
    file_pattern = re.compile(r"aipapers_with_keywords_(.+)\.txt$")
    for path in sorted(wanted_dir.glob("aipapers_with_keywords_*.txt")):
        m = file_pattern.match(path.name)
        if not m:
            continue
        keyword = m.group(1).strip().lower()
        text = path.read_text(encoding="utf-8")
        blocks = [b.strip() for b in text.split(sep) if b.strip()]
        papers = []
        for block in blocks:
            no_m = re.search(r"\[No\.(\d+)\]\s*(.+)", block)
            if not no_m:
                continue
            no_str, title_en = no_m.group(1), no_m.group(2).strip()
            source = ""
            title_zh = ""
            ptype = ""
            link = ""
            category = ""
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("来源:"):
                    source = line.replace("来源:", "").strip()
                elif line.startswith("标题:"):
                    title_zh = line.replace("标题:", "").strip()
                elif line.startswith("类型:"):
                    ptype = line.replace("类型:", "").strip()
                elif line.startswith("链接:"):
                    link = line.replace("链接:", "").strip()
                elif line.startswith("类别:"):
                    category = line.replace("类别:", "").strip()
            papers.append({
                "no": int(no_str) if no_str.isdigit() else len(papers) + 1,
                "title_en": title_en[:200] if title_en else "",
                "title_zh": title_zh[:150] if title_zh else "",
                "source": source,
                "type": ptype,
                "link": link,
                "category": category,
            })
        if papers:
            out[keyword] = papers
    return out


def collect_all_summaries(root: Path) -> list[dict]:
    """遍历项目目录，收集所有 statistics_summary.txt 的解析结果。"""
    data = []
    for path in root.rglob("*_statistics_summary.txt"):
        parsed = parse_summary_file(path)
        if parsed and parsed["total_papers"] > 0:
            data.append(parsed)
    # 按会议名、年份排序
    data.sort(key=lambda x: (x["conference"], x["year"]), reverse=True)
    return data


def build_aggregate(data: list[dict]) -> dict:
    """汇总：各会议各年论文数、会议列表、年份列表等。"""
    by_conf_year = {}
    conferences = set()
    years = set()
    details_with_top = []
    for d in data:
        c, y = d["conference"], d["year"]
        conferences.add(c)
        years.add(y)
        top_cat = d["categories"][:15]
        top_org = d["organizations"][:30]
        by_conf_year[(c, y)] = {
            "total_papers": d["total_papers"],
            "total_categories": d["total_categories"],
            "total_organizations": d["total_organizations"],
            "top_categories": top_cat,
            "top_organizations": top_org
        }
        details_with_top.append({
            **d,
            "top_categories": top_cat,
            "top_organizations": top_org
        })

    return {
        "conferences": sorted(conferences),
        "years": sorted(years),
        "by_conference_year": {f"{c}_{y}": v for (c, y), v in by_conf_year.items()},
        "details": details_with_top
    }


def main():
    root = Path(__file__).resolve().parent
    data = collect_all_summaries(root)
    if not data:
        print("未找到任何 statistics_summary.txt 文件")
        return

    agg = build_aggregate(data)
    agg["wanted_papers"] = parse_wanted_papers(root)
    out_json = root / "dashboard_data.json"
    out_json.write_text(json.dumps(agg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成: {out_json}")

    # 生成单文件 HTML，内嵌 JSON，便于直接用浏览器打开
    html_path = root / "dashboard.html"
    html_content = read_template_and_embed(agg)
    html_path.write_text(html_content, encoding="utf-8")
    print(f"已生成: {html_path}，用浏览器打开即可查看大屏。")


def read_template_and_embed(agg: dict) -> str:
    """读取 dashboard_template.html（若存在）或使用内联模板，并嵌入 agg 数据。"""
    root = Path(__file__).resolve().parent
    template_path = root / "dashboard_template.html"
    if template_path.exists():
        tpl = template_path.read_text(encoding="utf-8")
    else:
        tpl = get_inline_template()
    # 将 DATA 占位符替换为 JSON
    json_str = json.dumps(agg, ensure_ascii=False)
    return tpl.replace("/* __DASHBOARD_DATA__ */", json_str)


def get_inline_template() -> str:
    """返回内联的 HTML 模板（占位符 __DASHBOARD_DATA__ 在 build_dashboard 里替换）。"""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AI 顶会论文统计大屏</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
      background: #0a0a12;
      background-image: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0,212,255,0.15), transparent),
        radial-gradient(ellipse 60% 40% at 100% 100%, rgba(123,44,191,0.12), transparent),
        linear-gradient(180deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
      min-height: 100vh;
      color: #e0e0e0;
      overflow-x: hidden;
    }
    .dashboard { max-width: 1920px; margin: 0 auto; padding: 20px; }
    header {
      text-align: center;
      padding: 20px 0 24px;
      border-bottom: 2px solid rgba(0, 212, 255, 0.35);
      margin-bottom: 20px;
    }
    header h1 {
      font-size: clamp(1.8rem, 4vw, 2.8rem);
      font-weight: 700;
      background: linear-gradient(90deg, #00d4ff, #a855f7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-shadow: 0 0 40px rgba(0,212,255,0.3);
    }
    header p { margin-top: 6px; opacity: 0.9; font-size: 0.95rem; }
    .kpi-strip {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 32px;
      margin-bottom: 24px;
      padding: 20px 24px;
      background: rgba(0,212,255,0.06);
      border: 1px solid rgba(0,212,255,0.2);
      border-radius: 12px;
    }
    .kpi-item { text-align: center; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #00d4ff; font-variant-numeric: tabular-nums; }
    .kpi-label { font-size: 0.85rem; opacity: 0.85; margin-top: 4px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 18px;
      margin-bottom: 22px;
    }
    .card {
      background: rgba(20, 20, 40, 0.75);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid rgba(0, 212, 255, 0.18);
      box-shadow: 0 4px 24px rgba(0,0,0,0.25);
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .card:hover { border-color: rgba(0,212,255,0.35); box-shadow: 0 6px 28px rgba(0,212,255,0.08); }
    .card h2 {
      font-size: 1.1rem;
      margin-bottom: 10px;
      color: #00d4ff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .card h2::before { content: ''; width: 4px; height: 18px; background: #00d4ff; border-radius: 2px; }
    .total-big { font-size: 2rem; font-weight: 700; color: #fff; margin: 6px 0; font-variant-numeric: tabular-nums; }
    .meta { font-size: 0.85rem; opacity: 0.8; margin-top: 4px; }
    .chart-row {
      display: flex;
      align-items: flex-end;
      gap: 6px;
      height: 110px;
      margin-top: 14px;
      padding-top: 6px;
    }
    .bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; }
    .bar {
      width: 100%;
      max-width: 26px;
      border-radius: 6px 6px 0 0;
      min-height: 4px;
      transition: height 0.35s ease;
    }
    .bar-label { font-size: 0.68rem; margin-top: 4px; opacity: 0.9; }
    .table-wrap { overflow-x: auto; max-height: 260px; overflow-y: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    th, td { padding: 5px 8px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
    th { color: #00d4ff; font-weight: 600; position: sticky; top: 0; background: rgba(20,20,40,0.98); }
    tr:hover { background: rgba(0, 212, 255, 0.06); }
    .num { text-align: right; font-variant-numeric: tabular-nums; }
    .full-width { grid-column: 1 / -1; }
    .year-bars { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 10px; }
    .year-bar-item { display: flex; align-items: center; gap: 8px; }
    .year-bar-item .bar-bg { width: 100px; height: 22px; background: rgba(255,255,255,0.08); border-radius: 6px; overflow: hidden; }
    .year-bar-item .bar-fill { height: 100%; border-radius: 6px; transition: width 0.6s ease; }
    .year-bar-item span { font-variant-numeric: tabular-nums; min-width: 32px; font-size: 0.9rem; }
    .section-title { font-size: 1rem; color: rgba(255,255,255,0.7); margin-bottom: 10px; padding-left: 4px; }
    .tab-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 18px;
      padding: 6px 0;
      border-bottom: 2px solid rgba(0, 212, 255, 0.25);
    }
    .tab-btn {
      padding: 10px 20px;
      border: 1px solid rgba(0, 212, 255, 0.3);
      border-radius: 8px;
      background: rgba(20, 20, 40, 0.6);
      color: #e0e0e0;
      font-size: 0.95rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s, color 0.2s;
    }
    .tab-btn:hover {
      background: rgba(0, 212, 255, 0.15);
      border-color: rgba(0, 212, 255, 0.5);
      color: #00d4ff;
    }
    .tab-btn.active {
      background: rgba(0, 212, 255, 0.25);
      border-color: #00d4ff;
      color: #00d4ff;
    }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }
    .sub-tab-bar {
      display: flex;
      gap: 6px;
      margin-bottom: 12px;
      padding: 4px 0;
    }
    .sub-tab-btn {
      padding: 8px 16px;
      border: 1px solid rgba(0, 212, 255, 0.3);
      border-radius: 6px;
      background: rgba(20, 20, 40, 0.5);
      color: #b0b0b0;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background 0.2s, border-color 0.2s, color 0.2s;
    }
    .sub-tab-btn:hover { background: rgba(0, 212, 255, 0.1); color: #e0e0e0; border-color: rgba(0, 212, 255, 0.4); }
    .sub-tab-btn.active { background: rgba(0, 212, 255, 0.2); border-color: #00d4ff; color: #00d4ff; }
    .sub-tab-panel { display: none; }
    .sub-tab-panel.active { display: block; }
    .wanted-wrap { max-height: 70vh; overflow: auto; margin-top: 8px; }
    .wanted-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
    .wanted-table th, .wanted-table td { padding: 8px 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); }
    .wanted-table th { color: #00d4ff; font-weight: 600; position: sticky; top: 0; background: rgba(20,20,40,0.98); }
    .wanted-table tr:hover { background: rgba(0, 212, 255, 0.06); }
    .wanted-table .col-no { width: 48px; text-align: center; }
    .wanted-table .col-type { width: 80px; }
    .wanted-table .col-source { width: 100px; }
    .wanted-table a { color: #00d4ff; text-decoration: none; }
    .wanted-table a:hover { text-decoration: underline; }
    .wanted-title { max-width: 420px; }
  </style>
</head>
<body>
  <div class="dashboard">
    <header>
      <h1>AI 顶会论文统计大屏</h1>
      <p>基于各会议 statistics_summary 的论文数量、类别与机构统计</p>
    </header>

    <div class="kpi-strip" id="kpiStrip"></div>
    <div class="tab-bar" id="tabBar"></div>
    <div id="tabPanels"></div>
  </div>
  <script>
    const DATA = /* __DASHBOARD_DATA__ */ {};
    (function() {
      const details = DATA.details || [];
      const conferences = DATA.conferences || [];
      const years = DATA.years || [];
      var wantedPapers = DATA.wanted_papers || {};
      var wantedKeywords = Object.keys(wantedPapers);
      if (!details.length && !wantedKeywords.length) {
        document.body.innerHTML = '<div class="dashboard"><header><h1>AI 顶会论文统计大屏</h1><p>暂无数据。请在项目根目录运行 <code>python build_dashboard.py</code> 生成数据后刷新本页。</p></header></div>';
        return;
      }

      const colors = ['#00d4ff', '#7b2cbf', '#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3', '#f38181', '#aa96da'];
      function colorFor(i) { return colors[i % colors.length]; }
      function escapeHtml(s) { const div = document.createElement('div'); div.textContent = s; return div.innerHTML; }
      function truncate(s, len) { return s.length <= len ? s : s.slice(0, len) + '\u2026'; }

      const totalPapers = details.reduce((s, d) => s + d.total_papers, 0);
      const yearRange = years.length ? years[0] + ' \u2013 ' + years[years.length - 1] : '\u2014';
      document.getElementById('kpiStrip').innerHTML = `
        <div class="kpi-item"><div class="kpi-value">${totalPapers.toLocaleString()}</div><div class="kpi-label">总论文数</div></div>
        <div class="kpi-item"><div class="kpi-value">${conferences.length}</div><div class="kpi-label">会议数</div></div>
        <div class="kpi-item"><div class="kpi-value">${yearRange}</div><div class="kpi-label">年份范围</div></div>
        <div class="kpi-item"><div class="kpi-value">${details.length}</div><div class="kpi-label">统计条目</div></div>
      `;

      var byConfDetails = {};
      details.forEach(function(d) {
        if (!byConfDetails[d.conference]) byConfDetails[d.conference] = [];
        byConfDetails[d.conference].push(d);
      });
      conferences.forEach(function(conf) {
        if (byConfDetails[conf]) byConfDetails[conf].sort(function(a, b) { return b.year.localeCompare(a.year); });
      });

      var tabBar = document.getElementById('tabBar');
      var tabPanels = document.getElementById('tabPanels');

      conferences.forEach(function(conf, confIdx) {
        var list = byConfDetails[conf] || [];
        var confColor = colorFor(confIdx);

        var btn = document.createElement('button');
        btn.className = 'tab-btn' + (confIdx === 0 ? ' active' : '');
        btn.type = 'button';
        btn.textContent = conf;
        btn.style.borderColor = confIdx === 0 ? confColor : '';
        btn.dataset.conf = conf;
        tabBar.appendChild(btn);

        var panel = document.createElement('div');
        panel.id = 'panel-' + conf;
        panel.className = 'tab-panel' + (confIdx === 0 ? ' active' : '');
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-label', conf);

        var overviewGrid = document.createElement('section');
        overviewGrid.className = 'grid';
        var yearChartGrid = document.createElement('section');
        yearChartGrid.className = 'grid';

        var t1 = document.createElement('p');
        t1.className = 'section-title';
        t1.textContent = conf + ' \u5404\u5e74\u5ea6\u8bba\u6587\u6570';
        panel.appendChild(t1);
        panel.appendChild(overviewGrid);

        var t2 = document.createElement('p');
        t2.className = 'section-title';
        t2.textContent = conf + ' \u5e74\u5ea6\u8d8b\u52bf';
        panel.appendChild(t2);
        panel.appendChild(yearChartGrid);

        var t3 = document.createElement('p');
        t3.className = 'section-title';
        t3.textContent = conf + ' \u7c7b\u522b\u4e0e\u673a\u6784 Top';
        panel.appendChild(t3);
        var subTabBar = document.createElement('div');
        subTabBar.className = 'sub-tab-bar';
        subTabBar.innerHTML = '<button type="button" class="sub-tab-btn active" data-sub="cat">\u7c7b\u522b</button><button type="button" class="sub-tab-btn" data-sub="org">\u673a\u6784</button>';
        panel.appendChild(subTabBar);
        var catPanel = document.createElement('div');
        catPanel.className = 'sub-tab-panel active';
        catPanel.dataset.sub = 'cat';
        var orgPanel = document.createElement('div');
        orgPanel.className = 'sub-tab-panel';
        orgPanel.dataset.sub = 'org';
        var catGrid = document.createElement('section');
        catGrid.className = 'grid';
        var orgGrid = document.createElement('section');
        orgGrid.className = 'grid';
        catPanel.appendChild(catGrid);
        orgPanel.appendChild(orgGrid);
        panel.appendChild(catPanel);
        panel.appendChild(orgPanel);

        list.forEach(function(d, idx) {
          var card = document.createElement('div');
          card.className = 'card';
          card.innerHTML = '<h2>' + conf + ' ' + d.year + '</h2>' +
            '<div class="total-big">' + d.total_papers.toLocaleString() + '</div>' +
            '<div class="meta">\u7c7b\u522b\u6570: ' + d.total_categories + ' \u00b7 \u673a\u6784\u6570: ' + d.total_organizations + '</div>' +
            '<div class="chart-row"></div>';
          var chartRow = card.querySelector('.chart-row');
          if (d.top_categories && d.top_categories.length) {
            var topCat = d.top_categories.slice(0, 10);
            var maxC = Math.max.apply(null, topCat.map(function(x) { return x.count; })) || 1;
            topCat.forEach(function(c) {
              var wrap = document.createElement('div');
              wrap.className = 'bar-wrap';
              var bar = document.createElement('div');
              bar.className = 'bar';
              bar.style.height = (80 * c.count / maxC) + 'px';
              bar.style.background = confColor;
              wrap.appendChild(bar);
              var lbl = document.createElement('div');
              lbl.className = 'bar-label';
              lbl.textContent = c.count;
              lbl.title = c.name;
              wrap.appendChild(lbl);
              chartRow.appendChild(wrap);
            });
          }
          overviewGrid.appendChild(card);
        });

        var arr = list.slice().sort(function(a, b) { return a.year.localeCompare(b.year); });
        var maxP = Math.max.apply(null, arr.map(function(x) { return x.total_papers; })) || 1;
        var trendCard = document.createElement('div');
        trendCard.className = 'card';
        var inner = arr.map(function(a) {
          return '<div class="year-bar-item">' +
            '<span>' + a.year + '</span>' +
            '<div class="bar-bg"><div class="bar-fill" style="width:' + (100 * a.total_papers / maxP) + '%; background:' + confColor + '"></div></div>' +
            '<span>' + a.total_papers + '</span></div>';
        }).join('');
        trendCard.innerHTML = '<h2>' + conf + ' \u5e74\u5ea6\u8bba\u6587\u6570</h2><div class="year-bars">' + inner + '</div>';
        yearChartGrid.appendChild(trendCard);

        list.forEach(function(d) {
          var catRows = (d.top_categories || []).slice(0, 15).map(function(c) {
            return '<tr><td>' + c.rank + '</td><td title="' + escapeHtml(c.name) + '">' + truncate(c.name, 32) + '</td><td class="num">' + c.count + '</td><td class="num">' + c.percentage + '%</td></tr>';
          }).join('');
          var orgRows = (d.top_organizations || []).slice(0, 20).map(function(o) {
            return '<tr><td>' + o.rank + '</td><td title="' + escapeHtml(o.name) + '">' + truncate(o.name, 30) + '</td><td class="num">' + o.count + '</td><td class="num">' + o.percentage + '%</td></tr>';
          }).join('');
          var catCard = document.createElement('div');
          catCard.className = 'card';
          catCard.innerHTML = '<h2>' + conf + ' ' + d.year + ' \u7c7b\u522b Top</h2>' +
            '<div class="table-wrap"><table><thead><tr><th>#</th><th>\u7c7b\u522b</th><th>\u6570\u91cf</th><th>\u5360\u6bd4</th></tr></thead><tbody>' + (catRows || '<tr><td colspan="4">\u65e0</td></tr>') + '</tbody></table></div>';
          catGrid.appendChild(catCard);
          var orgCard = document.createElement('div');
          orgCard.className = 'card';
          orgCard.innerHTML = '<h2>' + conf + ' ' + d.year + ' \u673a\u6784 Top</h2>' +
            '<div class="table-wrap"><table><thead><tr><th>#</th><th>\u673a\u6784</th><th>\u8bba\u6587\u6570</th><th>\u5360\u6bd4</th></tr></thead><tbody>' + (orgRows || '<tr><td colspan="4">\u65e0</td></tr>') + '</tbody></table></div>';
          orgGrid.appendChild(orgCard);
        });

        subTabBar.addEventListener('click', function(e) {
          var b = e.target;
          if (!b.classList || !b.classList.contains('sub-tab-btn')) return;
          var sub = b.dataset.sub;
          subTabBar.querySelectorAll('.sub-tab-btn').forEach(function(x) { x.classList.remove('active'); });
          b.classList.add('active');
          catPanel.classList.toggle('active', sub === 'cat');
          orgPanel.classList.toggle('active', sub === 'org');
        });

        tabPanels.appendChild(panel);
      });

      if (wantedKeywords.length > 0) {
        var wantBtn = document.createElement('button');
        wantBtn.className = 'tab-btn';
        wantBtn.type = 'button';
        wantBtn.textContent = '\u7cbe\u9009\u8bba\u6587';
        wantBtn.dataset.conf = 'WANTED';
        tabBar.appendChild(wantBtn);

        var wantPanel = document.createElement('div');
        wantPanel.id = 'panel-WANTED';
        wantPanel.className = 'tab-panel';
        wantPanel.setAttribute('role', 'tabpanel');
        wantPanel.setAttribute('aria-label', 'WANTED');

        var wantSubBar = document.createElement('div');
        wantSubBar.className = 'sub-tab-bar';
        wantedKeywords.forEach(function(kw, i) {
          var sb = document.createElement('button');
          sb.type = 'button';
          sb.className = 'sub-tab-btn' + (i === 0 ? ' active' : '');
          sb.textContent = kw;
          sb.dataset.kw = kw;
          wantSubBar.appendChild(sb);
        });
        wantPanel.appendChild(wantSubBar);
        if (conferences.length === 0) {
          wantBtn.classList.add('active');
          wantPanel.classList.add('active');
        }

        wantedKeywords.forEach(function(kw, i) {
          var subPanel = document.createElement('div');
          subPanel.className = 'sub-tab-panel' + (i === 0 ? ' active' : '');
          subPanel.dataset.kw = kw;
          var list = wantedPapers[kw] || [];
          var rows = list.map(function(p) {
            var linkHtml = p.link ? '<a href="' + escapeHtml(p.link) + '" target="_blank" rel="noopener">\u67e5\u770b</a>' : '\u2014';
            var title = (p.title_en || p.title_zh || '').substring(0, 80);
            if ((p.title_en || p.title_zh || '').length > 80) title += '\u2026';
            return '<tr><td class="col-no">' + p.no + '</td><td class="wanted-title" title="' + escapeHtml(p.title_en || p.title_zh) + '">' + escapeHtml(title) + '</td><td class="col-source">' + escapeHtml(p.source) + '</td><td class="col-type">' + escapeHtml(p.type) + '</td><td>' + linkHtml + '</td></tr>';
          }).join('');
          subPanel.innerHTML = '<div class="wanted-wrap"><table class="wanted-table"><thead><tr><th class="col-no">\u5e8f\u53f7</th><th>\u6807\u9898</th><th class="col-source">\u6765\u6e90</th><th class="col-type">\u7c7b\u578b</th><th>\u94fe\u63a5</th></tr></thead><tbody>' + (rows || '<tr><td colspan="5">\u65e0</td></tr>') + '</tbody></table></div>';
          wantPanel.appendChild(subPanel);
        });

        wantSubBar.addEventListener('click', function(e) {
          var b = e.target;
          if (!b.classList || !b.classList.contains('sub-tab-btn')) return;
          var kw = b.dataset.kw;
          wantSubBar.querySelectorAll('.sub-tab-btn').forEach(function(x) { x.classList.remove('active'); });
          b.classList.add('active');
          wantPanel.querySelectorAll('.sub-tab-panel').forEach(function(p) { p.classList.remove('active'); });
          var sp = wantPanel.querySelector('.sub-tab-panel[data-kw="' + kw + '"]');
          if (sp) sp.classList.add('active');
        });

        tabPanels.appendChild(wantPanel);
      }

      tabBar.addEventListener('click', function(e) {
        var btn = e.target;
        if (btn.classList && btn.classList.contains('tab-btn')) {
          var conf = btn.dataset.conf;
          if (!conf) return;
          tabBar.querySelectorAll('.tab-btn').forEach(function(b) {
            b.classList.remove('active');
            b.style.borderColor = '';
          });
          btn.classList.add('active');
          btn.style.borderColor = colorFor(conferences.indexOf(conf));
          tabPanels.querySelectorAll('.tab-panel').forEach(function(p) {
            p.classList.remove('active');
          });
          var panel = document.getElementById('panel-' + conf);
          if (panel) panel.classList.add('active');
        }
      });
    })();
  </script>
</body>
</html>"""


if __name__ == "__main__":
    main()
