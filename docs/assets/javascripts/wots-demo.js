/* Teaching diagrams only: these widgets do not generate keys or compute hashes. */
(() => {
  let nextId = 0;

  function createElement(tag, className = "", text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function chainValue(index) {
    const value = createElement("span", "wots-demo__chain-value", "x");
    value.append(createElement("sub", "", index));
    return value;
  }

  function prepareRoot(root, titleText) {
    const title = createElement("p", "wots-demo__title", titleText);
    title.id = `wots-demo-title-${++nextId}`;
    root.setAttribute("role", "group");
    root.setAttribute("aria-labelledby", title.id);
    root.replaceChildren(title);
    return title;
  }

  function metric(label, attribute) {
    const item = createElement("div", "wots-demo__metric");
    const value = createElement("span", "wots-demo__value");
    value.setAttribute(attribute, "");
    item.append(createElement("div", "", label), value);
    return { item, value };
  }

  function buildChain(root) {
    const title = prepareRoot(root, "交互演示：一条哈希链如何分配签名和验签的计算");
    const field = createElement("div", "wots-demo__field");
    const label = createElement("label", "", "选择需要签署的数字（0–15）");
    const slider = createElement("input");
    slider.type = "range";
    slider.min = "0";
    slider.max = "15";
    slider.step = "1";
    slider.value = "6";
    slider.id = `${title.id}-digit`;
    slider.dataset.wotsDigit = "";
    label.htmlFor = slider.id;
    field.append(label, slider);

    const legend = createElement("p", "wots-demo__hint",
      "已计算 → 公开签名 ✓ → 待验签；每个箭头表示一次哈希。可拖动滑块或使用方向键，小屏可左右滑动查看完整链。");
    const scroll = createElement("div", "wots-demo__chain-scroll");
    scroll.tabIndex = 0;
    scroll.setAttribute("role", "region");
    scroll.setAttribute("aria-label", "哈希链，从私钥 x0 到公钥 x15，可左右滚动");
    const chain = createElement("div", "wots-demo__chain");
    const nodes = Array.from({ length: 16 }, (_, index) => {
      const node = createElement("div", "wots-demo__node");
      node.dataset.wotsNode = index;
      const position = index === 0 ? "私钥起点" : index === 15 ? "公钥终点" : `位置 ${index}`;
      const state = createElement("span", "wots-demo__node-state");
      node.append(chainValue(index), createElement("span", "wots-demo__node-role", position), state);
      chain.append(node);
      return { node, state };
    });
    scroll.append(chain);

    const summary = createElement("div", "wots-demo__summary");
    summary.setAttribute("role", "status");
    summary.setAttribute("aria-live", "polite");
    summary.setAttribute("aria-atomic", "true");
    const metrics = createElement("div", "wots-demo__metrics");
    const signing = metric("签名者计算（次）", "data-wots-sign-steps");
    const verifying = metric("验证者继续计算（次）", "data-wots-verify-steps");
    metrics.append(signing.item, verifying.item);
    const signatureLine = createElement("div", "wots-demo__signature", "公开的签名值：");
    const signature = createElement("span");
    signature.dataset.wotsChainSignature = "";
    signatureLine.append(signature);
    summary.append(metrics, signatureLine);

    const reset = createElement("button", "wots-demo__reset", "重置为 6");
    reset.type = "button";
    reset.dataset.wotsChainReset = "";
    const note = createElement("p", "wots-demo__hint",
      "这是链位置示意，不生成真实密钥或计算哈希。签名与验签的链哈希次数合计为 15；每次切换只展示一种签名选择，WOTS 密钥仍然只能安全签署一条消息。");

    function centerSelected() {
      const selected = nodes[Number(slider.value)].node;
      scroll.scrollLeft = selected.offsetLeft - (scroll.clientWidth - selected.offsetWidth) / 2;
    }

    function render() {
      const digit = Number(slider.value);
      slider.setAttribute("aria-valuetext", `数字 ${digit}，签名计算 ${digit} 次，验签计算 ${15 - digit} 次`);
      signing.value.textContent = digit;
      verifying.value.textContent = 15 - digit;
      signature.replaceChildren(chainValue(digit));
      nodes.forEach(({ node, state }, index) => {
        node.dataset.stage = index < digit ? "sign" : index === digit ? "signature" : "verify";
        state.textContent = index < digit ? "已计算" : index === digit ? "公开 ✓" : "待验签";
      });
    }

    slider.addEventListener("input", () => {
      render();
      centerSelected();
    });
    reset.addEventListener("click", () => {
      slider.value = "6";
      render();
      centerSelected();
    });
    root.append(field, legend, scroll, summary, reset, note);
    render();
    requestAnimationFrame(centerSelected);
  }

  function parameterStats(w) {
    const messageChains = Math.ceil(256 / Math.log2(w));
    let checksumChains = 1;
    let capacity = w;
    const checksumMax = messageChains * (w - 1);
    while (capacity <= checksumMax) {
      checksumChains += 1;
      capacity *= w;
    }
    const totalChains = messageChains + checksumChains;
    return { messageChains, checksumChains, totalChains,
      signatureBytes: totalChains * 32, totalSteps: totalChains * (w - 1) };
  }

  function buildParameters(root) {
    const title = prepareRoot(root, "交互演示：签名大小与哈希计算量的权衡");
    const controls = createElement("div", "wots-demo__controls");
    const label = createElement("label", "", "Winternitz 参数 w");
    const select = createElement("select");
    select.id = `${title.id}-parameter`;
    select.dataset.wotsParameter = "";
    label.htmlFor = select.id;
    const parameters = [4, 16, 256];
    parameters.forEach((w) => {
      const option = createElement("option", "", w);
      option.value = w;
      select.append(option);
    });
    select.value = "16";
    controls.append(label, select);

    const summary = createElement("div", "wots-demo__summary");
    summary.setAttribute("role", "status");
    summary.setAttribute("aria-live", "polite");
    summary.setAttribute("aria-atomic", "true");
    const metrics = createElement("div", "wots-demo__metrics");
    const outputs = [
      ["消息链数", "messageChains", "data-wots-message-chains"],
      ["Checksum 链数", "checksumChains", "data-wots-checksum-chains"],
      ["总链数", "totalChains", "data-wots-total-chains"],
      ["签名大小（B）", "signatureBytes", "data-wots-signature-bytes"],
      ["签名＋验签链哈希（次）", "totalSteps", "data-wots-total-steps"],
    ].map(([labelText, key, attribute]) => {
      const output = metric(labelText, attribute);
      metrics.append(output.item);
      return { key, value: output.value };
    });
    const stepsFormula = createElement("p", "wots-demo__hint",
      "签名＋验签链哈希（次）= 总链数 × (w − 1)。");
    const calculation = createElement("span");
    calculation.dataset.wotsStepsCalculation = "";
    stepsFormula.append(createElement("br"), calculation);
    summary.append(metrics, stepsFormula);

    const chart = createElement("div", "wots-demo__chart");
    chart.setAttribute("role", "group");
    chart.setAttribute("aria-label", "三种参数的签名大小对比，单位字节");
    const maximum = Math.max(...parameters.map((w) => parameterStats(w).signatureBytes));
    const bars = parameters.map((w) => {
      const bytes = parameterStats(w).signatureBytes;
      const row = createElement("div", "wots-demo__bar-row");
      row.dataset.wotsBar = w;
      const label = createElement("span", "wots-demo__bar-label", `w = ${w}`);
      const track = createElement("div", "wots-demo__bar-track");
      const bar = createElement("div", "wots-demo__bar");
      bar.style.width = `${100 * bytes / maximum}%`;
      bar.setAttribute("aria-hidden", "true");
      track.append(bar);
      row.append(label, track, createElement("span", "wots-demo__bar-number", `${bytes} B`));
      chart.append(row);
      return { w, row };
    });
    const note = createElement("p", "wots-demo__hint",
      "固定使用 256-bit 摘要、32 B 签名元素和固定长度 Base-w Checksum。步数只统计签名与验签的链哈希，不包括消息摘要、密钥生成及封装开销。");

    function render() {
      const w = Number(select.value);
      const stats = parameterStats(w);
      outputs.forEach(({ key, value }) => { value.textContent = stats[key]; });
      calculation.textContent = `当前参数：${stats.totalChains} × (${w} − 1) = ${stats.totalSteps} 次。`;
      bars.forEach(({ w: parameter, row }) => {
        row.dataset.selected = String(parameter === w);
      });
    }

    select.addEventListener("change", render);
    root.append(controls, summary, createElement("p", "wots-demo__chart-title", "签名大小对比"), chart, note);
    render();
  }

  function buildChecksum(root) {
    prepareRoot(root, "交互演示：修改摘要，观察 Checksum 如何阻止链推进");
    const source = [10, 11, 12, 13, 0, 14];
    const hint = createElement("p", "wots-demo__hint", "已有签名的摘要为 ABCD，Checksum 为 0E。输入另一个 4 位十六进制摘要，比较六条链需要移动的方向。");
    const controls = createElement("div", "wots-demo__controls wots-demo__checksum-controls");
    const field = createElement("label", "", "目标摘要（4 位十六进制）");
    const target = createElement("input");
    target.id = `${root.getAttribute("aria-labelledby")}-target`;
    field.htmlFor = target.id;
    target.type = "text";
    target.value = "ABCE";
    target.maxLength = 4;
    target.autocomplete = "off";
    target.spellcheck = false;
    target.setAttribute("autocapitalize", "characters");
    target.dataset.wotsTarget = "";
    const reset = createElement("button", "wots-demo__reset", "重置为 ABCE");
    reset.type = "button";
    reset.dataset.wotsChecksumReset = "";
    const controlRow = createElement("div", "wots-demo__checksum-row");
    controlRow.append(target, reset);
    controls.append(field, controlRow);

    const error = createElement("p", "wots-demo__error", "请输入恰好 4 位十六进制数字（0–9、A–F），例如 ABCE。");
    error.id = `${root.getAttribute("aria-labelledby")}-error`;
    error.dataset.wotsChecksumError = "";
    error.setAttribute("role", "alert");
    error.hidden = true;
    target.setAttribute("aria-describedby", error.id);

    const result = createElement("div");
    result.dataset.wotsChecksumResult = "";
    const summary = createElement("div", "wots-demo__summary");
    summary.setAttribute("role", "status");
    summary.setAttribute("aria-live", "polite");
    summary.setAttribute("aria-atomic", "true");
    const checksumLine = createElement("div");
    const checksumValue = createElement("strong");
    checksumValue.dataset.wotsChecksumValue = "";
    checksumLine.append("目标 Checksum = ", checksumValue);
    const status = createElement("p", "wots-demo__attack-status");
    status.dataset.wotsAttackStatus = "";
    summary.append(checksumLine, status);

    const tableTitle = createElement("p", "wots-demo__table-title", "各链的位置变化：原签名 → 目标签名");
    tableTitle.id = `${root.getAttribute("aria-labelledby")}-comparison`;
    const table = createElement("table", "wots-demo__comparison");
    table.setAttribute("aria-labelledby", tableTitle.id);
    const header = createElement("thead");
    const headerRow = createElement("tr");
    ["哈希链", "原位置", "目标位置", "所需操作"].forEach((text) => {
      const cell = createElement("th", "", text);
      cell.scope = "col";
      headerRow.append(cell);
    });
    header.append(headerRow);
    const body = createElement("tbody");
    const rows = source.map((_, index) => {
      const row = createElement("tr");
      row.dataset.wotsComparisonRow = "";
      const label = createElement("th", "", index < 4 ? `消息 ${index + 1}` : `校验 ${index - 3}`);
      label.scope = "row";
      const original = createElement("td", "", String(source[index]));
      const next = createElement("td");
      const operation = createElement("td");
      row.append(label, original, next, operation);
      body.append(row);
      return { row, next, operation };
    });
    table.append(header, body);
    const tableWrap = createElement("div", "wots-demo__table-wrap");
    tableWrap.append(table);
    result.append(summary, tableTitle, tableWrap);
    const note = createElement("p", "wots-demo__hint", "位置用十进制显示；Checksum 始终用两位十六进制表示。向前移动可以继续哈希；向后移动无法仅靠继续哈希完成。这里直接比较摘要数字，不生成真实签名，也不搜索产生目标摘要的消息。WOTS 密钥仍只能安全签署一条消息。");

    function render() {
      const value = target.value.toUpperCase();
      const valid = /^[0-9A-F]{4}$/.test(value);
      target.setAttribute("aria-invalid", String(!valid));
      error.hidden = valid;
      result.hidden = !valid;
      if (!valid) return;

      const digits = Array.from(value, (digit) => parseInt(digit, 16));
      const checksum = digits.reduce((sum, digit) => sum + 15 - digit, 0);
      const encoded = checksum.toString(16).toUpperCase().padStart(2, "0");
      const allDigits = [...digits, ...Array.from(encoded, (digit) => parseInt(digit, 16))];
      checksumValue.textContent = encoded;
      rows.forEach(({ row, next, operation }, index) => {
        const delta = allDigits[index] - source[index];
        row.dataset.direction = delta < 0 ? "backward" : delta > 0 ? "forward" : "same";
        next.textContent = allDigits[index];
        operation.textContent = delta < 0 ? `需后退 ${-delta} 步` : delta > 0 ? `向前哈希 ${delta} 次` : "直接复用";
      });
      const unchanged = value === "ABCD";
      const messageBackwards = digits.some((digit, index) => digit < source[index]);
      status.dataset.result = unchanged ? "unchanged" : "blocked";
      status.textContent = unchanged
        ? "摘要未改变：所有链的位置相同，这不是对新摘要的伪造。"
        : messageBackwards
          ? "无法仅靠向前哈希构造：至少一条消息链需要后退。"
          : "无法仅靠向前哈希构造：消息数字增加使 Checksum 减小，至少一条校验链需要后退。";
    }

    target.addEventListener("input", render);
    reset.addEventListener("click", () => {
      target.value = "ABCE";
      render();
    });
    root.append(hint, controls, error, result, note);
    render();
  }

  function initialize() {
    [
      ["[data-wots-chain-demo]", buildChain],
      ["[data-wots-parameter-demo]", buildParameters],
      ["[data-wots-checksum-demo]", buildChecksum],
    ].forEach(([selector, build]) => {
      document.querySelectorAll(selector).forEach((root) => {
        if (root.dataset.initialized) return;
        build(root);
        root.dataset.initialized = "true";
        root.hidden = false;
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
  if (typeof document$ !== "undefined") document$.subscribe(initialize);
})();
