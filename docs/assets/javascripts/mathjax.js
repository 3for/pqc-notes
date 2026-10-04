/* Resolve against this file so root, nested pages and GitHub project paths work. */
(() => {
  const assets = new URL("../", document.currentScript.src);
  window.MathJax = {
    loader: {
      paths: { mathjax: new URL("vendor/mathjax/", assets).href.replace(/\/$/, "") },
    },
    tex: {
      inlineMath: [["\\(", "\\)"]],
      displayMath: [["\\[", "\\]"]],
      processEscapes: true,
      processEnvironments: true,
      tags: "none",
    },
    options: {
      ignoreHtmlClass: ".*|",
      processHtmlClass: "arithmatex",
    },
    output: {
      font: "mathjax-newcm",
      fontPath: new URL("vendor/mathjax-newcm-font", assets).href,
      mtextInheritFont: true,
    },
  };
})();

