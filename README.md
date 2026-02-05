# Easy to AI Papers

一个便捷的AI论文信息获取与翻译工具，从 [Paper Copilot](https://papercopilot.com/) 网站获取历年AI会议论文信息，自动翻译并生成中文txt文件，方便中文用户查找和阅读AI论文资料。

## 📋 项目简介

本项目旨在帮助中文用户更方便地获取和浏览AI领域的顶级会议论文。通过从Paper Copilot网站抓取论文信息，使用大语言模型进行翻译，生成结构化的中文txt文件，让论文查找变得更加简单高效。

## ✨ 主要功能

- 🔍 **抓取论文信息**：从Paper Copilot网站获取AI会议论文的详细信息
- 🌐 **智能翻译**：使用LLM自动将论文标题翻译为中文
- 📝 **结构化输出**：生成包含论文标题、中文标题、链接、类别、作者、机构等信息的txt文件
- 📚 **多会议支持**：支持NIPS、ICML等主流AI会议
- 💾 **本地存储**：所有论文信息以txt格式保存在本地，方便离线查阅

## 🗂️ 项目结构

```
easy_to_ai_papers/
├── paper_list.py          # 主程序：提取和翻译论文信息
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明文档
└── papers/               # 论文数据目录
    ├── nips2026.html                    # NIPS 2026会议HTML文件
    ├── nips2026_accepted_titles.txt     # NIPS 2026论文中文列表
    ├── icml2025_accepted_titles.txt     # ICML 2025论文中文列表
    └── icml2026_paple_table.html        # ICML 2026会议HTML文件
```

## 🚀 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备HTML文件

从 [Paper Copilot](https://papercopilot.com/) 网站下载目标会议的HTML文件，保存到 `papers/` 目录下。

### 3. 运行程序

修改 `paper_list.py` 中的文件路径和输出文件名，然后运行：

```bash
python paper_list.py
```

程序会自动：
- 解析HTML文件，提取论文信息
- 使用LLM翻译论文标题
- 将结果保存到指定的txt文件

### 4. 查看结果

生成的txt文件包含每篇论文的详细信息：
- 论文编号
- 英文标题
- 中文标题（翻译）
- 论文链接
- 类别
- 作者
- 机构
- 展示类型

## 📄 输出示例

```
No.1. Paper Title in English
   标题: 论文的中文标题
   链接: https://openreview.net/forum/...
   类别: Machine Learning
   作者: Author1, Author2
   机构: University1, University2
   类型: Poster
```



## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 感谢 [Paper Copilot](https://papercopilot.com/) 提供论文信息
- 感谢所有为AI研究做出贡献的研究者们
