#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从Security目录下的4个JSON文件中提取标题包含"vuln"的论文
会议: CCS, NDSS, SP, USS
"""

import json
import time
from pathlib import Path
from src.llm.llm_client import translate_to_chinese


def extract_papers_from_ccs(json_data, keyword="vuln", case_sensitive=False):
    """从CCS JSON数据中提取匹配的论文"""
    matched_papers = []
    papers_by_year = json_data.get("papers_by_year", {})
    
    for year, papers in papers_by_year.items():
        for paper in papers:
            title = paper.get("title", "")
            if not title:
                continue
            
            # 检查标题是否包含关键词
            if case_sensitive:
                if keyword in title:
                    matched_papers.append({
                        "title": title,
                        "source": f"CCS {year}",
                        "doi": paper.get("doi", "N/A"),
                        "year": year
                    })
            else:
                if keyword.lower() in title.lower():
                    matched_papers.append({
                        "title": title,
                        "source": f"CCS {year}",
                        "doi": paper.get("doi", "N/A"),
                        "year": year
                    })
    
    return matched_papers


def extract_papers_from_ndss_sp_uss(json_data, conference_name, keyword="vuln", case_sensitive=False):
    """从NDSS/SP/USS JSON数据中提取匹配的论文（它们结构相同）"""
    matched_papers = []
    details = json_data.get("details", {})
    
    for year, year_data in details.items():
        papers = year_data.get("papers", [])
        for paper in papers:
            title = paper.get("title", "")
            if not title:
                continue
            
            # 检查标题是否包含关键词
            if case_sensitive:
                if keyword in title:
                    identifier = paper.get("identifier", {})
                    doi_or_url = identifier.get("value", "N/A")
                    matched_papers.append({
                        "title": title,
                        "source": f"{conference_name} {year}",
                        "doi": doi_or_url,
                        "year": year
                    })
            else:
                if keyword.lower() in title.lower():
                    identifier = paper.get("identifier", {})
                    doi_or_url = identifier.get("value", "N/A")
                    matched_papers.append({
                        "title": title,
                        "source": f"{conference_name} {year}",
                        "doi": doi_or_url,
                        "year": year
                    })
    
    return matched_papers


def translate_title(title, delay=2):
    """翻译论文标题"""
    try:
        translated = translate_to_chinese(title)
        time.sleep(delay)  # 延迟，避免请求过快
        return translated.strip()
    except Exception as e:
        print(f"  翻译失败: {e}")
        return ""


def save_to_txt(papers, output_file, keyword, translate_titles=False, delay=2, conf_counts=None):
    """将匹配的论文信息保存到txt文件"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"论文标题包含关键词 '{keyword}' 的论文列表\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"共找到 {len(papers)} 篇论文\n\n")
        
        # 写入会议统计
        if conf_counts:
            f.write("按会议统计:\n")
            for conf, count in sorted(conf_counts.items()):
                f.write(f"  {conf}: {count} 篇\n")
            f.write("\n")
        
        f.write("=" * 100 + "\n\n")
        
        for idx, paper in enumerate(papers, 1):
            title = paper.get('title', 'N/A')
            f.write(f"[No.{idx}] {title}\n")
            
            # 如果启用翻译，翻译标题
            if translate_titles:
                print(f"  正在翻译第 {idx}/{len(papers)} 篇: {title[:60]}...")
                title_ch = translate_title(title, delay)
                if title_ch:
                    f.write(f"标题(中): {title_ch}\n")
            
            f.write(f"来源: {paper.get('source', 'Unknown')}\n")
            f.write(f"年份: {paper.get('year', 'N/A')}\n")
            doi = paper.get('doi', 'N/A')
            if doi != 'N/A':
                if doi.startswith('http'):
                    f.write(f"链接: {doi}\n")
                else:
                    f.write(f"DOI: {doi}\n")
            f.write("-" * 100 + "\n\n")
        
        f.write("=" * 100 + "\n")
        f.write("报告生成完成\n")
        if translate_titles:
            f.write(f"已翻译 {len(papers)} 篇论文标题\n")
        
        # 再次写入会议统计（文件末尾）
        if conf_counts:
            f.write("\n" + "=" * 100 + "\n")
            f.write("按会议统计:\n")
            for conf, count in sorted(conf_counts.items()):
                f.write(f"  {conf}: {count} 篇\n")
        
        f.write("=" * 100 + "\n")
    
    print(f"\n结果已保存到: {output_file}")


def main():
    """主函数"""
    security_dir = Path("Security")
    keyword = "vuln"
    case_sensitive = False
    translate_titles = True  # 是否翻译标题
    request_delay = 2  # 翻译请求之间的延迟（秒）
    output_file = "Security/secpapers_with_vuln.txt"
    
    # 会议配置：文件名 -> 会议名称
    conferences = {
        "ccs.json": ("CCS", extract_papers_from_ccs),
        "ndss.json": ("NDSS", extract_papers_from_ndss_sp_uss),
        "sp.json": ("SP", extract_papers_from_ndss_sp_uss),
        "usenix.json": ("USENIX", extract_papers_from_ndss_sp_uss)
    }
    
    all_matched_papers = []
    
    print("=" * 100)
    print(f"开始从Security目录提取标题包含关键词 '{keyword}' 的论文...")
    print("=" * 100 + "\n")
    
    for json_file, (conf_name, extract_func) in conferences.items():
        json_path = security_dir / json_file
        
        if not json_path.exists():
            print(f"警告: 文件不存在，跳过: {json_path}")
            continue
        
        print(f"正在处理: {conf_name} ({json_file})...")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 根据文件类型调用不同的提取函数
            if json_file == "ccs.json":
                matched = extract_func(json_data, keyword, case_sensitive)
            else:
                matched = extract_func(json_data, conf_name, keyword, case_sensitive)
            
            all_matched_papers.extend(matched)
            print(f"  ✓ {conf_name} 处理完成，找到 {len(matched)} 篇匹配论文")
        
        except Exception as e:
            print(f"  ✗ {conf_name} 处理出错: {e}")
            continue
    
    # 按年份和标题排序
    all_matched_papers.sort(key=lambda x: (x.get('year', ''), x.get('title', '')))
    
    # 计算会议统计
    conf_counts = {}
    for paper in all_matched_papers:
        source = paper.get('source', 'Unknown')
        conf = source.split()[0]  # 提取会议名称
        conf_counts[conf] = conf_counts.get(conf, 0) + 1
    
    # 保存到文件
    if all_matched_papers:
        if translate_titles:
            print(f"\n开始翻译 {len(all_matched_papers)} 篇论文标题...")
            print("=" * 100)
        
        save_to_txt(all_matched_papers, output_file, keyword, translate_titles, request_delay, conf_counts)
        print(f"\n✅ 提取完成！共找到 {len(all_matched_papers)} 篇论文")
        
        # 打印会议统计
        print("\n按会议统计:")
        for conf, count in sorted(conf_counts.items()):
            print(f"  {conf}: {count} 篇")
    else:
        print(f"\n⚠️  未找到包含关键词 '{keyword}' 的论文")


if __name__ == "__main__":
    main()
