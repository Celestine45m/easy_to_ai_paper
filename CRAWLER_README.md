# PaperCopilot 爬虫使用说明

## 功能说明

从 [papercopilot.com](https://papercopilot.com/) 网站爬取论文列表，支持：
- 根据会议名称和年份自动构建URL
- 自动点击"click to fetch all"按钮展开所有论文
- 提取`<table id="paperlist">`的内容
- 保存为HTML文件到对应会议目录

## 安装依赖

```bash
pip install selenium beautifulsoup4 requests
```

## ChromeDriver 安装

脚本使用Chrome浏览器，需要安装ChromeDriver：

1. **Windows**:
   - 下载ChromeDriver: https://chromedriver.chromium.org/downloads
   - 确保ChromeDriver在PATH中，或放在项目目录下

2. **使用webdriver-manager（推荐）**:
   ```bash
   pip install webdriver-manager
   ```
   然后修改脚本中的`setup_driver`函数使用webdriver-manager自动管理驱动

## 使用方法

### 1. 命令行使用

```bash
# 爬取单个会议
python crawl_papercopilot.py --conference NeurIPS --year 2025

# 批量爬取多个会议
python crawl_papercopilot.py --conference NeurIPS ICLR ICML --year 2025

# 使用无头模式（后台运行，不显示浏览器窗口）
python crawl_papercopilot.py --conference NeurIPS --year 2025 --headless

# 指定输出目录
python crawl_papercopilot.py --conference NeurIPS --year 2025 --output-dir ./Papers

# 调整页面加载等待时间
python crawl_papercopilot.py --conference NeurIPS --year 2025 --wait-time 10
```

### 2. Python代码调用

```python
from crawl_papercopilot import crawl_paper_list, crawl_multiple_conferences

# 单个会议
filepath = crawl_paper_list("NeurIPS", "2025", headless=False, wait_time=5)
print(f"文件已保存到: {filepath}")

# 批量爬取
conferences_years = [
    ("NeurIPS", "2025"),
    ("ICLR", "2025"),
    ("ICML", "2025"),
]
results = crawl_multiple_conferences(conferences_years, headless=False)
```

## 支持的会议

脚本内置了以下会议的URL映射：
- NeurIPS, ICLR, ICML, AAAI, IJCAI
- ACL, EMNLP, NAACL, COLING
- CVPR, ICCV, ECCV, WACV
- KDD, WWW, SIGIR
- ICRA, IROS, RSS, CoRL
- AISTATS, ACML, UAI, COLT, ALT
- ARR, COLM
- SIGGRAPH, SIGGRAPH Asia
- ACM-MM

如果会议不在列表中，脚本会自动尝试使用小写加连字符的格式。

## 输出文件

- 文件保存位置：`{会议名称}/{会议名称}_{年份}.html`
- 例如：`NeurIPS/NeurIPS_2025.html`
- 文件包含完整的HTML结构，包括`<table id="paperlist">`及其所有内容

## 注意事项

1. **网络连接**：确保网络连接正常，能够访问 papercopilot.com
2. **等待时间**：如果网络较慢，可以增加`--wait-time`参数
3. **Chrome浏览器**：需要安装Chrome浏览器
4. **反爬虫**：如果遇到反爬虫限制，可以：
   - 增加等待时间
   - 使用非无头模式（显示浏览器窗口）
   - 在两次爬取之间增加延迟

## 故障排除

### 问题1：找不到ChromeDriver
**解决方案**：
- 安装ChromeDriver并确保在PATH中
- 或使用webdriver-manager自动管理

### 问题2：找不到"click to fetch all"按钮
**解决方案**：
- 页面可能已自动加载所有内容，脚本会继续提取表格
- 检查URL是否正确

### 问题3：超时错误
**解决方案**：
- 增加`--wait-time`参数
- 检查网络连接
- 确认URL是否正确

### 问题4：表格为空
**解决方案**：
- 检查页面是否完全加载
- 尝试手动访问URL确认页面结构
- 增加等待时间

## 示例输出

```
====================================================================================================
开始爬取: NeurIPS 2025
====================================================================================================

目标URL: https://papercopilot.com/paper-list/neurips-paper-list/neurips-2025-paper-list/
正在启动浏览器...
正在访问页面...
等待页面加载（5秒）...
正在查找并点击'click to fetch all'按钮...
  ✓ 成功点击按钮: //button[contains(text(), 'click to fetch all')]
等待内容加载完成...
正在提取表格内容...
  ✓ 成功提取表格，大小: 123456 字符
  ✓ 已保存到: NeurIPS/NeurIPS_2025.html

✅ 爬取成功！文件已保存
正在关闭浏览器...
```
