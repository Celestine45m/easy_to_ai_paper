# -*- coding: utf-8 -*-
"""分析 vfp_vi_t_vuln_base_info.csv 中极危/高危漏洞的通用场景"""
import csv
from collections import defaultdict

csv_path = r"d:\vfp_vi_t_vuln_base_info.csv"

# 列: CVE_ID, 等级, 标题, 漏洞类型, 描述
level_type_count = defaultdict(lambda: defaultdict(int))  # level -> { vuln_type: count }
level_total = defaultdict(int)

with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 4:
            continue
        cve_id, level, title, vuln_type = row[0], row[1], row[2], row[3]
        level = level.strip()
        vuln_type = vuln_type.strip()
        if not vuln_type:
            vuln_type = "(空)"
        level_total[level] += 1
        # 漏洞类型可能包含多个用 | 分隔
        for t in vuln_type.replace("|", ",").split(","):
            t = t.strip()
            if t:
                level_type_count[level][t] += 1

out_lines = []
for target in ["极危", "高危"]:
    out_lines.append(f"\n========== {target} 漏洞 ==========")
    out_lines.append(f"总条数: {level_total.get(target, 0)}")
    types = level_type_count.get(target, {})
    total = sum(types.values())
    sorted_types = sorted(types.items(), key=lambda x: -x[1])[:25]
    out_lines.append(f"\n漏洞类型分布 (Top 25):")
    for t, cnt in sorted_types:
        pct = 100.0 * cnt / total if total else 0
        out_lines.append(f"  {cnt:6d} ({pct:5.2f}%)  {t}")

out_path = r"d:\llm\model\easy_to_ai_papers\vuln_severity_analysis.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print("Written to", out_path)
