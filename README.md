# PQC Notes

**Deep dives into post-quantum cryptography — from papers and standards to real-world implementations.**

深入探索后量子密码，连接论文中的思想与安全论证、标准中的算法与约束，以及实际实现中的工程取舍。内容以中文为主，面向具备密码学基础的学习者、研究者与开发者。

[在线阅读](https://3for.github.io/pqc-notes/) · [内容源码](docs/) · [提问与勘误](https://github.com/3for/pqc-notes/issues) · [参与贡献](CONTRIBUTING.md)

## 内容方向

项目围绕以下三个方向持续积累专题，选题可以从一个理论问题、一条标准要求或一个实现细节出发。

| 方向 | 关注的问题 |
| --- | --- |
| **论文精读 · Papers** | 构造为什么成立？依赖哪些安全假设？证明和推导中省略了哪些关键步骤？ |
| **标准解读 · Standards** | 算法、参数、接口和编码有哪些具体要求？不同版本有哪些变化？规范与论文构造如何对应？ |
| **实现研究 · Implementations** | 算法如何落到代码、库与协议中？如何验证正确性、复现实验，并理解性能、内存与实现安全之间的取舍？ |

希望通过这些专题把原理、规范和实现行为联系起来：推导有来源可核对，实验有步骤可复现，结论注明版本、前提与适用范围。下方列出目前已有的内容，其余方向欢迎共同建设。

## 当前内容

### 基础格密码学

本专题以 Vadim Lyubashevsky 的 [*Basic Lattice Cryptography: The concepts behind Kyber (ML-KEM) and Dilithium (ML-DSA)*](https://eprint.iacr.org/2024/1287.pdf) 为基础，对应原文 2025 年 6 月 18 日版本。正文按原文顺序整理，附录补充学习过程中需要展开的推导。

阅读路线为 **LWE / SIS → 格与多项式环 → ML-KEM / ML-DSA**。本专题建议具备线性代数、模运算和公钥加密的基础，并了解 CPA / CCA 安全及混合论证；熟悉 ElGamal 和 Schnorr 会更容易建立类比。

| 想解决的问题 | 阅读入口 |
| --- | --- |
| 系统理解 LWE、格、多项式环及加密和签名构造 | [基础格密码学笔记](https://3for.github.io/pqc-notes/basic-lattice-cryptography-notes-zh/) |
| 引例中的安全性论证为什么需要两次不可区分性替换？ | [附录 A：混合论证](https://3for.github.io/pqc-notes/basic-lattice-cryptography-notes-zh/#a) |
| 为什么多项式相乘可以计算独立误差之和的分布？ | [附录 B：误差分布与生成函数](https://3for.github.io/pqc-notes/basic-lattice-cryptography-notes-zh/#b) |
| 环上的多项式乘法怎样变成矩阵乘法？ | [附录 C：矩阵表示](https://3for.github.io/pqc-notes/basic-lattice-cryptography-notes-zh/#c) |

本专题支持中文搜索，以及章节、公式、参考文献、附录和脚注之间的跳转。阅读时可以沿专题路线学习，也可以从一个具体问题进入，再回到原文核对。

## 参与贡献

欢迎完善现有内容，也欢迎围绕其他 PQC 算法、标准和实现提出独立专题。每篇内容围绕一个清楚的问题展开，并提供读者能够继续核对和探索的线索。

欢迎从小问题开始参与：

- **提问或勘误**：附上章节、公式或段落位置，说明哪里看不懂、哪里可能有误。无需先搭建本地环境。
- **论文研读与推导**：分析构造或安全论证，展开省略的步骤，补充可手算的例子和图示。
- **标准分析**：解读具体条款、参数与接口，梳理版本变化及其与论文或实现的关系。
- **实现分析与复现实验**：解读源码，核验测试向量，复现性能结果，或记录库与协议集成中的问题；注明实现版本、运行环境和验证方法。
- **核对与校对**：检查译法、符号、推导、来源和实验结果。
- **改进阅读体验**：修复导航、公式显示、搜索或手机布局问题。

具体做法见[贡献指南](CONTRIBUTING.md)。小勘误可以直接发 Issue 或 PR；新增长篇内容或调整组织方式时，先在 Issue 中说明读者问题和提纲，便于讨论范围。

## 本地预览

需要 Python 3.12 或以上，以及 [uv](https://docs.astral.sh/uv/getting-started/installation/)。在仓库根目录执行：

```bash
uv sync --frozen
uv run --frozen zensical serve
```

访问终端显示的地址，默认是 `http://127.0.0.1:8000`。依赖版本记录在 `uv.lock` 中；准备提交 PR 时，请参考贡献指南中的 Fork 与分支流程。

## 提交前检查

先构建，再检查生成页面：

```bash
uv run --frozen zensical build --clean
uv run --frozen python scripts/check_site.py
```

静态检查会核对站内链接及锚点，并检查当前长文的公式标记和脚注。涉及公式、页面样式或交互时，再运行浏览器检查：

```bash
uv run --frozen playwright install chromium
uv run --frozen python scripts/check_browser.py
```

已安装 Google Chrome 的 macOS 环境可以省略 Chromium 安装步骤。浏览器检查覆盖当前长文的公式渲染、图片、脚注往返、中文搜索和手机宽度；它目前在本地运行，未接入 CI。检查范围及注意事项见[贡献指南](CONTRIBUTING.md)。

## GitHub Pages 发布

站点使用 Zensical 和 MathJax 构建，由[发布工作流](.github/workflows/pages.yml)自动发布：

- **提交到 `main` 的 PR**：构建并执行静态检查。
- **推送或合并到 `main`**：检查通过后部署到 GitHub Pages。
- **手动发布**：在 Actions 中选择 `Build and publish notes`，通过 `Run workflow` 在 `main` 分支运行。

首次配置仓库时，在 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。Fork 后自行发布，还需将 `zensical.toml` 中的站点地址和仓库信息改为自己的配置。详见 [GitHub Pages 发布源说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 仓库结构

| 路径 | 用途 |
| --- | --- |
| `docs/` | 各专题文档与站点内容 |
| `docs/index.md` | 网站首页与阅读入口 |
| `docs/basic-lattice-cryptography-notes-zh.md` | 基础格密码学专题及补充推导 |
| `docs/basic-lattice-cryptography-2024-1287.pdf` | 基础格密码学专题对应的英文原文 |
| `docs/output/` | 正文引用的图片 |
| `docs/assets/`、`overrides/` | 网站样式、水印、本地数学资源与模板 |
| `zensical.toml` | 站点信息、导航、署名与 GitHub 链接 |
| `scripts/` | 构建结果检查、浏览器检查和数学资源维护 |
| `.github/workflows/pages.yml` | 自动检查与发布 |

站点内容维护以 `docs/` 中的源文件为准；`site/`、`.venv/` 和 `.cache/` 是生成目录，不提交到仓库。

## 来源与署名

论文、标准和实现分析均应保留原作者或项目的来源信息，并注明对应版本。中文整理、补充推导及实验结果应清楚标注；新增内容请注明撰写或整理者、参考来源和核验方式，校对贡献可在 PR 中记录覆盖范围。

仓库尚未为原创文档及代码确定统一许可证；论文、图片和第三方依赖的来源与许可需分别保留。MathJax 及字体的许可记录见 [vendor 说明](docs/assets/vendor/README.txt)。
