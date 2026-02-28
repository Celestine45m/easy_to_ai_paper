#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合并的统计分析工具：同时统计论文的类别分布和机构分布
"""

import json
from collections import Counter
from pathlib import Path


def analyze_categories(json_file_path):
    """
    读取JSON文件，统计category字段的分布
    
    Args:
        json_file_path: JSON文件路径
        
    Returns:
        Counter对象，包含category及其出现次数
    """
    category_counter = Counter()
    
    # 读取JSON文件（每行一个JSON对象）
    with open(json_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue
            
            try:
                # 解析JSON对象
                paper = json.loads(line)
                
                # 提取category字段
                category = paper.get('category', 'Unknown')
                
                # 统计
                category_counter[category] += 1
                
            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行JSON解析失败: {e}")
                continue
            except Exception as e:
                print(f"警告: 第 {line_num} 行处理出错: {e}")
                continue
    
    return category_counter


def analyze_affiliations(json_file_path, first_author_only=True):
    """
    读取JSON文件，统计affiliations字段的分布
    
    Args:
        json_file_path: JSON文件路径
        first_author_only: 如果为True，只统计第一作者的机构；否则统计所有机构
        
    Returns:
        Counter对象，包含机构及其出现次数，总论文数
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


def print_category_statistics(category_counter, conference_name, year):
    """
    打印类别统计结果
    
    Args:
        category_counter: Counter对象
        conference_name: 会议名称
        year: 年份
    """
    # 按出现次数降序排列
    sorted_categories = category_counter.most_common()
    
    # 计算总数
    total_papers = sum(category_counter.values())
    
    print("=" * 80)
    print(f"{conference_name} {year} 论文类别统计（按出现次数降序）")
    print("=" * 80)
    print(f"\n总论文数: {total_papers}\n")
    print(f"{'排名':<6} {'类别':<50} {'数量':<10} {'占比':<10}")
    print("-" * 80)
    
    for rank, (category, count) in enumerate(sorted_categories, 1):
        percentage = (count / total_papers) * 100
        print(f"{rank:<6} {category:<50} {count:<10} {percentage:>6.2f}%")
    
    print("=" * 80)


def save_category_statistics(category_counter, output_file, conference_name, year):
    """
    保存类别统计结果到文件
    
    Args:
        category_counter: Counter对象
        output_file: 输出文件路径
        conference_name: 会议名称
        year: 年份
    """
    sorted_categories = category_counter.most_common()
    total_papers = sum(category_counter.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"{conference_name} {year} 论文类别统计（按出现次数降序）\n")
        f.write("=" * 80 + "\n")
        f.write(f"\n总论文数: {total_papers}\n\n")
        f.write(f"{'排名':<6} {'类别':<50} {'数量':<10} {'占比':<10}\n")
        f.write("-" * 80 + "\n")
        
        for rank, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / total_papers) * 100
            f.write(f"{rank:<6} {category:<50} {count:<10} {percentage:>6.2f}%\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"\n类别统计结果已保存到: {output_file}")


def print_affiliation_statistics(affiliation_counter, total_papers, top_n=50, first_author_only=True, conference_name="", year=""):
    """
    打印机构统计结果
    
    Args:
        affiliation_counter: Counter对象
        total_papers: 总论文数
        top_n: 显示前N个机构
        first_author_only: 是否只统计第一作者机构
        conference_name: 会议名称
        year: 年份
    """
    # 按出现次数降序排列
    sorted_affiliations = affiliation_counter.most_common()
    
    print("=" * 100)
    if first_author_only:
        print(f"{conference_name} {year} 论文机构统计（仅第一作者机构，按出现次数降序）")
    else:
        print(f"{conference_name} {year} 论文机构统计（所有机构，按出现次数降序）")
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


def save_affiliation_statistics(affiliation_counter, total_papers, output_file='affiliation_statistics.txt', top_n=None, first_author_only=True, conference_name="", year=""):
    """
    保存机构统计结果到文件
    
    Args:
        affiliation_counter: Counter对象
        total_papers: 总论文数
        output_file: 输出文件路径
        top_n: 保存前N个机构（None表示保存全部）
        first_author_only: 是否只统计第一作者机构
        conference_name: 会议名称
        year: 年份
    """
    sorted_affiliations = affiliation_counter.most_common()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        if first_author_only:
            f.write(f"{conference_name} {year} 论文机构统计（仅第一作者机构，按出现次数降序）\n")
        else:
            f.write(f"{conference_name} {year} 论文机构统计（所有机构，按出现次数降序）\n")
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
    
    print(f"\n机构统计结果已保存到: {output_file}")


def save_summary_statistics(category_counter, affiliation_counter, total_papers, 
                           output_file, conference_name, year, first_author_only=True):
    """
    保存汇总统计结果到文件（包含类别、机构统计）
    
    Args:
        category_counter: 类别统计Counter对象
        affiliation_counter: 机构统计Counter对象
        total_papers: 总论文数
        output_file: 输出文件路径
        conference_name: 会议名称
        year: 年份
        first_author_only: 是否只统计第一作者机构
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write(f"{conference_name} {year} 论文统计分析汇总报告\n")
        f.write("=" * 100 + "\n\n")
        
        # ========== 类别统计 ==========
        sorted_categories = category_counter.most_common()
        total_category_papers = sum(category_counter.values())
        
        f.write("【一、论文类别统计】\n")
        f.write("=" * 100 + "\n")
        f.write(f"总论文数: {total_category_papers}\n")
        f.write(f"总类别数: {len(category_counter)}\n\n")
        f.write(f"{'排名':<6} {'类别':<50} {'数量':<10} {'占比':<10}\n")
        f.write("-" * 100 + "\n")
        
        for rank, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / total_category_papers) * 100
            f.write(f"{rank:<6} {category:<50} {count:<10} {percentage:>6.2f}%\n")
        
        f.write("\n\n")
        
        # ========== 机构统计 ==========
        sorted_affiliations = affiliation_counter.most_common()
        
        f.write("【二、论文机构统计】\n")
        f.write("=" * 100 + "\n")
        if first_author_only:
            f.write("统计模式: 仅第一作者机构\n")
        else:
            f.write("统计模式: 所有机构\n")
        f.write(f"总论文数: {total_papers}\n")
        f.write(f"总机构数: {len(affiliation_counter)}\n\n")
        f.write(f"{'排名':<6} {'机构名称':<70} {'论文数':<10} {'占比':<10}\n")
        f.write("-" * 100 + "\n")
        
        for rank, (affiliation, count) in enumerate(sorted_affiliations, 1):
            percentage = (count / total_papers) * 100
            f.write(f"{rank:<6} {affiliation:<70} {count:<10} {percentage:>6.2f}%\n")
        
        f.write("\n" + "=" * 100 + "\n")
        f.write("报告生成完成\n")
        f.write("=" * 100 + "\n")
    
    print(f"\n汇总统计报告已保存到: {output_file}")


def main():
    """主函数：同时执行类别统计和机构统计"""
    # 配置参数
    paper_list = ["ICLR", "ICML", "NeurIPS", "AAAI", "IJCAI", "ACL", "EMNLP"]
    year = "2024"
    first_author_only = False  # 改为True只统计第一作者机构
    
    for paper in paper_list:
        json_file = Path(f"{paper}/{paper}_{year}_accepted.json")
        
        if not json_file.exists():
            print(f"跳过: 文件不存在: {json_file}")
            continue
        
        print(f"\n{'='*100}")
        print(f"正在处理: {paper} {year}")
        print(f"{'='*100}\n")
        
        # ========== 类别统计 ==========
        print("=" * 80)
        print("【1/2】开始统计类别分布...")
        print("=" * 80)
        category_counter = analyze_categories(json_file)
        print_category_statistics(category_counter, paper, year)

        
        # ========== 机构统计 ==========
        print("\n" + "=" * 80)
        print("【2/2】开始统计机构分布...")
        print("=" * 80)
        if first_author_only:
            print("统计模式: 仅第一作者机构\n")
        else:
            print("统计模式: 所有机构\n")
        
        affiliation_counter, total_papers = analyze_affiliations(json_file, first_author_only=first_author_only)
        print_affiliation_statistics(affiliation_counter, total_papers, top_n=50, 
                                     first_author_only=first_author_only, 
                                     conference_name=paper, year=year)

        # ========== 保存汇总报告 ==========
        summary_output_file = f'{paper}/{paper}_{year}_statistics_summary.txt'
        save_summary_statistics(category_counter, affiliation_counter, total_papers,
                               summary_output_file, paper, year, first_author_only)
        
        print(f"\n✅ {paper} {year} 统计完成！\n")


if __name__ == "__main__":
    main()