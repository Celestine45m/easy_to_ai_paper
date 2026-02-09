#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计NeurIPS 2025接受论文的机构分布
"""

import json
from collections import Counter
from pathlib import Path


def analyze_affiliations(json_file_path, first_author_only=True):
    """
    读取JSON文件，统计affiliations字段的分布
    
    Args:
        json_file_path: JSON文件路径
        first_author_only: 如果为True，只统计第一作者的机构；否则统计所有机构
        
    Returns:
        Counter对象，包含机构及其出现次数
    """
    affiliation_counter = Counter()
    total_papers = 0
    papers_without_first_author_affiliation = 0
    
    # 读取JSON文件（每行一个JSON对象）
    with open(json_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            try:
                # 解析JSON对象
                paper = json.loads(line)
                total_papers += 1
                
                # 提取authors和affiliations字段
                authors_str = paper.get('authors', '')
                affiliations_str = paper.get('affiliations', '')
                
                if not affiliations_str:
                    continue
                
                # 用分号分割机构和作者
                # 注意：affiliations字段格式可能是 ";Institution1;Institution2;"
                # 分割后可能包含空字符串，需要过滤
                affiliations = [aff.strip() for aff in affiliations_str.split(';') if aff.strip()]
                authors = [auth.strip() for auth in authors_str.split(';') if auth.strip()]
                
                if first_author_only:
                    # 只统计第一作者的机构
                    if authors and affiliations:
                        # 第一作者通常对应第一个机构（或第一个非空机构）
                        # 如果affiliations以分号开头，第一个元素可能是空，需要找到第一个非空机构
                        first_author_affiliation = affiliations[0] if affiliations else None
                        
                        if first_author_affiliation:
                            affiliation_counter[first_author_affiliation] += 1
                        else:
                            papers_without_first_author_affiliation += 1
                    else:
                        papers_without_first_author_affiliation += 1
                else:
                    # 统计所有机构
                    for affiliation in affiliations:
                        affiliation_counter[affiliation] += 1
                
            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行JSON解析失败: {e}")
                continue
            except Exception as e:
                print(f"警告: 第 {line_num} 行处理出错: {e}")
                continue
    
    if first_author_only and papers_without_first_author_affiliation > 0:
        print(f"注意: 有 {papers_without_first_author_affiliation} 篇论文无法确定第一作者机构\n")
    
    return affiliation_counter, total_papers


def print_statistics(affiliation_counter, total_papers, top_n=50, first_author_only=True):
    """
    打印统计结果
    
    Args:
        affiliation_counter: Counter对象
        total_papers: 总论文数
        top_n: 显示前N个机构
        first_author_only: 是否只统计第一作者机构
    """
    # 按出现次数降序排列
    sorted_affiliations = affiliation_counter.most_common()
    
    print("=" * 100)
    if first_author_only:
        print("NeurIPS 2025 论文机构统计（仅第一作者机构，按出现次数降序）")
    else:
        print("NeurIPS 2025 论文机构统计（所有机构，按出现次数降序）")
    print("=" * 100)
    print(f"\n总论文数: {total_papers}")
    print(f"总机构数: {len(affiliation_counter)}")
    print(f"显示前 {min(top_n, len(sorted_affiliations))} 个机构\n")
    print(f"{'排名':<6} {'机构名称':<70} {'论文数':<10} {'占比':<10}")
    print("-" * 100)
    
    # 显示前top_n个
    for rank, (affiliation, count) in enumerate(sorted_affiliations[:top_n], 1):
        percentage = (count / total_papers) * 100
        print(f"{rank:<6} {affiliation:<70} {count:<10} {percentage:>6.2f}%")
    
    print("=" * 100)
    
    # 显示一些统计信息
    if len(sorted_affiliations) > top_n:
        print(f"\n（还有 {len(sorted_affiliations) - top_n} 个机构未显示，完整结果请查看输出文件）")


def save_statistics(affiliation_counter, total_papers, output_file='affiliation_statistics.txt', top_n=None, first_author_only=True):
    """
    保存统计结果到文件
    
    Args:
        affiliation_counter: Counter对象
        total_papers: 总论文数
        output_file: 输出文件路径
        top_n: 保存前N个机构（None表示保存全部）
        first_author_only: 是否只统计第一作者机构
    """
    sorted_affiliations = affiliation_counter.most_common()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        if first_author_only:
            f.write("NeurIPS 2025 论文机构统计（仅第一作者机构，按出现次数降序）\n")
        else:
            f.write("NeurIPS 2025 论文机构统计（所有机构，按出现次数降序）\n")
        f.write("=" * 100 + "\n")
        f.write(f"\n总论文数: {total_papers}\n")
        f.write(f"总机构数: {len(affiliation_counter)}\n")
        
        if top_n:
            f.write(f"显示前 {min(top_n, len(sorted_affiliations))} 个机构\n")
        
        f.write(f"\n{'排名':<6} {'机构名称':<70} {'论文数':<10} {'占比':<10}\n")
        f.write("-" * 100 + "\n")
        
        # 保存前top_n个或全部
        affiliations_to_save = sorted_affiliations[:top_n] if top_n else sorted_affiliations
        
        for rank, (affiliation, count) in enumerate(affiliations_to_save, 1):
            percentage = (count / total_papers) * 100
            f.write(f"{rank:<6} {affiliation:<70} {count:<10} {percentage:>6.2f}%\n")
        
        f.write("=" * 100 + "\n")
    
    print(f"\n统计结果已保存到: {output_file}")


def analyze_by_country(affiliation_counter):
    """
    按国家/地区分析机构分布（简单版本，基于机构名称关键词）
    
    Args:
        affiliation_counter: Counter对象
        
    Returns:
        按国家/地区分组的统计
    """
    # 常见国家/地区关键词（可以根据需要扩展）
    country_keywords = {
        'USA': ['University', 'MIT', 'Stanford', 'Berkeley', 'Carnegie Mellon', 'Cornell', 
                'Princeton', 'Yale', 'Harvard', 'Columbia', 'NYU', 'UCLA', 'USC', 
                'Google', 'Meta', 'Microsoft', 'Amazon', 'Apple', 'NVIDIA', 'OpenAI'],
        'China': ['Tsinghua', 'Peking', 'Fudan', 'Shanghai', 'Beijing', 'Nanjing', 
                  'Harbin', 'Zhejiang', 'Chinese Academy', 'Hong Kong', 'Macau'],
        'UK': ['Oxford', 'Cambridge', 'Imperial', 'UCL', 'Edinburgh', 'Manchester'],
        'Germany': ['Munich', 'Tübingen', 'Berlin', 'Max Planck', 'ETH'],
        'Canada': ['Toronto', 'Montreal', 'Waterloo', 'McGill', 'British Columbia'],
        'Switzerland': ['ETH Zurich', 'EPFL'],
        'France': ['Paris', 'INRIA', 'CNRS'],
        'Japan': ['Tokyo', 'Kyoto', 'RIKEN'],
        'Singapore': ['Singapore'],
        'Australia': ['Australian', 'Sydney', 'Melbourne'],
        'Israel': ['Technion', 'Tel Aviv', 'Weizmann'],
    }
    
    country_stats = Counter()
    
    for affiliation, count in affiliation_counter.items():
        matched = False
        for country, keywords in country_keywords.items():
            if any(keyword.lower() in affiliation.lower() for keyword in keywords):
                country_stats[country] += count
                matched = True
                break
        if not matched:
            country_stats['Other'] += count
    
    return country_stats


def print_country_statistics(country_stats):
    """
    打印按国家/地区的统计
    
    Args:
        country_stats: 按国家分组的Counter对象
    """
    sorted_countries = country_stats.most_common()
    total = sum(country_stats.values())
    
    print("\n" + "=" * 80)
    print("按国家/地区统计（基于机构名称关键词，仅供参考）")
    print("=" * 80)
    print(f"{'排名':<6} {'国家/地区':<30} {'论文数':<10} {'占比':<10}")
    print("-" * 80)
    
    for rank, (country, count) in enumerate(sorted_countries, 1):
        percentage = (count / total) * 100
        print(f"{rank:<6} {country:<30} {count:<10} {percentage:>6.2f}%")
    
    print("=" * 80)


def main():
    """主函数"""
    # JSON文件路径
    paper = "ICLR"
    year = "2025"
    json_file = Path(f"{paper}/{paper}_{year}_accepted.json")
    if not json_file.exists():
        print(f"错误: 文件不存在: {json_file}")
        return
    
    # 设置是否只统计第一作者机构
    first_author_only = False  # 改为True只统计第一作者机构
    
    print(f"正在读取文件: {json_file}")
    if first_author_only:
        print("正在统计第一作者机构分布...\n")
    else:
        print("正在统计所有机构分布...\n")
    
    # 统计机构
    affiliation_counter, total_papers = analyze_affiliations(json_file, first_author_only=first_author_only)
    
    # 打印结果（显示前50个）
    print_statistics(affiliation_counter, total_papers, top_n=50, first_author_only=first_author_only)
    
    # 保存完整结果
    output_file = f'{paper}/{paper}_{year}_affiliation_statistics_first_author.txt' if first_author_only else f'{paper}/{paper}_{year}_affiliation_statistics.txt'
    
    save_statistics(affiliation_counter, total_papers, output_file=output_file, top_n=None, first_author_only=first_author_only)
    
    # 按国家/地区分析（可选）
    print("\n正在进行按国家/地区的统计分析...")
    country_stats = analyze_by_country(affiliation_counter)
    print_country_statistics(country_stats)
    
    # 返回结果供进一步使用
    return affiliation_counter, total_papers


if __name__ == "__main__":
    result = main()
