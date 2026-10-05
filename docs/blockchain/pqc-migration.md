# 区块链后量子迁移现状

## 1. 引言 { #introduction }

量子计算风险已不再是明天才需要面对的问题。随着 2024 年 [NIST 首批可用于生产环境的 PQC 标准](https://csrc.nist.gov/news/2024/postquantum-cryptography-fips-approved)获得批准，迁移路径正变得更加清晰，而时间窗口也显得比以往更加紧迫。各组织已经被要求着手向后量子密码学（PQC）迁移，这使“量子安全加密货币”不再只是一个宣传用语，而成为一项对实际实现的检验。

投资者和开发者需要一种通俗易懂的方式来比较具备量子就绪能力的区块链，因此本文整理了下面这份参考表。将在其中看到所有声称支持后量子密码学的主要区块链，以及它们的实际实现、签名方案选择和标准化状态。

本文重点关注签名方案，因为对于大多数区块链而言，这是最直接的量子安全薄弱点。虽然其他密码学组件（如密钥交换和哈希）同样需要升级为抗量子方案，但数字签名承担着交易授权功能，因此很可能最先、也最严重地受到量子攻击。

资料来源见[参考资料 \[1\]](#ref-quantum-canary)。

## 2. 量子就绪区块链逐项目对比 { #comparison }

### 2.1 区块链对比 { #implementations }

这份独立技术评估仅依据区块链网络当前采用标准化后量子密码学的情况（遵循 NIST 指南）进行评级。评级反映的是截至 2026 年 2 月的实现状态，并不代表项目的整体质量、其在非量子环境下的安全性或未来潜力。较低的评级表示项目仍依赖容易受到未来量子威胁的传统签名，而这在当今行业中十分普遍。

| 区块链 | 代币 | 评级 | 状态 | 签名方案 | 交易签名 | P2P | 共识机制 | 零知识证明 | 隐私保护 | GitHub |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| Quantus Network | QUAN | **A+** | 测试网 | Dilithium-5（L5） | ✅ | ✅ | ✅ | ✅ | ✅ | [Quantus-Network](https://github.com/Quantus-Network) |
| Cellframe Network | CELL | **A+** | 主网 | Dilithium-5（L5） | ✅ | ✅ | ✅ | ✅ | ✅ | [demlabs-cellframe](https://github.com/demlabs-cellframe) |
| XX Network | XX | **A** | 主网 | WOTS+（L5） | ✅ | ✅ | ✅ | ❌ | ✅ | [xxfoundation](https://github.com/xxfoundation) |
| Abelian | ABEL | **A** | 主网 | Dilithium-3（L3） | ✅ | ❌ | ✅ | ✅ | ✅ | [pqabelian](https://github.com/pqabelian) |
| Quantum Resistant Ledger | QRL | **B** | 主网 | XMSS（L5） | ✅ | ✅ | ✅ | ❌ | ❌ | [theqrl](https://github.com/theqrl) |
| Starknet | STRK | **C** | 主网 | ECDSA（L1） | ❌ | ❌ | ❌ | ✅ | ✅ | [starkware-libs](https://github.com/starkware-libs) |
| Nexus | NXS | **C** | 主网 | Falcon-512（L1） | ✅ | ❌ | ✅ | ❌ | ❌ | [Nexusoft](https://github.com/Nexusoft) |
| Zcash | ZEC | **C** | 主网 | ECDSA（L1） | ❌ | ❌ | ✅ | ❌ | ✅ | [zcash](https://github.com/zcash) |
| QANplatform | QANX | **C** | 主网 | Dilithium-5（L5） | ✅ | ❌ | ✅ | ❌ | ❌ | [QANplatform](https://github.com/QANplatform) |
| Mochimo | MCM | **C** | 主网 | WOTS+（L5） | ✅ | ❌ | ✅ | ❌ | ❌ | [mochimodev](https://github.com/mochimodev) |
| IOTA | IOTA | **C** | 主网 | Dilithium-5（L5） | ✅ | ❌ | ✅ | ❌ | ❌ | [iotaledger](https://github.com/iotaledger) |
| Bitcoin | BTC | **D** | 主网 | Schnorr（L1） | ❌ | ❌ | ✅ | ❌ | ❌ | [bitcoin](https://github.com/bitcoin) |
| Algorand | ALGO | **D** | 主网 | Falcon-1024（L5） | ✅ | ❌ | ❌ | ❌ | ❌ | [algorandfoundation](https://github.com/algorandfoundation) |
| Hedera | HBAR | **D** | 主网 | Ed25519（L1） | ❌ | ❌ | ✅ | ❌ | ❌ | [hashgraph](https://github.com/hashgraph) |
| Monero | XMR | **D** | 主网 | Ed25519（L1） | ❌ | ❌ | ✅ | ❌ | ❌ | [monero-project](https://github.com/monero-project) |
| Ethereum | ETH | **F** | 主网 | ECDSA（L1） | ❌ | ❌ | ❌ | ❌ | ❌ | [ethereum](https://github.com/ethereum) |
| Solana | SOL | **F** | 主网 | Ed25519（L1） | ❌ | ❌ | ❌ | ❌ | ❌ | [solana-foundation](https://github.com/solana-foundation) |

**图例**：✅ = 具备后量子能力，❌ = 未具备后量子能力；P2P = 点对点连接，L = NIST 安全等级。

> **数据说明**：评级按照五项后量子能力中已覆盖的项目数计算：5 项为 A+、4 项为 A、3 项为 B、2 项为 C、1 项为 D、0 项为 F。

### 2.2 签名方案 { #signatures }

密码学签名方案的详细规格和安全等级如下，公钥、私钥和签名大小均以字节为单位。

| 方案 | 类型 | 等级 | 标准 / 规范 | 公钥（字节） | 私钥（字节） | 签名（字节） | 定稿日期 |
| :--- | :---: | :---: | :--- | ---: | ---: | ---: | :---: |
| Falcon-1024 | 后量子 | L5 | [FIPS 206（草案）](https://csrc.nist.gov/presentations/2025/fips-206-fn-dsa-falcon) | 1,793 | 2,305 | 1,280 | 草案 |
| Dilithium-5 | 后量子 | L5 | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) | 2,592 | 4,896 | 4,595 | 2024-08-13 |
| XMSS | 后量子 | L5 | [RFC 8391](https://datatracker.ietf.org/doc/rfc8391/) | 64 | 1,343 | 2,500 | 2018-05-01 |
| WOTS+ | 后量子 | L5 | [RFC 8391](https://datatracker.ietf.org/doc/rfc8391/) | 2,144 | 2,144 | 2,144 | 2018-05-01 |
| Dilithium-3 | 后量子 | L3 | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) | 1,952 | 4,032 | 3,293 | 2024-08-13 |
| ECDSA | 传统密码 | L1 | [FIPS 186-5](https://csrc.nist.gov/pubs/fips/186-5/final) | 64 | 32 | 64 | 2023-02-03 |
| Schnorr | 传统密码 | L1 | [BIP 340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) | 33 | 32 | 64 | 2016-11-01 |
| Falcon-512 | 后量子 | L1 | [FIPS 206（草案）](https://csrc.nist.gov/presentations/2025/fips-206-fn-dsa-falcon) | 897 | 1,281 | 666 | 草案 |
| Ed25519 | 传统密码 | L1 | [RFC 8032](https://datatracker.ietf.org/doc/rfc8032/) | 32 | 64 | 64 | 2017-01-01 |

其中：后量子 = 后量子密码学，等级 = NIST 安全等级。

以上表格列出了签名方案选择、相关标准、宣称的 NIST 安全等级，以及会影响费用和吞吐量的大致尺寸。

### 2.3 重要说明与注意事项 { #notes-and-caveats }

#### 2.3.1 NIST 标准状态 { #standards }

NIST 目前已经最终确定了两项签名方案标准，第三项预计很快发布：

- [FIPS 204（ML-DSA）](https://csrc.nist.gov/pubs/fips/204/final)：于 2024 年 8 月最终确定
- [FIPS 205（SLH-DSA）](https://csrc.nist.gov/pubs/fips/205/final)：于 2024 年 8 月最终确定
- **FIPS 206（Falcon）**：预计于 2026 年发布（目前为草案状态）

对比评级综合考虑了实现成熟度、与标准的一致性以及文档的清晰程度。

#### 2.3.2 大小与性能影响 { #size-and-performance }

公钥和签名大小是各参数集下的平均值。它们会增大交易负载，进而影响费用和吞吐量。NIST 安全等级提供了一把统一的安全标尺，便于对不同签名方案进行同类比较。

- ECDSA 签名：约 64 字节
- ML-DSA 签名：约 3,000+ 字节
- WOTS+ 签名：约 2,100+ 字节

#### 2.3.3 零知识密码学注意事项 { #zero-knowledge }

> **重要提示**：某些系统（如 Zcash）被标记为具备“后量子零知识证明”能力，但这一说法需要进一步澄清。

虽然 Zcash 使用了先进的零知识证明（zk-SNARK），但其底层密码学原语仍然依赖椭圆曲线，因此容易受到量子攻击。真正的后量子零知识证明需要建立在基于哈希或其他抗量子基础之上，如 StarkNet 所使用的 zk-STARK。

注意核实零知识证明的实现采用的是后量子密码学原语，而不仅仅是兼容后量子的证明系统。

#### 2.3.4 四大关键攻击面 { #threat-model }

PQC 能力复选框明确展示了每种实现覆盖了以下四个关键攻击面中的哪些方面：

- **交易签名**：最直接的薄弱点
- **P2P 连接**：网络通信安全
- **共识机制**：区块验证密码学
- **零知识证明**：隐私保护计算

#### 2.3.5 迁移现实 { #migration }

仅通过保护交易签名，就可以降低量子技术带来的很大一部分破坏。然而，P2P、共识和零知识证明组件也存在薄弱点，有时需要从根本上改变系统架构。

像比特币这样继承自“量子计算机还只是纯粹科幻概念”时代密码学选择的区块链，与从一开始就按抗量子目标设计的区块链相比，存在更多安全缺口。

## 3. 区块链安全评估实用指南 { #assessment-guide }

### 3.1 尽职调查清单 { #due-diligence }

- 核实 PQC 实现已经投入生产环境，而不仅仅部署在测试网
- 确认参数集与已发布的规范一致
- 查找针对 PQC 实现开展的独立安全审计

### 3.2 标准时间表 { #standards-timeline }

- **FIPS 204（ML-DSA）**：于 2024 年 8 月最终确定
- **FIPS 205（SLH-DSA）**：于 2024 年 8 月最终确定
- **FIPS 206（Falcon）**：预计于 2026 年发布（目前为草案状态）
- **迁移期限**：许多组织计划在 2030 年前全面实现量子就绪

### 3.3 需要警惕的危险信号 { #red-flags }

- **模糊声明**：只宣称“抗量子”，却没有提供具体实现细节
- **非标准方案**：使用专有算法或未明确说明的算法
- **覆盖不完整**：只保护签名，却忽略 P2P 和共识机制
- **没有时间表**：路线图中缺少具体的交付日期

## 参考资料 { #references }

<a id="ref-quantum-canary"></a>
\[1\] [Quantum Canary：Is Your Blockchain Quantum-Ready?](https://www.quantumcanary.org/is-your-blockchain-quantum-ready)（2026-08-24 整理）。
