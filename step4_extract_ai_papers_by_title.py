#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从所有AI会议的accepted.json中提取指定关键词的论文
"""

import json
import time
from pathlib import Path
from step2_paper_list import search_arxiv_by_title, get_paper_details_from_arxiv
from src.llm.llm_client import translate_to_chinese


def _fetch_single_paper_abstract(paper_info, delay=2):
    """
    为单篇论文获取摘要并翻译
    
    Args:
        paper_info: 论文信息字典（必须包含'title'字段）
        delay: 请求延迟（秒）
        
    Returns:
        dict: 更新后的论文信息字典（包含摘要信息）
    """
    title = paper_info.get('title', 'N/A')
    
    # 根据标题在arxiv中搜索
    print(f"  → 在arxiv中搜索论文...")
    arxiv_id = search_arxiv_by_title(title, max_results=5, max_retries=3, timeout=10)
    
    # 如果找到了arxiv ID，获取论文详情
    if arxiv_id:
        print(f"  ✓ 找到arxiv ID: {arxiv_id}")
        paper_details = get_paper_details_from_arxiv(arxiv_id, max_retries=3, timeout=10)
        
        if paper_details:
            abstract = paper_details.get('abstract', '')
            if abstract:
                paper_info['abstract'] = abstract
                paper_info['arxiv_id'] = paper_details.get('arxiv_id', '')
                paper_info['arxiv_link'] = paper_details.get('arxiv_link', '')
                print(f"  ✓ 已从arxiv获取摘要 ({len(abstract)} 字符)")
                
                # 翻译摘要
                try:
                    print(f"  → 正在翻译摘要...")
                    abstract_ch = translate_to_chinese(abstract)
                    paper_info['abstract_ch'] = abstract_ch
                    print(f"  ✓ 翻译完成")
                except Exception as e:
                    print(f"  ✗ 翻译失败: {e}")
                    paper_info['abstract_ch'] = ""
            else:
                print(f"  ✗ arxiv未返回摘要")
                paper_info['abstract'] = ""
                paper_info['abstract_ch'] = ""
        else:
            print(f"  ✗ 无法从arxiv获取论文详情")
            paper_info['abstract'] = ""
            paper_info['abstract_ch'] = ""
            paper_info['arxiv_id'] = ""
            paper_info['arxiv_link'] = ""
    else:
        print(f"  ✗ 未在arxiv中找到匹配的论文")
        paper_info['abstract'] = ""
        paper_info['abstract_ch'] = ""
        paper_info['arxiv_id'] = ""
        paper_info['arxiv_link'] = ""
    
    return paper_info


def _write_single_paper_to_file(paper, paper_num, output_file, keywords, is_first_paper=False):
    """
    将单篇论文信息写入文件（追加模式）
    
    Args:
        paper: 论文信息字典
        paper_num: 论文编号
        output_file: 输出文件路径
        keywords: 搜索的关键词（用于写入文件头）
        is_first_paper: 是否是第一篇论文（用于写入文件头）
    """
    # 将keywords统一转换为列表用于显示
    if isinstance(keywords, str):
        keywords_display = keywords
        keywords_list = [keywords]
    else:
        keywords_display = ", ".join([f"'{kw}'" for kw in keywords])
        keywords_list = keywords
    
    mode = 'w' if is_first_paper else 'a'
    
    with open(output_file, mode, encoding='utf-8') as f:
        # 如果是第一篇，写入文件头
        if is_first_paper:
            f.write("=" * 100 + "\n")
            if len(keywords_list) == 1:
                f.write(f"论文标题包含关键词 {keywords_display} 的论文列表\n")
            else:
                f.write(f"论文标题包含关键词（任意一个）{keywords_display} 的论文列表\n")
            f.write("=" * 100 + "\n\n")
        
        # 写入论文信息
        f.write(f"[No.{paper_num}] {paper.get('title', 'N/A')}\n")
        f.write(f"来源: {paper.get('source', 'Unknown')}\n")
        matched_kw = paper.get('matched_keywords', [])
        if matched_kw:
            if len(matched_kw) == 1:
                f.write(f"命中: {matched_kw[0]}\n")
            else:
                f.write(f"命中: {', '.join(matched_kw)}\n")
        else:
            f.write(f"命中: N/A\n")
        f.write(f"标题: {paper.get('title_ch', 'N/A')}\n")
        f.write(f"类别: {paper.get('category', 'N/A')}\n")
        f.write(f"作者: {paper.get('authors', 'N/A')}\n")
        f.write(f"机构: {paper.get('affiliations', 'N/A')}\n")
        f.write(f"类型: {paper.get('presentation_type', 'N/A')}\n")
        f.write(f"链接: {paper.get('url', 'N/A')}\n")
        
        # 添加arxiv信息（如果有）
        arxiv_id = paper.get('arxiv_id', '')
        arxiv_link = paper.get('arxiv_link', '')
        # if arxiv_id:
        #     f.write(f"arXiv ID: {arxiv_id}\n")
        if arxiv_link:
            f.write(f"arXi: {arxiv_link}\n")
        
        # 添加摘要信息（如果有）
        abstract = paper.get('abstract', '')
        abstract_ch = paper.get('abstract_ch', '')
        if abstract:
            f.write(f"英摘: {abstract}\n")
        if abstract_ch:
            f.write(f"中摘: {abstract_ch}\n")
        
        f.write("-" * 100 + "\n")


def extract_papers_by_keyword(keywords, case_sensitive=False, fetch_abstracts=False, delay=2, output_file=None):
    """
    从所有AI会议的JSON文件中提取标题包含指定关键词的论文
    
    Args:
        keywords: 要搜索的关键词，可以是字符串或列表。如果是列表，只要标题包含任意一个关键词就匹配（OR关系）
        case_sensitive: 是否区分大小写，默认为False（不区分大小写）
        fetch_abstracts: 是否获取摘要并翻译，默认为False
        delay: 获取摘要时的请求延迟（秒），默认为2秒
        output_file: 输出文件路径，如果提供则逐条写入
        
    Returns:
        list: 包含匹配论文信息的列表，每个元素是一个字典
    """
    # 将keywords统一转换为列表
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # 将keywords统一转换为列表
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # 配置参数
        # 使用 (会议, 年份) 元组列表，避免 dict 中同会议多届被重复 key 覆盖
    paper_list = [
        ("NeurIPS", "2025"),
        ("NeurIPS", "2024"),
        ("NeurIPS", "2023"),
        
        ("ICLR", "2025"),
        ("ICLR", "2024"),
        ("ICLR", "2023"),
        
        ("ICML", "2025"),
        ("ICML", "2024"),
        ("ICML", "2023"),

        ("ACL", "2024"),
        ("ACL", "2023"),

        ("EMNLP", "2024"),
        ("EMNLP", "2023"),
        
        ("AAAI", "2025"),
        ("AAAI", "2024"),
        ("AAAI", "2023"),
        
        ("IJCAI", "2024"),
        ("IJCAI", "2023"),
        

    ]

    
    matched_papers = []
    paper_count = 0
    
    # 如果提供输出文件，清空文件
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            pass  # 清空文件
    
    if fetch_abstracts:
        print(f"\n{'='*100}")
        print(f"已启用摘要获取功能，将逐篇获取摘要并翻译")
        print(f"{'='*100}\n")
    
    for conference, year in paper_list:

        json_file = Path(f"{conference}/{conference}_{year}_accepted.json")
    
        if not json_file.exists():
            print(f"警告: 文件不存在，跳过: {json_file}")
            continue
        
        print(f"正在处理: {conference} {year}...")
        conference_count = 0
        
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
                            if keyword.lower() in title_lower :
                                # rank有点特殊，需要额外处理下
                                if "-rank" not in title_lower:
                                    matched_keywords.append(keyword)
                    
                    if matched_keywords:
                        # 添加来源字段和命中的关键词
                        paper['source'] = f"{conference} {year}"
                        paper['matched_keywords'] = matched_keywords
                        paper_count += 1
                        conference_count += 1
                        
                        # 如果启用，立即获取摘要并翻译
                        if fetch_abstracts:
                            print(f"\n[{paper_count}] 开始获取摘要: {title[:60]}...")
                            paper = _fetch_single_paper_abstract(paper, delay)
                            time.sleep(delay)  # 延迟，避免请求过快
                        
                        matched_papers.append(paper)
                        
                        # 如果提供输出文件，立即写入
                        if output_file:
                            _write_single_paper_to_file(paper, paper_count, output_file, keywords, is_first_paper=(paper_count == 1))
                            print(f"  📝 已保存第 {paper_count} 篇论文到 {output_file}")
                
                except json.JSONDecodeError as e:
                    print(f"警告: {conference} 第 {line_num} 行JSON解析失败: {e}")
                    continue
                except Exception as e:
                    print(f"警告: {conference} 第 {line_num} 行处理出错: {e}")
                    continue
        
        print(f"  ✓ {conference} 处理完成，找到 {conference_count} 篇匹配论文")
    
    # 如果提供输出文件，写入文件尾
    if output_file and matched_papers:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("=" * 100 + "\n")
            f.write(f"共找到 {len(matched_papers)} 篇论文\n")
            if fetch_abstracts:
                success_count = sum(1 for p in matched_papers if p.get('abstract'))
                f.write(f"其中 {success_count} 篇成功获取摘要并翻译\n")
            f.write("报告生成完成\n")
            f.write("=" * 100 + "\n")
    
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
            f.write(f"[No.{idx}] {paper.get('title', 'N/A')}\n")
            f.write(f"来源: {paper.get('source', 'Unknown')}\n")
            matched_kw = paper.get('matched_keywords', [])
            if matched_kw:
                if len(matched_kw) == 1:
                    f.write(f"命中: {matched_kw[0]}\n")
                else:
                    f.write(f"命中: {', '.join(matched_kw)}\n")
            else:
                f.write(f"命中: N/A\n")
            # f.write(f"标题: {paper.get('title', 'N/A')}\n")
            f.write(f"标题: {paper.get('title_ch', 'N/A')}\n")
            f.write(f"类别: {paper.get('category', 'N/A')}\n")
            f.write(f"作者: {paper.get('authors', 'N/A')}\n")
            f.write(f"机构: {paper.get('affiliations', 'N/A')}\n")
            f.write(f"类型: {paper.get('presentation_type', 'N/A')}\n")
            f.write(f"链接: {paper.get('url', 'N/A')}\n")
            
            # 如果论文包含摘要信息，则输出（这些信息可能来自paper_list.py的处理）
            arxiv_id = paper.get('arxiv_id', '')
            arxiv_link = paper.get('arxiv_link', '')
            abstract = paper.get('abstract', '')
            abstract_ch = paper.get('abstract_ch', '')
            
            if arxiv_id:
                f.write(f"arXiv ID: {arxiv_id}\n")
            if arxiv_link:
                f.write(f"arXiv链接: {arxiv_link}\n")
            if abstract:
                f.write(f"\n英摘:\n{abstract}\n")
            if abstract_ch:
                f.write(f"\n中摘:\n{abstract_ch}\n")
            
            f.write("-" * 100 + "\n\n")
        
        f.write("=" * 100 + "\n")
        f.write("报告生成完成\n")
        f.write("=" * 100 + "\n")
    
    print(f"\n结果已保存到: {output_file}")


def main():
    """主函数"""
    # 配置参数
    keywords = ["vuln"]  # 要搜索的关键词列表，可以包含多个关键词（OR关系）

    # keywords = ["prediction","evaluation","rank"]  # 要搜索的关键词列表，可以包含多个关键词（OR关系）
    # 示例：keywords = ["prediction", "forecast", "prediction"]  # 只要标题包含任意一个关键词就匹配
    case_sensitive = False  # 是否区分大小写
    fetch_abstracts = True  # 是否获取摘要并翻译（设置为True以获取摘要，需要较长时间）
    request_delay = 2  # 每次请求之间的延迟（秒），避免请求过快
    output_file = f"WANTED_PAPERS/aipapers_with_keywords_{keywords[0]}.txt"  # 输出文件名
    
    
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
    
    # 提取论文（如果fetch_abstracts=True，会逐条获取摘要并写入文件）
    matched_papers = extract_papers_by_keyword(
        keywords=keywords, 
        case_sensitive=case_sensitive,
        fetch_abstracts=fetch_abstracts,
        delay=request_delay,
        output_file=output_file if fetch_abstracts else None  # 如果获取摘要，则逐条写入；否则最后一起写入
    )
    
    # 如果没有逐条写入（即fetch_abstracts=False），则最后一起保存
    if matched_papers and not fetch_abstracts:
        save_to_txt(matched_papers, output_file, keywords)
        print(f"\n✅ 提取完成！共找到 {len(matched_papers)} 篇论文")
    elif matched_papers:
        print(f"\n✅ 提取完成！共找到 {len(matched_papers)} 篇论文")
        success_count = sum(1 for p in matched_papers if p.get('abstract'))
        print(f"   其中 {success_count} 篇成功获取摘要并翻译")
    else:
        print(f"\n⚠️  未找到包含关键词 {keywords_display} 的论文")


if __name__ == "__main__":
    main()
