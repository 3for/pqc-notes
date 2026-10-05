# 后量子密码学习笔记

深入探索后量子密码，连接论文中的思想与安全论证、标准中的算法与约束，以及实际实现中的工程取舍。内容以中文为主，面向具备密码学基础的学习者、研究者与开发者。

[阅读基础格密码学笔记](basic-lattice-cryptography-notes-zh.md){ .md-button .md-button--primary }
[阅读 PQC 与区块链专题](blockchain/index.md){ .md-button }

## 基础格密码学

本篇笔记基于 Vadim Lyubashevsky 的 [*Basic Lattice Cryptography: The concepts behind Kyber (ML-KEM) and Dilithium (ML-DSA)*](https://eprint.iacr.org/2024/1287.pdf)，原文版本为 2025 年 6 月 18 日，包含中文整理及附录中的补充推导。

按原文顺序阅读，也可以通过章节目录跳转：

- **加密与 LWE**：从简单构造理解误差、参数与密文压缩。
- **格与困难性**：连接 LWE、SIS 和格上的几何问题。
- **多项式环与 ML-KEM**：理解代数结构、NTT 与 Kyber（ML-KEM）。
- **证明与 ML-DSA**：从 $\Sigma$ 协议、Fiat–Shamir 变换走向 Dilithium（ML-DSA）。
- **补充推导**：混合论证、误差分布与多项式乘法的矩阵表示。

[下载对应版本的英文原文](basic-lattice-cryptography-2024-1287.pdf)。

## PQC 与区块链

围绕**威胁模型、协议迁移与实现研究**，整理区块链中的后量子迁移进展、签名方案与评估方法。

首篇[《区块链后量子迁移现状》](blockchain/pqc-migration.md)整理了 17 个区块链项目的对比、签名方案规格与标准状态，以及安全评估时的注意事项。阅读项目对比时，请结合文章注明的时间范围、评级说明和注意事项。

可以直接查看[区块链对比](blockchain/pqc-migration.md#implementations)、[签名方案](blockchain/pqc-migration.md#signatures)和[安全评估指南](blockchain/pqc-migration.md#assessment-guide)。完整阅读入口与维护方式见[专题导读](blockchain/index.md)；后续逐步补充协议迁移案例、实现分析和复现实验。

## 阅读与查找

基础格密码学笔记支持公式、参考文献、附录和脚注之间的跳转；点击脚注序号查看解释，再通过返回箭头回到正文。区块链文章提供章节目录、项目与签名对比表，以及资料来源链接。较宽的公式和表格可以横向滚动。

使用搜索查找概念，如「模数切换」「高斯消元」「后量子迁移」或「Falcon」。通过左侧导航切换专题，并跳转到当前文章的章节。
