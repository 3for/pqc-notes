/* Merkle authentication only. Fixed strings stand in for public keys; no OTS is generated. */
(() => {
  let nextId = 0;

  function element(tag, className = "", text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function hex(bytes) {
    return Array.from(bytes, (byte) => byte.toString(16).padStart(2, "0")).join("");
  }

  async function hash(prefix, ...parts) {
    const input = new Uint8Array(1 + parts.reduce((length, part) => length + part.length, 0));
    input[0] = prefix;
    let offset = 1;
    parts.forEach((part) => {
      input.set(part, offset);
      offset += part.length;
    });
    return new Uint8Array(await crypto.subtle.digest("SHA-256", input));
  }

  function showDigest(node, bytes) {
    const full = hex(bytes);
    node.textContent = full.slice(0, 8);
    node.title = full;
  }

  async function build(root) {
    const id = `mss-demo-${++nextId}`;
    const encoder = new TextEncoder();
    const leaves = await Promise.all(Array.from({ length: 4 }, (_, index) =>
      hash(0x00, encoder.encode(`MSS demo public key ${index}`))));
    const parents = await Promise.all([
      hash(0x01, leaves[0], leaves[1]),
      hash(0x01, leaves[2], leaves[3]),
    ]);
    const trustedRoot = await hash(0x01, parents[0], parents[1]);
    const values = { Root: trustedRoot, P0: parents[0], P1: parents[1] };
    leaves.forEach((value, index) => { values[`L${index}`] = value; });
    let selected = 2;
    let revision = 0;

    const title = element("p", "mss-demo__title", "交互演示：用两个认证节点重建四叶子树的根");
    title.id = `${id}-title`;
    root.setAttribute("role", "group");
    root.setAttribute("aria-labelledby", title.id);
    const hint = element("p", "mss-demo__hint", "选择一个叶子，观察从该叶子到根的重建路径，以及需要提供的两个兄弟节点。");
    const choices = element("div", "mss-demo__choices");
    choices.setAttribute("role", "group");
    choices.setAttribute("aria-label", "选择要认证的叶子");
    const buttons = leaves.map((_, index) => {
      const button = element("button", "mss-demo__leaf-button", `叶子 ${index}`);
      button.type = "button";
      button.dataset.mssLeaf = index;
      button.addEventListener("click", () => {
        selected = index;
        render().catch(disable);
      });
      choices.append(button);
      return button;
    });

    const tree = element("div", "mss-demo__tree");
    tree.setAttribute("role", "group");
    tree.setAttribute("aria-label", "原始 Merkle 公钥树，根和节点值保持固定");
    const svgNS = "http://www.w3.org/2000/svg";
    const connectors = document.createElementNS(svgNS, "svg");
    connectors.setAttribute("viewBox", "0 0 400 360");
    connectors.setAttribute("preserveAspectRatio", "none");
    connectors.setAttribute("aria-hidden", "true");
    connectors.classList.add("mss-demo__connectors");
    ["M200 100 L100 130", "M200 100 L300 130", "M100 230 L50 260",
      "M100 230 L150 260", "M300 230 L250 260", "M300 230 L350 260"].forEach((d) => {
      const path = document.createElementNS(svgNS, "path");
      path.setAttribute("d", d);
      connectors.append(path);
    });
    tree.append(connectors);
    const nodes = Object.entries(values).map(([name, value]) => {
      const node = element("div", "mss-demo__node");
      node.dataset.mssNode = name;
      const digest = element("code", "mss-demo__digest");
      showDigest(digest, value);
      const role = element("span", "mss-demo__node-role");
      node.append(element("strong", "", name), digest, role);
      tree.append(node);
      return { name, node, role };
    });

    const legend = element("p", "mss-demo__hint", "实线框：重建路径；虚线框：认证节点。树上显示原始节点，下方显示实际传入的认证值。哈希仅显示前 8 个十六进制字符，悬停可查看完整值。");
    const toggle = element("label", "mss-demo__tamper-label");
    const tamper = element("input");
    tamper.type = "checkbox";
    tamper.dataset.mssTamper = "";
    toggle.append(tamper, element("span", "", "篡改第一个认证节点 auth[0]（翻转首字节的一位）"));
    tamper.addEventListener("change", () => { render().catch(disable); });

    const proof = element("div", "mss-demo__proof");
    const proofTitle = element("p", "mss-demo__section-title", "传入的认证路径（从叶子向上）");
    const authentication = element("div", "mss-demo__authentication");
    const authNodes = [0, 1].map((level) => {
      const item = element("div", "mss-demo__auth-item");
      const label = element("span");
      const digest = element("code", "mss-demo__digest");
      digest.dataset.mssAuth = level;
      item.append(label, digest);
      authentication.append(item);
      return { label, digest };
    });
    const steps = element("ol", "mss-demo__steps");
    const stepNodes = [0, 1].map((level) => {
      const item = element("li");
      item.dataset.mssStep = level;
      const formula = element("span", "mss-demo__formula");
      const digest = element("code", "mss-demo__digest");
      digest.dataset.mssStepHash = level;
      item.append(formula, element("span", "", " = "), digest);
      steps.append(item);
      return { item, formula, digest };
    });
    proof.append(proofTitle, authentication, steps);

    const summary = element("div", "mss-demo__summary");
    summary.setAttribute("role", "status");
    summary.setAttribute("aria-live", "polite");
    summary.setAttribute("aria-atomic", "true");
    const result = element("p", "mss-demo__result");
    result.dataset.mssResult = "";
    const expectedLine = element("div", "", "可信根：");
    const expected = element("code", "mss-demo__digest");
    expected.dataset.mssExpectedRoot = "";
    showDigest(expected, trustedRoot);
    expectedLine.append(expected);
    const computedLine = element("div", "", "重建根：");
    const computed = element("code", "mss-demo__digest");
    computed.dataset.mssComputedRoot = "";
    computedLine.append(computed);
    summary.append(result, expectedLine, computedLine);
    const note = element("p", "mss-demo__hint", "使用 SHA-256：叶子为 H(0x00 ∥ UTF-8 演示公钥字符串)，父节点为 H(0x01 ∥ 左侧 32 字节 ∥ 右侧 32 字节)。校验比较完整 256-bit 根值。本演示只验证集合成员关系，不生成或验证 OTS 签名，也不演示密钥使用状态。");

    function disable() {
      revision += 1;
      root.hidden = true;
      root.dataset.initialized = "unavailable";
      root.removeAttribute("aria-busy");
      root.replaceChildren();
    }

    async function render() {
      const current = ++revision;
      const leafIndex = selected;
      const changed = tamper.checked;
      const parentIndex = Math.floor(leafIndex / 2);
      const siblingIndex = leafIndex ^ 1;
      const siblingParent = parentIndex ^ 1;
      const firstAuth = leaves[siblingIndex].slice();
      if (changed) firstAuth[0] ^= 1;
      root.setAttribute("aria-busy", "true");
      const reconstructedParent = leafIndex % 2 === 0
        ? await hash(0x01, leaves[leafIndex], firstAuth)
        : await hash(0x01, firstAuth, leaves[leafIndex]);
      const reconstructedRoot = parentIndex === 0
        ? await hash(0x01, reconstructedParent, parents[siblingParent])
        : await hash(0x01, parents[siblingParent], reconstructedParent);
      if (current !== revision) return;

      root.dataset.selectedLeaf = leafIndex;
      root.dataset.tampered = String(changed);
      buttons.forEach((button, index) => button.setAttribute("aria-pressed", String(index === leafIndex)));
      nodes.forEach(({ name, node, role }) => {
        const isAuth = name === `L${siblingIndex}` || name === `P${siblingParent}`;
        const isPath = name === "Root" || name === `P${parentIndex}` || name === `L${leafIndex}`;
        node.dataset.role = isAuth ? "authentication" : isPath ? "path" : "other";
        role.textContent = name === "Root" ? "可信根" : name === `L${leafIndex}` ? "当前叶子"
          : isAuth ? "认证节点" : isPath ? "重建路径" : "树节点";
      });
      authNodes[0].label.textContent = `auth[0] = L${siblingIndex}${changed ? "（已篡改）" : ""}`;
      authNodes[1].label.textContent = `auth[1] = P${siblingParent}`;
      showDigest(authNodes[0].digest, firstAuth);
      showDigest(authNodes[1].digest, parents[siblingParent]);
      const leafNames = [`L${2 * parentIndex}`, `L${2 * parentIndex + 1}`];
      if (changed) leafNames[leafIndex % 2 === 0 ? 1 : 0] += "*";
      stepNodes[0].formula.textContent = `P${parentIndex}′ = H(0x01 ∥ ${leafNames[0]} ∥ ${leafNames[1]})`;
      stepNodes[0].item.dataset.order = `${leafNames[0]},${leafNames[1]}`;
      const parentNames = parentIndex === 0 ? ["P0′", "P1"] : ["P0", "P1′"];
      stepNodes[1].formula.textContent = `Root′ = H(0x01 ∥ ${parentNames[0]} ∥ ${parentNames[1]})`;
      stepNodes[1].item.dataset.order = parentNames.join(",");
      showDigest(stepNodes[0].digest, reconstructedParent);
      showDigest(stepNodes[1].digest, reconstructedRoot);
      showDigest(computed, reconstructedRoot);
      const valid = hex(reconstructedRoot) === hex(trustedRoot);
      result.dataset.valid = String(valid);
      result.textContent = valid ? `✓ 叶子 ${leafIndex} 认证通过：重建根与可信根一致。`
        : `✗ 叶子 ${leafIndex} 认证失败：认证节点被修改，重建根与可信根不同。`;
      root.removeAttribute("aria-busy");
    }

    root.replaceChildren(title, hint, choices, tree, legend, toggle, proof, summary, note);
    await render();
  }

  function initialize() {
    if (!globalThis.crypto?.subtle || typeof TextEncoder === "undefined") return;
    document.querySelectorAll("[data-mss-demo]").forEach((root) => {
      if (root.dataset.initialized) return;
      root.dataset.initialized = "pending";
      build(root).then(() => {
        root.dataset.initialized = "true";
        root.hidden = false;
      }).catch(() => {
        root.hidden = true;
        root.dataset.initialized = "unavailable";
        root.removeAttribute("aria-busy");
        root.replaceChildren();
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
