# Easy to AI Papers

一个便捷的AI论文信息获取与翻译工具，从 [Paper Copilot](https://papercopilot.com/) 网站获取历年AI会议论文信息，自动翻译并生成中文txt文件，方便中文用户查找和阅读AI论文资料。

## 📋 项目简介

本项目旨在帮助中文用户更方便地获取和浏览AI领域的顶级会议论文。通过从Paper Copilot网站抓取论文信息，使用大语言模型进行翻译，生成结构化的中文txt和json文件，让论文查找变得更加简单高效。

**核心特性：**
- 🎯 自动化论文信息提取和翻译
- 🔍 根据关键词智能筛选论文
- 📄 从arXiv自动获取论文摘要并翻译
- 📊 提供论文机构、类别等统计分析
- 🔄 支持多种数据格式（txt/json）
- 🌍 支持多个顶级AI会议（ICLR、ICML、NeurIPS、AAAI、IJCAI、ACL、EMNLP）

## ✨ 主要功能

- 🔍 **抓取论文信息**：从Paper Copilot网站获取AI会议论文的详细信息
- 🌐 **智能翻译**：使用LLM自动将论文标题和摘要翻译为中文
- 🔎 **关键词筛选**：根据关键词从所有会议中筛选目标论文
- 📄 **摘要获取**：自动从arXiv获取论文摘要并翻译为中文
- 📝 **结构化输出**：生成包含论文标题、中文标题、链接、类别、作者、机构、摘要等信息的txt和json文件
- 📚 **多会议支持**：支持ICLR、ICML、NeurIPS、AAAI、IJCAI、ACL、EMNLP等主流AI会议
- 💾 **本地存储**：所有论文信息以txt和json格式保存在本地，方便离线查阅
- 📊 **统计分析**：提供机构分布和类别分布的统计分析工具
- 🔢 **数据格式**：支持txt和json两种格式，便于不同场景使用
- ⚡ **实时处理**：支持逐条处理论文，实时保存结果，避免数据丢失

## 🗂️ 项目结构

```
easy_to_ai_papers/
├── paper_list.py                    # 主程序：提取和翻译论文信息，支持从arXiv获取摘要
├── extract_papers_by_title.py      # 根据关键词提取论文，支持从arXiv获取摘要并翻译
├── analyze_statistics.py            # 合并的统计分析工具（推荐使用）
├── analyze_affiliations.py         # 机构统计分析工具（独立版本）
├── analyze_categories.py           # 类别统计分析工具（独立版本）
├── test_html_structure.py          # HTML结构测试脚本
├── requirements.txt                # 项目依赖
├── README.md                       # 项目说明文档
├── LICENSE                         # 许可证文件
├── RESEARCH_EVALUATION.md         # 研究评估报告
├── WANTED_PAPERS/                  # 关键词筛选的论文结果目录
├── src/                            # 源代码目录
│   ├── conf/                       # 配置文件
│   │   └── GlobalParament.py      # 全局参数配置
│   └── llm/                        # LLM相关模块
│       ├── llm_client.py          # LLM客户端
│       └── llm_aksk.py            # LLM认证配置
├── ICLR/                           # ICLR会议数据
│   ├── ICLR_2025.html             # ICLR 2025 HTML文件
│   ├── ICLR_2025_accepted.txt     # ICLR 2025 论文中文列表
│   ├── ICLR_2025_accepted.json    # ICLR 2025 论文JSON数据
│   └── ICLR_2025_statistics_summary.txt  # 统计汇总报告
├── ICML/                           # ICML会议数据
│   ├── ICML_2025.html             # ICML 2025 HTML文件
│   ├── ICML_2025_accepted.txt     # ICML 2025 论文中文列表
│   ├── ICML_2025_accepted.json    # ICML 2025 论文JSON数据
│   └── ICML_2025_statistics_summary.txt  # 统计汇总报告
├── NeurIPS/                        # NeurIPS会议数据
│   ├── NeurIPS_2025.html          # NeurIPS 2025 HTML文件
│   ├── NeurIPS_2025_accepted.txt  # NeurIPS 2025 论文中文列表
│   ├── NeurIPS_2025_accepted.json # NeurIPS 2025 论文JSON数据
│   └── NeurIPS_2025_statistics_summary.txt  # 统计汇总报告
├── AAAI/                           # AAAI会议数据
│   ├── AAAI_2025.html             # AAAI 2025 HTML文件
│   ├── AAAI_2025_accepted.txt     # AAAI 2025 论文中文列表
│   ├── AAAI_2025_accepted.json    # AAAI 2025 论文JSON数据
│   └── AAAI_2025_statistics_summary.txt  # 统计汇总报告
├── IJCAI/                          # IJCAI会议数据
│   ├── IJCAI_2025.html            # IJCAI 2025 HTML文件
│   ├── IJCAI_2025_accepted.txt    # IJCAI 2025 论文中文列表
│   ├── IJCAI_2025_accepted.json   # IJCAI 2025 论文JSON数据
│   └── IJCAI_2025_statistics_summary.txt  # 统计汇总报告
├── ACL/                            # ACL会议数据
│   ├── ACL_2025.html              # ACL 2025 HTML文件
│   ├── ACL_2025_accepted.txt      # ACL 2025 论文中文列表
│   ├── ACL_2025_accepted.json     # ACL 2025 论文JSON数据
│   └── ACL_2025_statistics_summary.txt  # 统计汇总报告
└── EMNLP/                          # EMNLP会议数据
    ├── EMNLP_2025.html            # EMNLP 2025 HTML文件
    ├── EMNLP_2025_accepted.txt    # EMNLP 2025 论文中文列表
    ├── EMNLP_2025_accepted.json   # EMNLP 2025 论文JSON数据
    └── EMNLP_2025_statistics_summary.txt  # 统计汇总报告
```

## 🚀 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd easy_to_ai_papers
   ```

2. **安装依赖**
   ```bash
   pip install beautifulsoup4 requests langchain langchain-openai huggingface_hub
   ```

3. **配置LLM**（编辑 `src/conf/GlobalParament.py` 和 `src/llm/llm_client.py`）

4. **准备HTML文件**（从Paper Copilot下载，保存到对应会议目录）

5. **运行程序**
   ```bash
   # 提取和翻译论文信息（支持从arXiv获取摘要）
   python paper_list.py
   
   # 根据关键词提取论文（支持从arXiv获取摘要并翻译）
   python extract_papers_by_title.py
   
   # 生成统计分析报告
   python analyze_statistics.py
   ```

## 📖 详细使用说明

### 1. 环境要求

- Python 3.7+
- 需要配置LLM API（用于翻译功能）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

**主要依赖包：**
- `beautifulsoup4` - HTML解析
- `requests` - HTTP请求
- `langchain` - LLM框架
- `langchain-openai` - OpenAI兼容的LLM客户端
- `huggingface_hub` - HuggingFace Hub支持

如果 `requirements.txt` 不完整，可以手动安装：
```bash
pip install beautifulsoup4 requests langchain langchain-openai huggingface_hub
```

### 3. 配置LLM

项目使用LLM进行论文标题翻译，需要配置LLM API：

1. **配置认证信息**：编辑 `src/conf/GlobalParament.py`，设置：
   - `access_key`: API访问密钥
   - `secret_key`: API密钥
   - `user_id`: 用户ID
   - `domain`: API服务器域名

2. **配置业务代码**：在 `src/llm/llm_client.py` 中，`post_requests_llm` 函数需要传入业务代码（Code），根据你的LLM服务配置进行修改。

**注意**：如果你使用的是标准的OpenAI API或其他兼容的API，可以直接修改 `get_llm_client()` 函数中的配置。

### 4. 准备HTML文件

从 [Paper Copilot](https://papercopilot.com/) 网站下载目标会议的HTML文件，保存到对应的会议目录下（如 `ICLR/`, `ICML/`, `NeurIPS/`），文件名格式为：`{会议名称}_{年份}.html`（如 `ICLR_2025.html`）。

**下载步骤：**
1. 访问 [Paper Copilot](https://papercopilot.com/)
2. 选择目标会议和年份
3. 下载HTML格式的论文列表
4. 将文件保存到对应的会议目录

### 5. 运行程序

#### 方式一：提取所有论文信息（paper_list.py）

修改 `paper_list.py` 中的会议名称和年份，然后运行：

```bash
python paper_list.py
```

程序会自动：
- 解析HTML文件，提取论文信息
- 使用LLM翻译论文标题
- （可选）从arXiv获取摘要并翻译
- 将结果保存到txt和json文件

**配置说明：**
在 `paper_list.py` 的 `__main__` 部分修改以下变量：
```python
conference = "ICLR"  # 会议名称：ICLR, ICML, NeurIPS, AAAI, IJCAI, ACL, EMNLP
year = "2025"        # 年份
fetch_abstracts = True  # 是否从arXiv获取摘要并翻译（需要较长时间）
request_delay = 2    # 每次请求之间的延迟（秒），避免请求过快
```

#### 方式二：根据关键词筛选论文（extract_papers_by_title.py）

根据关键词从所有会议的JSON文件中筛选论文：

```bash
python extract_papers_by_title.py
```

**功能特点：**
- 支持多个关键词（OR关系，只要标题包含任意一个关键词就匹配）
- 支持大小写敏感/不敏感搜索
- 自动标注论文来源会议
- （可选）从arXiv获取摘要并翻译
- 逐条处理，实时保存结果

**配置说明：**
在 `extract_papers_by_title.py` 的 `main()` 函数中修改：
```python
keywords = ["prediction"]  # 关键词列表，支持多个关键词
# keywords = ["prediction", "evaluation", "rank"]  # 多个关键词示例
case_sensitive = False  # 是否区分大小写
fetch_abstracts = True  # 是否从arXiv获取摘要并翻译
request_delay = 2  # 请求延迟（秒）
output_file = "WANTED_PAPERS/papers_with_keywords.txt"  # 输出文件
```

**输出文件：**
- `WANTED_PAPERS/papers_with_keywords.txt` - 包含匹配论文的详细信息（包括摘要）

### 6. 统计分析

项目提供了合并的统计分析工具，可以一次性完成类别和机构统计：

#### 合并统计分析（推荐）
```bash
python analyze_statistics.py
```

**功能特点：**
- 同时统计论文的类别分布和机构分布
- 支持批量处理多个会议（在脚本中配置会议列表）
- 支持第一作者机构或所有机构的统计模式
- 生成统一的汇总报告文件

**输出文件：**
- `{会议}/{会议}_{年份}_statistics_summary.txt` - 包含类别统计和机构统计的完整报告

**配置说明：**
在 `analyze_statistics.py` 的 `main()` 函数中可以修改：
```python
paper_list = ["ICLR", "ICML", "NeurIPS", "AAAI", "IJCAI", "ACL", "EMNLP"]  # 会议列表
year = "2025"  # 年份
first_author_only = False  # False=统计所有机构, True=仅统计第一作者机构
```

#### 独立统计分析工具（可选）

如果需要单独运行某个统计：

**机构统计分析：**
```bash
python analyze_affiliations.py
```

**类别统计分析：**
```bash
python analyze_categories.py
```

### 7. 查看结果

#### txt格式输出
生成的txt文件包含每篇论文的详细信息：
- 论文编号
- 英文标题
- 中文标题（翻译）
- 论文链接
- 类别
- 作者
- 机构
- 展示类型
- （可选）arXiv ID和链接
- （可选）英文摘要
- （可选）中文摘要（翻译）

#### json格式输出
每行一个JSON对象，包含以下字段：
- `title`: 英文标题
- `title_ch`: 中文标题
- `url`: 论文链接
- `category`: 类别
- `authors`: 作者列表
- `affiliations`: 机构列表
- `presentation_type`: 展示类型
- `arxiv_id`: arXiv ID（如果获取了摘要）
- `arxiv_link`: arXiv链接（如果获取了摘要）
- `abstract`: 英文摘要（如果获取了摘要）
- `abstract_ch`: 中文摘要（如果获取了摘要）
- `source`: 论文来源会议（仅extract_papers_by_title.py）
- `matched_keywords`: 命中的关键词（仅extract_papers_by_title.py）

## 📄 输出示例

### txt格式示例（包含摘要）
```
[No.1] Paper Title in English
来源: ICLR 2025
命中: prediction
标题: 论文的中文标题
类别: Machine Learning
作者: Author1; Author2
机构: University1; University2
类型: Poster
链接: https://openreview.net/forum/...
arXiv ID: 2301.12345
arXiv链接: https://arxiv.org/abs/2301.12345

英摘:
This paper presents a novel approach to...

中摘:
本文提出了一种新的方法来...
----------------------------------------------------------------------------------------------------
```

### json格式示例（包含摘要）
```json
{"title": "Paper Title in English", "title_ch": "论文的中文标题", "url": "https://openreview.net/forum/...", "category": "Machine Learning", "authors": "Author1; Author2", "affiliations": "University1; University2", "presentation_type": "Poster", "arxiv_id": "2301.12345", "arxiv_link": "https://arxiv.org/abs/2301.12345", "abstract": "This paper presents a novel approach to...", "abstract_ch": "本文提出了一种新的方法来...", "source": "ICLR 2025", "matched_keywords": ["prediction"]}
```

### 统计汇总报告示例
```
====================================================================================================
ICLR 2025 论文统计分析汇总报告
====================================================================================================

【一、论文类别统计】
====================================================================================================
总论文数: 3103
总类别数: 25

排名   类别                                                        数量      占比
----------------------------------------------------------------------------------------------------
1      Machine Learning                                           850      27.39%
2      Deep Learning                                               620      19.98%
...

【二、论文机构统计】
====================================================================================================
统计模式: 所有机构
总论文数: 3103
总机构数: 1250

排名   机构名称                                                            论文数      占比
----------------------------------------------------------------------------------------------------
1      Stanford University                                                 120       3.87%
2      MIT                                                                 95        3.06%
...
```



## ⚙️ 配置说明

### LLM配置

项目使用LangChain框架调用LLM进行翻译。主要配置位置：

- **认证配置**：`src/conf/GlobalParament.py`
  - 设置API访问密钥和服务器地址
  
- **LLM客户端**：`src/llm/llm_client.py`
  - 配置LLM模型和API端点
  - 默认使用OpenAI兼容的API格式

### arXiv摘要获取配置

项目支持从arXiv自动获取论文摘要并翻译：

- **工作原理**：
  1. 根据论文标题在arXiv中搜索匹配的论文
  2. 提取arXiv ID
  3. 从arXiv API获取论文详情（包括摘要）
  4. 使用LLM翻译摘要为中文

- **配置位置**：
  - `paper_list.py`: 设置 `fetch_abstracts = True` 启用摘要获取
  - `extract_papers_by_title.py`: 设置 `fetch_abstracts = True` 启用摘要获取
  - `request_delay`: 设置请求延迟（秒），避免请求过快（arXiv API有速率限制，建议至少2秒）

- **注意事项**：
  - 获取摘要需要较长时间，建议设置合适的延迟
  - 不是所有论文都能在arXiv找到（只有已上传到arXiv的论文才能获取）
  - 程序会逐条处理，实时保存结果，即使中途中断也不会丢失已处理的数据

### 关键词筛选配置

- **extract_papers_by_title.py**：
  - `keywords`: 关键词列表，支持多个关键词（OR关系）
  - `case_sensitive`: 是否区分大小写
  - `fetch_abstracts`: 是否获取摘要
  - `output_file`: 输出文件路径

### 统计分析配置

- **合并统计工具**：`analyze_statistics.py`（推荐）
  - 在 `main()` 函数中配置会议列表和年份
  - 可设置 `first_author_only` 参数选择机构统计方式
  - 自动生成包含类别和机构统计的汇总报告

- **独立统计工具**：
  - `analyze_affiliations.py` - 机构统计
  - `analyze_categories.py` - 类别统计

## ⚠️ 注意事项

1. **LLM API配置**：确保LLM API配置正确，否则翻译功能无法使用
2. **HTML格式**：确保HTML文件格式正确，程序会解析表格结构提取论文信息
3. **文件路径**：确保HTML文件路径与 `paper_list.py` 中的配置一致
4. **翻译速度**：大量论文翻译可能需要较长时间，建议分批处理
5. **数据过滤**：程序会自动过滤被拒绝（Reject）和撤回（Withdraw）的论文
6. **arXiv摘要获取**：
   - 需要网络连接访问arXiv API
   - 不是所有论文都能在arXiv找到
   - 建议设置合适的请求延迟（至少2秒），避免触发API速率限制
   - 程序支持逐条处理，实时保存，即使中断也不会丢失数据
7. **关键词筛选**：支持多个关键词，只要标题包含任意一个关键词就匹配（OR关系）

## 🔧 故障排除

### 常见问题

**Q: 翻译失败怎么办？**
- 检查LLM API配置是否正确
- 检查网络连接是否正常
- 查看控制台错误信息

**Q: HTML解析失败？**
- 确认HTML文件格式正确
- 检查文件编码是否为UTF-8
- 使用 `test_html_structure.py` 测试HTML结构

**Q: 统计结果为空？**
- 确认JSON文件已生成
- 检查JSON文件格式是否正确（每行一个JSON对象）

**Q: 无法从arXiv获取摘要？**
- 确认论文已上传到arXiv（不是所有会议论文都会上传到arXiv）
- 检查网络连接是否正常
- 确认arXiv API可访问（可能需要科学上网）
- 检查论文标题是否与arXiv上的标题完全匹配

**Q: 关键词筛选没有结果？**
- 检查关键词拼写是否正确
- 尝试使用更通用的关键词
- 确认JSON文件已生成且格式正确
- 检查是否设置了正确的大小写敏感选项

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 感谢 [Paper Copilot](https://papercopilot.com/) 提供论文信息
- 感谢所有为AI研究做出贡献的研究者们
