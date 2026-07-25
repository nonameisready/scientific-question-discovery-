# benchmark/ — 评测基准

科学问题发现能力的评测基准。

## 规划内容

- 任务定义：给定研究背景/文献集合，评测系统提出科学问题的能力
- 评分维度：新颖性（novelty）、可行性（feasibility）、科学价值（significance）、清晰度（clarity）
- 评分方式：人工评估协议 + 自动评估（LLM-as-judge）
- Baseline 方法与参考结果

## 约定

- 任务数据引用 `datasets/` 中的数据集，不在此重复存放
- 评分标准（rubric）以文档形式明确给出，保证评估可复现
