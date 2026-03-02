from bs4 import BeautifulSoup
import re
import time
import requests
import json
from urllib.parse import quote
from xml.etree import ElementTree as ET
from src.llm.llm_client import get_llm_client, translate_to_chinese


def extract_paper_titles_with_details(input_file_path, output_file_path, output_json_path, fetch_abstracts=False, delay=2):
    """
    提取论文标题及其详细信息（标题、作者、类别等）
    
    Args:
        input_file_path: HTML输入文件路径
        output_file_path: 文本输出文件路径
        output_json_path: JSON输出文件路径
        fetch_abstracts: 是否从arxiv获取摘要并翻译，默认为False
        delay: 获取摘要时的请求延迟（秒），默认为2秒
    """
    # 清空输出文件（如果存在）
    with open(output_file_path, 'w', encoding='utf-8') as f:
        pass  # 清空文件
    with open(output_json_path, 'w', encoding='utf-8') as f:
        pass  # 清空文件
    
    # 方法1: 直接处理HTML字符串
    with open(input_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    papers = []
    
    index = 0
    tr_len = len(soup.find_all('tr'))
    print(f"tr_len: {tr_len}")
    
    if fetch_abstracts:
        print(f"\n{'='*100}")
        print(f"已启用摘要获取功能，将逐篇获取摘要并翻译")
        print(f"{'='*100}\n")

    # 查找所有表格行
    for tr in soup.find_all('tr')[:]:
        try:
            # 查找该行中的所有<td>元素
            td_elements = tr.find_all('td')
            
            if len(td_elements) >= 6:  # 确保有足够的数据列
                # 提取论文标题（第3列）
                title_td = td_elements[2]
                title_link = title_td.find('a', href=True)
                
                # if title_link and 'openreview.net/forum' in title_link['href']:
                if title_link :
                    title = title_link.get_text(strip=True)
                    
                    # 过滤评分数字
                    if title and not re.match(r'^\d+$', title):
                        index += 1

                        presentation_type = td_elements[7].get_text(strip=True) if len(td_elements) > 7 else ''
                        if 'Reject'in presentation_type or 'Withdraw'in presentation_type  or 'Short' in presentation_type or 'Demo' in presentation_type:
                            continue
                        print(f"index: {index} , td_elements: {td_elements[7].get_text(strip=True)}")

                        # if index < 3585:
                        #     paper_info = {
                        #     'title': title,
                        #     'url': title_link['href'],
                        #     'category': td_elements[3].get_text(strip=True) if len(td_elements) > 3 else '',
                        #     'authors': td_elements[4].get_text(strip=True) if len(td_elements) > 4 else '',
                        #     'affiliations': td_elements[5].get_text(strip=True) if len(td_elements) > 5 else '',
                        #     'presentation_type': td_elements[7].get_text(strip=True) if len(td_elements) > 7 else ''
                        #     }
                        #     papers.append(paper_info)
                        #     print(f"跳过第 {index} 篇论文")
                        #     continue

                        title_ch = translate_to_chinese(title)
                        # 提取其他信息
                        paper_info = {
                            'title': title,
                            'title_ch': title_ch,
                            'url': title_link['href'],
                            'category': td_elements[3].get_text(strip=True) if len(td_elements) > 3 else '',
                            'authors': td_elements[4].get_text(strip=True) if len(td_elements) > 4 else '',
                            'affiliations': td_elements[5].get_text(strip=True) if len(td_elements) > 5 else '',
                            'presentation_type': td_elements[7].get_text(strip=True) if len(td_elements) > 7 else ''
                        }
  
                        # 如果启用，立即获取摘要并翻译
                        if fetch_abstracts:
                            print(f"\n[{index}] 开始获取摘要: {title[:60]}...")
                            paper_info = _fetch_single_paper_abstract(paper_info, delay)
                            # time.sleep(delay)  # 延迟，避免请求过快

                        papers.append(paper_info)

                        # 将详细信息写入文件（包含摘要信息）
                        _write_paper_to_files(paper_info, len(papers), output_file_path, output_json_path)
                        
                        print(f"📝 已保存第 {len(papers)} 篇论文到 {output_file_path}, {output_json_path}")
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print(f"\n{'='*100}")
    print(f"✅ 处理完成！共提取 {len(papers)} 篇论文")
    if fetch_abstracts:
        success_count = sum(1 for p in papers if p.get('abstract'))
        print(f"   其中 {success_count} 篇成功获取摘要并翻译")
    print(f"{'='*100}\n")
    
    return papers


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


def _write_paper_to_files(paper_info, paper_num, output_file_path, output_json_path):
    """
    将单篇论文信息写入文件（包含摘要信息）
    
    Args:
        paper_info: 论文信息字典
        paper_num: 论文编号
        output_file_path: 文本输出文件路径
        output_json_path: JSON输出文件路径
    """
    # 写入文本文件
    with open(output_file_path, "a", encoding="utf-8") as f:
        f.write(f"No.{paper_num}. {paper_info.get('title', 'N/A')}\n")
        f.write(f"   标题: {paper_info.get('title_ch', 'N/A')}\n")
        f.write(f"   链接: {paper_info.get('url', 'N/A')}\n")
        f.write(f"   类别: {paper_info.get('category', 'N/A')}\n")
        f.write(f"   作者: {paper_info.get('authors', 'N/A')}\n")
        f.write(f"   机构: {paper_info.get('affiliations', 'N/A')}\n")
        f.write(f"   类型: {paper_info.get('presentation_type', 'N/A')}\n")
        
        # 添加arxiv信息（如果有）
        arxiv_id = paper_info.get('arxiv_id', '')
        arxiv_link = paper_info.get('arxiv_link', '')
        if arxiv_id:
            f.write(f"   arXiv ID: {arxiv_id}\n")
        if arxiv_link:
            f.write(f"   arXiv链接: {arxiv_link}\n")
        
        # 添加摘要信息（如果有）
        abstract = paper_info.get('abstract', '')
        abstract_ch = paper_info.get('abstract_ch', '')
        if abstract:
            f.write(f"   英摘: {abstract}\n")
        if abstract_ch:
            f.write(f"   中摘: {abstract_ch}\n")
        
        f.write("\n")  # 空行分隔
    
    # 写入JSON文件
    with open(output_json_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(paper_info, ensure_ascii=False) + "\n")


def search_arxiv_by_title(title, max_results=5, max_retries=3, timeout=10):
    """
    根据论文标题在arxiv中搜索，返回最匹配的arxiv ID
    
    Args:
        title: 论文标题
        max_results: 返回的最大结果数
        max_retries: 最大重试次数
        timeout: 请求超时时间（秒）
        
    Returns:
        str: arxiv ID，如果未找到返回None
    """
    if not title or title == 'N/A':
        return None
    
    # 清理标题，移除特殊字符，用于搜索
    # 移除常见的标点符号，保留字母、数字和空格
    clean_title = re.sub(r'[^\w\s]', ' ', title)
    # 移除多余空格
    clean_title = ' '.join(clean_title.split())
    # 限制长度，arxiv搜索对查询长度有限制
    if len(clean_title) > 200:
        clean_title = clean_title[:200]
    
    # 构建搜索查询（使用标题搜索）
    # 使用ti:前缀表示标题搜索，使用引号确保精确匹配
    search_query = f'ti:"{clean_title}"'
    # URL编码
    encoded_query = quote(search_query)
    
    # arxiv搜索API URL
    api_url = f"http://export.arxiv.org/api/query?search_query={encoded_query}&start=0&max_results={max_results}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            
            # 定义命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # 查找所有entry元素
            entries = root.findall('atom:entry', ns)
            
            if not entries:
                return None
            
            # 尝试匹配最相似的标题
            best_match = None
            best_score = 0
            
            title_lower = title.lower()
            
            for entry in entries:
                title_elem = entry.find('atom:title', ns)
                if title_elem is None:
                    continue
                
                arxiv_title = title_elem.text.strip()
                arxiv_title_lower = arxiv_title.lower()
                
                # 计算相似度（简单的字符串匹配）
                # 方法1: 完全匹配
                if title_lower == arxiv_title_lower:
                    # 提取arxiv ID
                    id_elem = entry.find('atom:id', ns)
                    if id_elem is not None:
                        arxiv_id = id_elem.text.split('/')[-1]
                        return arxiv_id
                
                # 方法2: 计算共同单词的比例
                title_words = set(re.findall(r'\w+', title_lower))
                arxiv_words = set(re.findall(r'\w+', arxiv_title_lower))
                
                if title_words:
                    common_words = title_words.intersection(arxiv_words)
                    score = len(common_words) / len(title_words)
                    
                    if score > best_score and score > 0.5:  # 至少50%的单词匹配
                        best_score = score
                        id_elem = entry.find('atom:id', ns)
                        if id_elem is not None:
                            arxiv_id = id_elem.text.split('/')[-1]
                            best_match = arxiv_id
            
            return best_match
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"警告: arxiv搜索失败 (标题: {title[:50]}...): {e}")
            return None
        except ET.ParseError as e:
            print(f"警告: 解析arxiv搜索响应失败 (标题: {title[:50]}...): {e}")
            return None
        except Exception as e:
            print(f"警告: 处理arxiv搜索响应出错 (标题: {title[:50]}...): {e}")
            return None
    
    return None


def get_paper_details_from_arxiv(arxiv_id, max_retries=3, timeout=10):
    """
    从arxiv API获取论文详情
    
    Args:
        arxiv_id: arxiv ID（格式：2301.12345 或 cs.CV/2301.12345）
        max_retries: 最大重试次数
        timeout: 请求超时时间（秒）
        
    Returns:
        dict: 包含论文详情的字典，包括abstract, title, authors等，如果获取失败返回None
    """
    if not arxiv_id:
        return None
    
    # 标准化arxiv ID格式（移除版本号）
    arxiv_id_clean = re.sub(r'v[0-9]+$', '', arxiv_id)
    
    # arxiv API URL
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id_clean}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # 解析XML响应
            root = ET.fromstring(response.content)
            
            # 定义命名空间
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            # 查找entry元素
            entry = root.find('atom:entry', ns)
            if entry is None:
                return None
            
            # 提取信息
            title_elem = entry.find('atom:title', ns)
            title = title_elem.text.strip() if title_elem is not None else ""
            
            summary_elem = entry.find('atom:summary', ns)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""
            
            # 提取作者
            authors = []
            for author_elem in entry.findall('atom:author', ns):
                name_elem = author_elem.find('atom:name', ns)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # 提取发表日期
            published_elem = entry.find('atom:published', ns)
            published = published_elem.text.strip() if published_elem is not None else ""
            
            # 提取arxiv链接
            arxiv_link = f"https://arxiv.org/abs/{arxiv_id_clean}"
            
            return {
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'published': published,
                'arxiv_link': arxiv_link,
                'arxiv_id': arxiv_id_clean
            }
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"警告: 从arxiv获取论文详情失败 (ID: {arxiv_id}): {e}")
            return None
        except ET.ParseError as e:
            print(f"警告: 解析arxiv API响应失败 (ID: {arxiv_id}): {e}")
            return None
        except Exception as e:
            print(f"警告: 处理arxiv API响应出错 (ID: {arxiv_id}): {e}")
            return None
    
    return None


def fetch_abstracts_and_translate(papers, delay=2):
    """
    根据论文标题在arxiv中搜索，获取摘要并翻译
    
    Args:
        papers: 论文列表（每个元素是包含'title'字段的字典）
        delay: 每次请求之间的延迟（秒），避免请求过快（arxiv API有速率限制）
        
    Returns:
        list: 包含摘要和中文摘要的论文列表
    """
    total = len(papers)
    print(f"\n开始根据标题从arxiv搜索并获取 {total} 篇论文的摘要...")
    print("=" * 100 + "\n")
    
    success_count = 0
    fail_count = 0
    
    for idx, paper in enumerate(papers, 1):
        title = paper.get('title', 'N/A')
        print(f"[{idx}/{total}] 正在处理: {title[:60]}...")
        
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
                    paper['abstract'] = abstract
                    paper['arxiv_id'] = paper_details.get('arxiv_id', '')
                    paper['arxiv_link'] = paper_details.get('arxiv_link', '')
                    print(f"  ✓ 已从arxiv获取摘要 ({len(abstract)} 字符)")
                    
                    # 翻译摘要
                    try:
                        print(f"  → 正在翻译摘要...")
                        abstract_ch = translate_to_chinese(abstract)
                        paper['abstract_ch'] = abstract_ch
                        print(f"  ✓ 翻译完成")
                        success_count += 1
                    except Exception as e:
                        print(f"  ✗ 翻译失败: {e}")
                        paper['abstract_ch'] = ""
                        fail_count += 1
                else:
                    print(f"  ✗ arxiv未返回摘要")
                    paper['abstract'] = ""
                    paper['abstract_ch'] = ""
                    fail_count += 1
            else:
                print(f"  ✗ 无法从arxiv获取论文详情")
                paper['abstract'] = ""
                paper['abstract_ch'] = ""
                paper['arxiv_id'] = ""
                paper['arxiv_link'] = ""
                fail_count += 1
        else:
            print(f"  ✗ 未在arxiv中找到匹配的论文")
            paper['abstract'] = ""
            paper['abstract_ch'] = ""
            paper['arxiv_id'] = ""
            paper['arxiv_link'] = ""
            fail_count += 1
        
        # 延迟，避免请求过快（arxiv API有速率限制，建议至少2秒）
        if idx < total:
            time.sleep(delay)
    
    print("\n" + "=" * 100)
    print(f"摘要获取和翻译完成！成功: {success_count}, 失败: {fail_count}\n")
    
    return papers


# 使用示例
if __name__ == "__main__":

    # 使用 (会议, 年份) 元组列表，避免 dict 中同会议多届被重复 key 覆盖
    paper_list = [
        # ("NeurIPS", "2025"),
        # ("NeurIPS", "2024"),
        # ("NeurIPS", "2023"),
        
        # ("ICLR", "2025"),
        # ("ICLR", "2024"),
        # ("ICLR", "2023"),
        
        # ("ICML", "2025"),
        # ("ICML", "2024"),
        # ("ICML", "2023"),
        
        # ("AAAI", "2025"),
        # ("AAAI", "2024"),
        # ("AAAI", "2023"),
        
        # ("IJCAI", "2024"),
        # ("IJCAI", "2023"),
        
        ("ACL", "2024"),
        ("ACL", "2023"),

        ("EMNLP", "2024"),
        ("EMNLP", "2023"),
    ]

    for conference, year in paper_list:
        print(f"处理: {conference} {year}")
        print(f"{'='*100}")
        input_file_path = f"{conference}/{conference}_{year}.html"
        output_file_path = f"{conference}/{conference}_{year}_accepted.txt"
        output_json_path = f"{conference}/{conference}_{year}_accepted.json"
        
        # 配置参数
        fetch_abstracts = False  # 设置为True以获取摘要并翻译（需要较长时间）
        request_delay = 2  # 每次请求之间的延迟（秒），避免请求过快
        
        # 提取论文信息
        detailed_papers = extract_paper_titles_with_details(
            input_file_path, 
            output_file_path, 
            output_json_path,
            fetch_abstracts=fetch_abstracts,
            delay=request_delay
        )
        
        print(f"\n✅ 处理完成！共提取 {len(detailed_papers)} 篇论文")



