from bs4 import BeautifulSoup
import re
import requests
import json
from src.llm.llm_client import get_llm_client, translate_to_chinese


def extract_paper_titles_with_details(input_file_path, output_file_path,output_json_path):
    """
    提取论文标题及其详细信息（标题、作者、类别等）
    """
    # 方法1: 直接处理HTML字符串
    with open(input_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    papers = []
    
    index = 0
    # 查找所有表格行
    for tr in soup.find_all('tr')[:]:
        try:
            # 查找该行中的所有<td>元素
            td_elements = tr.find_all('td')
            
            if len(td_elements) >= 6:  # 确保有足够的数据列
                # 提取论文标题（第3列）
                title_td = td_elements[2]
                title_link = title_td.find('a', href=True)
                
                if title_link and 'openreview.net/forum' in title_link['href']:
                    title = title_link.get_text(strip=True)
                    
                    # 过滤评分数字
                    if title and not re.match(r'^\d+$', title):
                        index += 1
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
                        papers.append(paper_info)

                        # 将详细信息写入文件
                        with open(output_file_path, "a", encoding="utf-8") as f:
                            f.write(f"No.{len(papers)}. {paper_info['title']}\n")
                            f.write(f"   标题: {paper_info['title_ch']}\n")
                            f.write(f"   链接: {paper_info['url']}\n")
                            f.write(f"   类别: {paper_info['category']}\n")
                            f.write(f"   作者: {paper_info['authors']}\n")
                            f.write(f"   机构: {paper_info['affiliations']}\n")
                            f.write(f"   类型: {paper_info['presentation_type']}\n")
                            f.write("\n")  # 空行分隔
                        # print(f"\n📝 已保存 {len(papers)} 篇论文的详细信息到 {output_file_path}")

                        
                        # 将详细信息写入文件
                        with open(output_json_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(paper_info, ensure_ascii=False) + "\n")  # 空行分隔
                        print(f"\n📝 已保存 {len(papers)} 篇论文的详细信息到 {output_file_path}, {output_json_path}")
        except Exception as e:
            print(f"Error: {e}")
            continue
    return papers

# 使用示例
if __name__ == "__main__":
    conference = "ICML"
    year = "2025"
    input_file_path = f"{conference}/{conference}_{year}.html"
    output_file_path = f"{conference}/{conference}_{year}_accepted_titles.txt"
    output_json_path = f"{conference}/{conference}_{year}_accepted_titles.json"

    detailed_papers = extract_paper_titles_with_details(input_file_path, output_file_path,output_json_path)



