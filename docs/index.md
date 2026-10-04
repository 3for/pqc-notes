# 后量子密码学习笔记

围绕格密码学，整理阅读材料、概念解释与补充推导。从 LWE 和 SIS 出发，逐步理解 ML-KEM 与 ML-DSA 背后的数学结构。

[阅读基础格密码学笔记](basic-lattice-cryptography-notes-zh.md){ .md-button .md-button--primary }
[下载英文原文](basic-lattice-cryptography-2024-1287.pdf){ .md-button }

## 基础格密码学

本篇笔记基于 Vadim Lyubashevsky 的 [*Basic Lattice Cryptography: The concepts behind Kyber (ML-KEM) and Dilithium (ML-DSA)*](https://eprint.iacr.org/2024/1287.pdf)，原文版本为 2025 年 6 月 18 日，包含中文整理及附录中的补充推导。

按原文顺序阅读，也可以通过章节目录跳转：

- **加密与 LWE**：从简单构造理解误差、参数与密文压缩。
- **格与困难性**：连接 LWE、SIS 和格上的几何问题。
- **多项式环与 ML-KEM**：理解代数结构、NTT 与 Kyber（ML-KEM）。
- **证明与 ML-DSA**：从 $\Sigma$ 协议、Fiat–Shamir 变换走向 Dilithium（ML-DSA）。
- **补充推导**：混合论证、误差分布与多项式乘法的矩阵表示。

## 阅读与查找

正文保留公式编号和脚注。点击脚注序号查看解释，再通过返回箭头回到正文；较宽的公式和表格可以横向滚动。

使用搜索查找概念，如「模数切换」「高斯消元」或「Fiat-Shamir」。

