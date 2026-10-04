# PQC 学习笔记

用 Zensical 和 MathJax 发布后量子密码学学习笔记，包含中文搜索、章节目录、公式、脚注和原文 PDF 下载。

当前长文是《基础格密码学：Kyber（ML-KEM）与 Dilithium（ML-DSA）背后的概念》的中文学习笔记；原文作者为 Vadim Lyubashevsky，署名保留在正文中。

## 本地预览

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，在仓库根目录执行：

```bash
uv sync --frozen
uv run zensical serve
```

访问终端显示的本地地址（默认 `http://127.0.0.1:8000`）。依赖版本由 `uv.lock` 固定，Python 要求为 3.12 或以上。

## 内容维护

- `docs/index.md`：网站首页。
- `docs/basic-lattice-cryptography-notes-zh.md`：笔记正文。
- `docs/basic-lattice-cryptography-2024-1287.pdf`：原文 PDF。
- `docs/output/`：正文图片，保留 Markdown 中的相对引用路径。
- `zensical.toml`：站点、导航和 Markdown 配置。

新增笔记时放入 `docs/`，并更新 `zensical.toml` 的导航。直接维护这一份正文即可。构建结果保存在 `site/`，无需提交。

## 检查样页

```bash
uv run zensical build --clean
uv run python scripts/check_site.py
```

浏览器检查会优先使用 macOS 上已安装的 Chrome；其他环境先安装 Chromium：

```bash
uv run playwright install chromium
uv run python scripts/check_browser.py
```

浏览器脚本会启动临时本地服务，模拟 `/pqc-notes/` 部署路径，阻止外部请求并验证公式、脚注往返、图片、中文搜索及手机宽度。可用 `PQC_BROWSER_EXECUTABLE` 指定浏览器路径；加上 `--screenshots .cache/preview` 可保存截图。

数学排版使用站内托管的 MathJax 4，支持正文中的 `array` 列间距语法。脚本及字体在 `docs/assets/vendor/`，不依赖外部 CDN；来源、版本与许可见该目录的 `README.txt`，需要重新下载时运行 `python3 scripts/vendor_mathjax.py`。

人工预览时可搜索“数论变换”“高斯消元”“拒绝采样”，再检查矩阵、带编号公式、表格和窄屏长公式的显示。

正文保留整篇长文，PDF 页码目录已由网页章节目录替代。书写块公式时，`$$` 前后留空行、块内避免空行，静态检查会核对所有块公式是否被正确识别。当前关闭了 Zensical 的正文搜索高亮，避免它替换 MathJax 正在处理的文本；搜索结果高亮和章节跳转仍然可用。

## GitHub Pages 自动发布

已提供 [发布工作流](.github/workflows/pages.yml)。首次发布前，在 GitHub 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**；操作说明见 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

提交并推送到 `main` 后，工作流会安装锁定依赖、构建、检查并部署；Pull Request 只执行构建和静态检查。在 Actions 中也可手动运行 `Build and publish notes`，选择 `main` 分支发布。

按当前仓库地址，预期网站地址为 <https://3for.github.io/pqc-notes/>。这是发布后的地址；以 Actions 部署结果为准。

浏览器检查目前作为本地验证运行，不包含在自动发布工作流中。工作流使用 GitHub 官方 Pages Actions，发布不需要单独保存个人访问令牌；参见 [自定义 Pages 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。
