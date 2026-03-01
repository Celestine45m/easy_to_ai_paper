#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 papercopilot.com 爬取论文列表
根据会议名称和年份，进入paper_list详情页，点击"click to fetch all"展开所有论文，
提取HTML中<table id="paperlist">保存到对应会议目录下为HTML文件
"""

import time
import os
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


# 会议名称到URL路径的映射
CONFERENCE_URL_MAP = {
    "NeurIPS": "neurips-paper-list",
    "ICLR": "iclr-paper-list",
    "ICML": "icml-paper-list",
    "AAAI": "aaai-paper-list",
    "IJCAI": "ijcai-paper-list",
    "ACL": "acl-paper-list",
    "EMNLP": "emnlp-paper-list",

    # "NAACL": "naacl-paper-list",
    # "COLING": "coling-paper-list",
    # "CVPR": "cvpr-paper-list",
    # "ICCV": "iccv-paper-list",
    # "ECCV": "eccv-paper-list",
    # "WACV": "wacv-paper-list",
    # "KDD": "kdd-paper-list",
    # "WWW": "www-paper-list",
    # "SIGIR": "sigir-paper-list",
    # "ICRA": "icra-paper-list",
    # "IROS": "iros-paper-list",
    # "RSS": "rss-paper-list",
    # "CoRL": "corl-paper-list",
    # "AISTATS": "aistats-paper-list",
    # "ACML": "acml-paper-list",
    # "UAI": "uai-paper-list",
    # "COLT": "colt-paper-list",
    # "ALT": "alt-paper-list",
    # "ARR": "arr-paper-list",
    # "COLM": "colm-accepted-paper-list",
    # "SIGGRAPH": "siggraph-paper-list",
    # "SIGGRAPH Asia": "siggraph-asia-paper-list",
    # "ACM-MM": "acmmm-paper-list",
}


def get_paper_list_url(conference, year):
    """
    构建paper_list页面的URL
    
    Args:
        conference: 会议名称（如 "NeurIPS", "ICLR"）
        year: 年份（如 "2025"）
        
    Returns:
        str: 完整的URL
    """
    base_url = "https://papercopilot.com"
    
    # 获取会议对应的URL路径
    conf_path = CONFERENCE_URL_MAP.get(conference)
    if not conf_path:
        # 如果没有映射，尝试使用小写加连字符的格式
        conf_path = conference.lower().replace(" ", "-") + "-paper-list"
    
    # 构建完整URL
    url = f"{base_url}/paper-list/{conf_path}/{conference.lower()}-{year}-paper-list/"
    
    return url


def setup_driver(headless=False):
    """
    设置并返回Selenium WebDriver
    
    Args:
        headless: 是否使用无头模式
        
    Returns:
        webdriver: Chrome WebDriver实例
    """
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        # 尝试使用webdriver-manager（如果已安装）
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            print("  ✓ 使用webdriver-manager自动管理ChromeDriver")
        except ImportError:
            # 如果没有安装webdriver-manager，使用系统PATH中的ChromeDriver
            driver = webdriver.Chrome(options=options)
            print("  ✓ 使用系统PATH中的ChromeDriver")
        return driver
    except Exception as e:
        print(f"❌ 无法启动Chrome浏览器: {e}")
        print("\n解决方案:")
        print("1. 确保已安装Chrome浏览器")
        print("2. 安装webdriver-manager自动管理驱动:")
        print("   pip install webdriver-manager")
        print("3. 或手动下载ChromeDriver并添加到PATH:")
        print("   https://chromedriver.chromium.org/downloads")
        raise


def click_fetch_all_button(driver, timeout=120):
    """
    查找并点击 "Click to Fetch All" 按钮。
    页面按钮为: <a id="btn_fetchall" class="wp-block-button__link wp-element-button">Click to Fetch All</a>
    
    Args:
        driver: WebDriver实例
        timeout: 超时时间（秒）
        
    Returns:
        bool: 是否成功点击
    """
    # 按优先级：先按 id（最稳定），再按文本/class
    selectors = [
        ("id", By.ID, "btn_fetchall"),
        ("css", By.CSS_SELECTOR, "#btn_fetchall"),
        ("xpath", By.XPATH, "//*[@id='btn_fetchall']"),
        ("xpath", By.XPATH, "//a[contains(text(), 'Click to Fetch All')]"),
        ("xpath", By.XPATH, "//a[contains(text(), 'Click to fetch all')]"),
        ("xpath", By.XPATH, "//a[contains(@class, 'wp-block-button__link') and contains(text(), 'Fetch All')]"),
        ("xpath", By.XPATH, "//button[contains(text(), 'Click to Fetch All')]"),
        ("xpath", By.XPATH, "//*[contains(text(), 'click to fetch all')]"),
    ]
    wait = WebDriverWait(driver, 5)
    for name, by, value in selectors:
        try:
            button = wait.until(EC.element_to_be_clickable((by, value)))
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            button.click()
            print(f"  ✓ 成功点击 'Click to Fetch All' 按钮 (通过 {name}: {value})")
            return True
        except TimeoutException:
            continue
        except Exception as e:
            continue
    print("  ⚠ 未找到 'Click to Fetch All' 按钮，可能页面已自动加载所有内容")
    return False


def extract_paperlist_table(driver):
    """
    从页面中提取<table id="paperlist">的内容
    
    Args:
        driver: WebDriver实例
        
    Returns:
        str: HTML字符串，如果未找到则返回None
    """
    try:
        # 等待表格加载
        wait = WebDriverWait(driver, 20)
        table = wait.until(
            EC.presence_of_element_located((By.ID, "paperlist"))
        )
        
        # 获取表格的HTML
        table_html = table.get_attribute('outerHTML')
        
        if table_html:
            print(f"  ✓ 成功提取表格，大小: {len(table_html)} 字符")
            return table_html
        else:
            print("  ⚠ 表格元素存在但内容为空")
            return None
            
    except TimeoutException:
        print("  ❌ 超时：未找到id='paperlist'的表格")
        return None
    except Exception as e:
        print(f"  ❌ 提取表格时出错: {e}")
        return None


def save_table_html(table_html, conference, year, output_dir=None):
    """
    保存表格HTML到文件
    
    Args:
        table_html: 表格HTML字符串
        conference: 会议名称
        year: 年份
        output_dir: 输出目录，如果为None则使用会议名称作为目录
        
    Returns:
        str: 保存的文件路径
    """
    if output_dir is None:
        output_dir = Path(conference)
    else:
        output_dir = Path(output_dir)
        # 如果指定了输出目录，仍然在目录下创建会议子目录
        output_dir = output_dir / conference
    
    # 确保目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 构建文件名
    filename = f"{conference}_{year}.html"
    filepath = output_dir / filename
    
    # 保存HTML（添加基本的HTML结构）
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{conference} {year} Paper List</title>
</head>
<body>
{table_html}
</body>
</html>"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✓ 已保存到: {filepath}")
    return str(filepath)


def crawl_paper_list(conference, year, headless=False, wait_time=120, output_dir=None, overwrite=False):
    """
    爬取指定会议和年份的论文列表
    
    Args:
        conference: 会议名称（如 "NeurIPS", "ICLR"）
        year: 年份（如 "2025"）
        headless: 是否使用无头模式
        wait_time: 页面加载等待时间（秒）
        output_dir: 输出目录，如果为None则使用会议名称作为目录
        overwrite: 如果文件已存在，是否覆盖
        
    Returns:
        str: 保存的文件路径，如果失败返回None
    """
    print(f"\n{'='*100}")
    print(f"开始爬取: {conference} {year}")
    print(f"{'='*100}\n")
    
    # 检查文件是否已存在
    if output_dir is None:
        check_dir = Path(conference)
    else:
        check_dir = Path(output_dir) / conference
    check_file = check_dir / f"{conference}_{year}.html"
    
    if check_file.exists() and not overwrite:
        print(f"⚠️  文件已存在: {check_file}")
        print("  使用 --overwrite 参数可以覆盖现有文件")
        return str(check_file)
    
    # 构建URL
    url = get_paper_list_url(conference, year)
    print(f"目标URL: {url}")
    
    driver = None
    try:
        # 设置WebDriver
        print("正在启动浏览器...")
        driver = setup_driver(headless=headless)
        
        # 访问页面
        print(f"正在访问页面...")
        driver.get(url)
        
        # 等待页面加载
        print(f"等待页面加载（{wait_time}秒）...")
        time.sleep(wait_time)
        
        # 尝试点击"click to fetch all"按钮
        print("正在查找并点击'click to fetch all'按钮...")
        click_fetch_all_button(driver, timeout=120)
        
        # 额外等待，确保内容加载完成
        print("等待内容加载完成...")
        time.sleep(60)
        
        # 提取表格
        print("正在提取表格内容...")
        table_html = extract_paperlist_table(driver)
        
        if table_html:
            # 保存文件
            filepath = save_table_html(table_html, conference, year, output_dir)
            print(f"\n✅ 爬取成功！文件已保存")
            return filepath
        else:
            print(f"\n❌ 爬取失败：未能提取表格内容")
            return None
            
    except Exception as e:
        print(f"\n❌ 爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        # 关闭浏览器
        if driver:
            print("正在关闭浏览器...")
            driver.quit()


def crawl_multiple_conferences(conferences_years, headless=False, wait_time=120):
    """
    批量爬取多个会议和年份的论文列表
    
    Args:
        conferences_years: 列表，每个元素是(conference, year)元组
        headless: 是否使用无头模式
        wait_time: 页面加载等待时间（秒）
        
    Returns:
        dict: {会议_年份: 文件路径}的字典
    """
    results = {}
    
    for conference, year in conferences_years:
        key = f"{conference}_{year}"
        filepath = crawl_paper_list(conference, year, headless, wait_time)
        results[key] = filepath
        
        # 在两次爬取之间等待，避免请求过快
        if len(conferences_years) > 1:
            print(f"\n等待5秒后继续下一个...")
            time.sleep(5)
    
    return results


def main():
    """主函数 - 支持命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="从 papercopilot.com 爬取论文列表",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 爬取单个会议
  python crawl_papercopilot.py --conference NeurIPS --year 2024 --overwrite
  
  # 批量爬取多个会议
  python crawl_papercopilot.py --conference NeurIPS ICLR ICML --year 2025
  
  # 使用无头模式（后台运行）
  python crawl_papercopilot.py --conference NeurIPS --year 2025 --headless
  
  # 指定输出目录
  python crawl_papercopilot.py --conference NeurIPS --year 2024 --output-dir ./NeurIPS
        """
    )
    
    # parser.add_argument(
    #     '--conference', '-c',
    #     nargs='+',
    #     required=True,
    #     help='会议名称（可指定多个，如: NeurIPS ICLR ICML）'
    # )
    # parser.add_argument(
    #     '--year', '-y',
    #     required=True,
    #     help='年份（如: 2025）'
    # )
    
    parser.add_argument(
        '--headless', '-H',
        action='store_true',
        help='使用无头模式（后台运行，不显示浏览器窗口）'
    )
    parser.add_argument(
        '--wait-time', '-w',
        type=int,
        default=5,
        help='页面加载等待时间（秒），默认5秒'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='输出目录，默认使用会议名称作为目录'
    )
    parser.add_argument(
        '--overwrite',
        default=True,
        action='store_true',
        help='如果文件已存在，覆盖现有文件'
    )
    
    args = parser.parse_args()
    
    # 构建会议和年份列表
    # conferences_years = [(conf, args.year) for conf in args.conference]

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
        ("AAAI", "2024"),
        # ("AAAI", "2023"),
        
        # ("IJCAI", "2024"),
        # ("IJCAI", "2023"),
        
        # ("ACL", "2024"),
        # ("ACL", "2023"),

        # ("EMNLP", "2024"),
        # ("EMNLP", "2023"),
    ]

    
    # 批量爬取
    results = {}
    for conference, year in paper_list:
        print(f"\n{'='*100}")
        print(f"处理: {conference} {year}")
        print(f"{'='*100}")
        
        filepath = crawl_paper_list(
            conference, 
            year, 
            headless=args.headless, 
            wait_time=args.wait_time,
            output_dir=args.output_dir,
            overwrite=args.overwrite
        )
        results[f"{conference}_{year}"] = filepath
        
        # 在两次爬取之间等待
        if len(paper_list) > 1:
            print(f"\n等待3秒后继续下一个...")
            time.sleep(3)
    
    # 打印总结
    print(f"\n{'='*100}")
    print("爬取总结:")
    print(f"{'='*100}")
    success_count = sum(1 for v in results.values() if v)
    print(f"成功: {success_count}/{len(results)}")
    for key, value in results.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value if value else '失败'}")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    # python crawl_papercopilot.py --conference NeurIPS --year 2024 --overwrite
    main()
