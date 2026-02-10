#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从所有AI会议的accepted.json中提取指定关键词的论文
"""

import json
from pathlib import Path


def extract_papers_by_keyword(keywords, case_sensitive=False):
    """
    从所有AI会议的JSON文件中提取标题包含指定关键词的论文
    
    Args:
        keywords: 要搜索的关键词，可以是字符串或列表。如果是列表，只要标题包含任意一个关键词就匹配（OR关系）
        case_sensitive: 是否区分大小写，默认为False（不区分大小写）
        
    Returns:
        list: 包含匹配论文信息的列表，每个元素是一个字典
    """
    # 将keywords统一转换为列表
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # 配置参数
    paper_list = ["ICLR", "ICML", "NeurIPS", "AAAI", "IJCAI", "ACL", "EMNLP"]
    year = "2025"
    
    matched_papers = []
    
    for conference in paper_list:
        json_file = Path(f"{conference}/{conference}_{year}_accepted.json")
        
        if not json_file.exists():
            print(f"警告: 文件不存在，跳过: {json_file}")
            continue
        
        print(f"正在处理: {conference} {year}...")
        
        # 读取JSON文件（每行一个JSON对象）
        with open(json_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                
                try:
                    # 解析JSON对象
                    paper = json.loads(line)
                    
                    # 提取title字段
                    title = paper.get('title', '')
                    
                    # 检查title中是否包含任意一个关键词，并记录所有命中的关键词
                    matched_keywords = []
                    if case_sensitive:
                        for keyword in keywords:
                            if keyword in title:
                                matched_keywords.append(keyword)
                    else:
                        title_lower = title.lower()
                        for keyword in keywords:
                            if keyword.lower() in title_lower:
                                matched_keywords.append(keyword)
                    
                    if matched_keywords:
                        # 添加来源字段和命中的关键词
                        paper['source'] = f"{conference} {year}"
                        paper['matched_keywords'] = matched_keywords
                        matched_papers.append(paper)
                
                except json.JSONDecodeError as e:
                    print(f"警告: {conference} 第 {line_num} 行JSON解析失败: {e}")
                    continue
                except Exception as e:
                    print(f"警告: {conference} 第 {line_num} 行处理出错: {e}")
                    continue
        
        print(f"  ✓ {conference} 处理完成，找到 {len([p for p in matched_papers if p.get('source', '').startswith(conference)])} 篇匹配论文")
    
    return matched_papers


def save_to_txt(papers, output_file, keywords):
    """
    将匹配的论文信息保存到txt文件
    
    Args:
        papers: 论文列表
        output_file: 输出文件路径
        keywords: 搜索的关键词（字符串或列表）
    """
    # 将keywords统一转换为列表用于显示
    if isinstance(keywords, str):
        keywords_display = keywords
        keywords_list = [keywords]
    else:
        keywords_display = ", ".join([f"'{kw}'" for kw in keywords])
        keywords_list = keywords
    
    # 确保输出目录存在
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        if len(keywords_list) == 1:
            f.write(f"论文标题包含关键词 {keywords_display} 的论文列表\n")
        else:
            f.write(f"论文标题包含关键词（任意一个）{keywords_display} 的论文列表\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"共找到 {len(papers)} 篇论文\n\n")
        f.write("=" * 100 + "\n\n")
        
        for idx, paper in enumerate(papers, 1):
            f.write(f"【论文 {idx}】\n")
            f.write(f"来源: {paper.get('source', 'Unknown')}\n")
            matched_kw = paper.get('matched_keywords', [])
            if matched_kw:
                if len(matched_kw) == 1:
                    f.write(f"命中关键词: {matched_kw[0]}\n")
                else:
                    f.write(f"命中关键词: {', '.join(matched_kw)}\n")
            else:
                f.write(f"命中关键词: N/A\n")
            f.write(f"标题: {paper.get('title', 'N/A')}\n")
            f.write(f"标题: {paper.get('title_ch', 'N/A')}\n")
            f.write(f"类别: {paper.get('category', 'N/A')}\n")
            f.write(f"作者: {paper.get('authors', 'N/A')}\n")
            f.write(f"机构: {paper.get('affiliations', 'N/A')}\n")
            f.write(f"类型: {paper.get('presentation_type', 'N/A')}\n")
            f.write(f"链接: {paper.get('url', 'N/A')}\n")
            f.write("-" * 100 + "\n\n")
        
        f.write("=" * 100 + "\n")
        f.write("报告生成完成\n")
        f.write("=" * 100 + "\n")
    
    print(f"\n结果已保存到: {output_file}")


def main():
    """主函数"""
    # 配置参数
    keywords = ["prediction"]  # 要搜索的关键词列表，可以包含多个关键词（OR关系）

    # keywords = ["prediction","evaluation","rank"]  # 要搜索的关键词列表，可以包含多个关键词（OR关系）
    # 示例：keywords = ["prediction", "forecast", "prediction"]  # 只要标题包含任意一个关键词就匹配
    case_sensitive = False  # 是否区分大小写
    output_file = "WANTED_PAPERS/papers_with_keywords.txt"  # 输出文件名
    
    # 将keywords统一转换为列表用于显示
    if isinstance(keywords, str):
        keywords_display = f"'{keywords}'"
        keywords_list = [keywords]
    else:
        keywords_display = ", ".join([f"'{kw}'" for kw in keywords])
        keywords_list = keywords
    
    print("=" * 100)
    if len(keywords_list) == 1:
        print(f"开始提取标题包含关键词 {keywords_display} 的论文...")
    else:
        print(f"开始提取标题包含关键词（任意一个）{keywords_display} 的论文...")
    print("=" * 100 + "\n")
    
    # 提取论文
    matched_papers = extract_papers_by_keyword(keywords=keywords, case_sensitive=case_sensitive)
    
    # 保存结果
    if matched_papers:
        save_to_txt(matched_papers, output_file, keywords)
        print(f"\n✅ 提取完成！共找到 {len(matched_papers)} 篇论文")
    else:
        print(f"\n⚠️  未找到包含关键词 {keywords_display} 的论文")


if __name__ == "__main__":
    main()
