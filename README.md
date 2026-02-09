# Easy to AI Papers

一个便捷的AI论文信息获取与翻译工具，从 [Paper Copilot](https://papercopilot.com/) 网站获取历年AI会议论文信息，自动翻译并生成中文txt文件，方便中文用户查找和阅读AI论文资料。

## 📋 项目简介

本项目旨在帮助中文用户更方便地获取和浏览AI领域的顶级会议论文。通过从Paper Copilot网站抓取论文信息，使用大语言模型进行翻译，生成结构化的中文txt和json文件，让论文查找变得更加简单高效。

**核心特性：**
- 🎯 自动化论文信息提取和翻译
- 📊 提供论文机构、类别等统计分析
- 🔄 支持多种数据格式（txt/json）
- 🌍 支持多个顶级AI会议（ICLR、ICML、NeurIPS）

## ✨ 主要功能

- 🔍 **抓取论文信息**：从Paper Copilot网站获取AI会议论文的详细信息
- 🌐 **智能翻译**：使用LLM自动将论文标题翻译为中文
- 📝 **结构化输出**：生成包含论文标题、中文标题、链接、类别、作者、机构等信息的txt和json文件
- 📚 **多会议支持**：支持ICLR、ICML、NeurIPS等主流AI会议
- 💾 **本地存储**：所有论文信息以txt和json格式保存在本地，方便离线查阅
- 📊 **统计分析**：提供机构分布和类别分布的统计分析工具
- 🔢 **数据格式**：支持txt和json两种格式，便于不同场景使用

## 🗂️ 项目结构

```
easy_to_ai_papers/
├── paper_list.py                    # 主程序：提取和翻译论文信息
├── analyze_affiliations.py         # 机构统计分析工具
├── analyze_categories.py           # 类别统计分析工具
├── test_html_structure.py          # HTML结构测试脚本
├── requirements.txt                # 项目依赖
├── README.md                       # 项目说明文档
├── LICENSE                         # 许可证文件
├── RESEARCH_EVALUATION.md         # 研究评估报告
├── src/                            # 源代码目录
│   ├── conf/                       # 配置文件
│   │   └── GlobalParament.py      # 全局参数配置
│   └── llm/                        # LLM相关模块
│       ├── llm_client.py          # LLM客户端
│       └── llm_aksk.py            # LLM认证配置
├── ICLR/                           # ICLR会议数据
│   ├── ICLR_2025.html             # ICLR 2025 HTML文件
│   ├── ICLR_2025_accepted.txt     # ICLR 2025 论文中文列表
│   └── ICLR_2025_accepted.json    # ICLR 2025 论文JSON数据
├── ICML/                           # ICML会议数据
│   ├── ICML_2025.html             # ICML 2025 HTML文件
│   ├── ICML_2025_accepted_titles.txt  # ICML 2025 论文标题列表
│   └── ICML_2025_accepted_titles.json # ICML 2025 论文JSON数据
└── NeurIPS/                        # NeurIPS会议数据
    ├── NeurIPS_2025.html          # NeurIPS 2025 HTML文件
    ├── NeurIPS_2025_accepted.txt  # NeurIPS 2025 论文中文列表
    ├── NeurIPS_2025_accepted.json # NeurIPS 2025 论文JSON数据
    ├── NeurIPS_2025_accepted_titles.txt  # NeurIPS 2025 论文标题列表
    ├── NeurIPS_2025_affiliation_statistics.txt  # 机构统计结果
    └── NeurIPS_2025_category_statistics.txt     # 类别统计结果
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
   python paper_list.py
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

修改 `paper_list.py` 中的会议名称和年份，然后运行：

```bash
python paper_list.py
```

程序会自动：
- 解析HTML文件，提取论文信息
- 使用LLM翻译论文标题
- 将结果保存到txt和json文件

**配置说明：**
在 `paper_list.py` 的 `__main__` 部分修改以下变量：
```python
conference = "ICLR"  # 会议名称：ICLR, ICML, NeurIPS
year = "2025"        # 年份
```

### 6. 统计分析

项目提供了两个统计分析工具：

#### 机构统计分析
```bash
python analyze_affiliations.py
```
- 统计论文的机构分布
- 支持第一作者机构或所有机构的统计
- 生成机构排名和占比统计
- 输出文件：`{会议}/{会议}_{年份}_affiliation_statistics.txt`

#### 类别统计分析
```bash
python analyze_categories.py
```
- 统计论文的类别分布
- 生成类别排名和占比统计
- 输出文件：`{会议}/{会议}_{年份}_category_statistics.txt`

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

#### json格式输出
每行一个JSON对象，包含以下字段：
- `title`: 英文标题
- `title_ch`: 中文标题
- `url`: 论文链接
- `category`: 类别
- `authors`: 作者列表
- `affiliations`: 机构列表
- `presentation_type`: 展示类型

## 📄 输出示例

### txt格式示例
```
No.1. Paper Title in English
   标题: 论文的中文标题
   链接: https://openreview.net/forum/...
   类别: Machine Learning
   作者: Author1; Author2
   机构: University1; University2
   类型: Poster
```

### json格式示例
```json
{"title": "Paper Title in English", "title_ch": "论文的中文标题", "url": "https://openreview.net/forum/...", "category": "Machine Learning", "authors": "Author1; Author2", "affiliations": "University1; University2", "presentation_type": "Poster"}
```

### 统计结果示例
```
================================================================================
NeurIPS 2025 论文机构统计（所有机构，按出现次数降序）
================================================================================

总论文数: 3103
总机构数: 1250
显示前 50 个机构

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

### 统计分析配置

- **机构统计**：`analyze_affiliations.py`
  - 可设置 `first_author_only` 参数选择统计方式
  - 可设置 `top_n` 参数控制显示数量

- **类别统计**：`analyze_categories.py`
  - 自动统计所有类别分布

## ⚠️ 注意事项

1. **LLM API配置**：确保LLM API配置正确，否则翻译功能无法使用
2. **HTML格式**：确保HTML文件格式正确，程序会解析表格结构提取论文信息
3. **文件路径**：确保HTML文件路径与 `paper_list.py` 中的配置一致
4. **翻译速度**：大量论文翻译可能需要较长时间，建议分批处理
5. **数据过滤**：程序会自动过滤被拒绝（Reject）和撤回（Withdraw）的论文

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

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 感谢 [Paper Copilot](https://papercopilot.com/) 提供论文信息
- 感谢所有为AI研究做出贡献的研究者们
