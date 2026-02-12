---
date: "2026-02-12"
title: "AI Daily Paper Digest - 2026年2月12日"
total_papers: 10
focus_papers: 4
---

# 🗞️ AI Daily Paper Digest

> 📅 2026年2月12日 | 共 10 篇精选论文 | 🔥 4 篇重点关注

---

## 🔥 今日亮点

今天最大的新闻是 **Step 3.5 Flash** 的发布——一个 196B 参数的稀疏 MoE 模型，仅用 11B 活跃参数就达到了 GPT-5.2 xHigh 和 Gemini 3.0 Pro 的水平，137 个 upvotes 遥遥领先。RL 方向的创新依然活跃：**iGRPO** 提出自反馈驱动的迭代 GRPO，在 AIME 上达到新 SOTA；**GRU-Mem** 用门控机制解决长上下文推理的效率问题；**PhyCritic** 将 RLVR 应用于物理 AI 评判模型。**ASA** 则揭示了一个有趣的"懒惰代理"现象——模型知道该用工具却不用。

---

## 📊 Top 10 论文排行

| # | 论文 | 🔺 | 关键词 |
|---|------|-----|--------|
| 1 | [Step 3.5 Flash: 11B 活跃参数的前沿级智能](papers/2602.10604.md) | 137 | MoE, Agent RL, Scaling |
| 2 | [GENIUS: 生成式流体智力评估](papers/2602.11144.md) | 36 | Benchmark, Multimodal |
| 3 | [PhyCritic: 物理 AI 多模态评判模型](papers/2602.11124.md) | 29 | Physical AI, RLVR |
| 4 | [ASA: 免训练工具调用表示工程](papers/2602.04935.md) | 22 | Agent, Tool-Calling |
| 5 | [GRU-Mem: 门控循环记忆长上下文推理](papers/2602.10560.md) | 21 | Long-Context, RL |
| 6 | [TimeChat-Captioner: 时间感知视频字幕](papers/2602.08711.md) | 17 | Video, GRPO |
| 7 | [Aletheia: 迈向自主数学研究](papers/2602.10177.md) | 17 | Math Research, Agent |
| 8 | [G-LNS: LLM 自动启发式设计](papers/2602.08253.md) | 15 | Optimization, LLM |
| 9 | [LatentLens: 揭示 VLM 中可解释的视觉 Token](papers/2602.00462.md) | 14 | Interpretability, VLM |
| 10 | [iGRPO: 自反馈驱动的 LLM 推理](papers/2602.09000.md) | 13 | RL, GRPO, Math SOTA |

---

## 🎯 重点关注 (Agent RL / Scaling RL)

### 1. Step 3.5 Flash (🔺137)
196B 总参数、11B 活跃参数的稀疏 MoE 模型。核心亮点是**可扩展的 RL 框架**——结合验证信号与偏好反馈，在大规模 off-policy 训练下保持稳定，实现数学、代码和工具使用上的持续自我提升。MTP-3 多 token 预测和 3:1 滑动窗口/全注意力优化了代理场景的延迟。
→ [详细解读](papers/2602.10604.md)

### 2. PhyCritic (🔺29)
将 RLVR 应用于物理 AI 领域的评判模型。两阶段管线：物理技能预热 + 自参考评判微调。自参考机制让评判模型在判断前先生成自己的预测作为参考，提升判断稳定性。
→ [详细解读](papers/2602.11124.md)

### 3. ASA (🔺22)
揭示"懒惰代理"问题：LLM 中间层已能完美解码工具使用意图，但行为上却过于保守。通过推理时激活干预，仅 20KB 资产即可将工具调用 F1 从 0.18 提升到 0.50。
→ [详细解读](papers/2602.04935.md)

### 4. iGRPO (🔺13)
GRPO 的两阶段迭代扩展：先采样多个草稿选最佳，再以最佳草稿为条件进行精炼。在 7B 模型上达到 AIME24 85.62%、AIME25 79.64% 新 SOTA。延迟熵崩塌是一个有趣的副效果。
→ [详细解读](papers/2602.09000.md)

---

## 📈 趋势观察

1. **RL 在各领域全面开花**：从推理（iGRPO）到代理（Step 3.5 Flash）到评判模型（PhyCritic）到记忆管理（GRU-Mem），RL 正在成为 LLM 训练的核心范式
2. **效率与能力的新平衡**：Step 3.5 Flash 证明了通过稀疏 MoE，小规模活跃参数可以达到前沿水平
3. **代理系统持续升温**：工具调用（ASA）、多轮交互（Step 3.5 Flash）、自主研究（Aletheia）都在推进代理能力
4. **评估与理解并重**：GENIUS 和 LatentLens 分别从评估和解释性角度深入理解多模态模型

---

*由 AI Daily 自动生成 | 数据来源：HuggingFace Daily Papers*