# Scientific Question Discovery（科学问题发现）

> 面向 AGI 的科学问题自动发现研究 —— 探索智能体如何像科学家一样提出好问题。

## 项目简介

本仓库是论文《Scientific Question Discovery》的研究工作区。我们认为，通往 AGI 的关键能力之一不是回答问题，而是**发现值得研究的科学问题**。本项目围绕这一核心思路展开：

- 提出一个科学问题发现的形式化框架（framework）
- 设计可复现的实验（experiments）
- 构建评测基准（benchmark）与数据集（datasets）
- 撰写并迭代论文（paper）

## 仓库结构

```
scientific-question-discovery/
├── README.md          # 项目说明（本文件）
├── paper/             # 论文正文、LaTeX 源码、参考文献
├── framework/         # 核心框架：问题发现的形式化定义与方法实现
├── experiments/       # 实验代码、配置与结果
├── benchmark/         # 评测基准：任务定义、评分标准、baseline
├── datasets/          # 数据集及其构建脚本、说明文档
├── figures/           # 论文与实验用图
└── LICENSE            # 开源许可证（MIT）
```

## 研究路线（Roadmap）

- [ ] 明确研究问题与相关工作综述（paper/outline.md）
- [ ] 定义科学问题发现的形式化框架
- [ ] 构建数据集与评测基准
- [ ] 完成核心实验与消融实验
- [ ] 撰写论文初稿并迭代

## 快速开始

```bash
git clone <repo-url>
cd scientific-question-discovery
```

各子目录下均有独立的 README 说明其用途与使用方式。

## 引用

论文完成后将在此处提供 BibTeX 引用格式。

## 许可证

本项目采用 [MIT License](LICENSE)。
