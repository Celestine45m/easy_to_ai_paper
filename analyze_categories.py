#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计NeurIPS 2025接受论文的category分布
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


def print_statistics(category_counter):
    """
    打印统计结果
    
    Args:
        category_counter: Counter对象
    """
    # 按出现次数降序排列
    sorted_categories = category_counter.most_common()
    
    # 计算总数
    total_papers = sum(category_counter.values())
    
    print("=" * 80)
    print("NeurIPS 2025 论文类别统计（按出现次数降序）")
    print("=" * 80)
    print(f"\n总论文数: {total_papers}\n")
    print(f"{'排名':<6} {'类别':<50} {'数量':<10} {'占比':<10}")
    print("-" * 80)
    
    for rank, (category, count) in enumerate(sorted_categories, 1):
        percentage = (count / total_papers) * 100
        print(f"{rank:<6} {category:<50} {count:<10} {percentage:>6.2f}%")
    
    print("=" * 80)


def save_statistics(category_counter, output_file):
    """
    保存统计结果到文件
    
    Args:
        category_counter: Counter对象
        output_file: 输出文件路径
    """
    sorted_categories = category_counter.most_common()
    total_papers = sum(category_counter.values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("NeurIPS 2025 论文类别统计（按出现次数降序）\n")
        f.write("=" * 80 + "\n")
        f.write(f"\n总论文数: {total_papers}\n\n")
        f.write(f"{'排名':<6} {'类别':<50} {'数量':<10} {'占比':<10}\n")
        f.write("-" * 80 + "\n")
        
        for rank, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / total_papers) * 100
            f.write(f"{rank:<6} {category:<50} {count:<10} {percentage:>6.2f}%\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"\n统计结果已保存到: {output_file}")


def main():
    """主函数"""
    # JSON文件路径

    paper = "NeurIPS"
    year = "2025"
    json_file = Path(f"{paper}/{paper}_{year}_accepted.json")
    output_file=f'{paper}/{paper}_{year}_category_statistics.txt'

    if not json_file.exists():
        print(f"错误: 文件不存在: {json_file}")
        return
    
    print(f"正在读取文件: {json_file}")
    print("正在统计category分布...\n")
    
    # 统计category
    category_counter = analyze_categories(json_file)
    
    # 打印结果
    print_statistics(category_counter)
    
    # 保存结果
    save_statistics(category_counter, output_file)
    
    # 返回Counter对象供进一步使用
    return category_counter


if __name__ == "__main__":
    result = main()
