/* A selection diagram only: no real keys, hashes, or signatures are generated. */
(() => {
  let nextId = 0;

  function secretLabel(position, bit) {
    const label = document.createElement("span");
    label.append("sk");
    const subscript = document.createElement("sub");
    subscript.textContent = `${position},${bit}`;
    label.append(subscript);
    return label;
  }

  function initialize() {
    document.querySelectorAll("[data-lamport-demo]").forEach((root) => {
      if (root.dataset.initialized) return;

      const initial = [1, 0, 1, 0];
      const bits = [...initial];
      const titleId = `lamport-demo-title-${++nextId}`;
      const title = document.createElement("p");
      title.className = "lamport-demo__title";
      title.id = titleId;
      title.textContent = "交互演示：选择摘要的 bit，观察公开哪些秘密值";
      root.setAttribute("role", "group");
      root.setAttribute("aria-labelledby", titleId);

      const grid = document.createElement("div");
      grid.className = "lamport-demo__grid";
      const columns = bits.map((bit, index) => {
        const column = document.createElement("div");
        const label = document.createElement("div");
        label.className = "lamport-demo__bit-label";
        label.textContent = `Bit ${index + 1}`;

        const button = document.createElement("button");
        button.type = "button";
        button.className = "lamport-demo__bit";
        button.dataset.lamportBit = index;
        button.setAttribute("aria-label", `切换 Bit ${index + 1}`);
        button.addEventListener("click", () => {
          bits[index] = 1 - bits[index];
          render();
        });
        column.append(label, button);

        const secrets = [0, 1].map((value) => {
          const secret = document.createElement("div");
          secret.className = "lamport-demo__secret";
          const mark = document.createElement("span");
          secret.append(secretLabel(index + 1, value), mark);
          column.append(secret);
          return { secret, mark };
        });
        grid.append(column);
        return { button, secrets };
      });

      const hint = document.createElement("p");
      hint.className = "lamport-demo__hint";
      hint.textContent = "点击 bit 切换 0/1；带 ✓ 的秘密值组成当前签名。按钮也支持 Tab 聚焦后按空格或 Enter 切换。";

      const summary = document.createElement("div");
      summary.className = "lamport-demo__summary";
      summary.setAttribute("role", "status");
      summary.setAttribute("aria-live", "polite");
      summary.setAttribute("aria-atomic", "true");
      const digestLabel = document.createElement("div");
      digestLabel.textContent = "当前消息摘要";
      const digest = document.createElement("div");
      digest.className = "lamport-demo__digest";
      digest.dataset.lamportDigest = "";
      const signatureLine = document.createElement("div");
      const signature = document.createElement("span");
      signature.dataset.lamportSignature = "";
      signatureLine.append("签名 = ", signature);
      summary.append(digestLabel, digest, signatureLine);

      const reset = document.createElement("button");
      reset.type = "button";
      reset.className = "lamport-demo__reset";
      reset.dataset.lamportReset = "";
      reset.textContent = "重置为 1010";
      reset.addEventListener("click", () => {
        bits.splice(0, bits.length, ...initial);
        render();
      });

      const note = document.createElement("p");
      note.className = "lamport-demo__hint";
      note.textContent = "本演示仅展示秘密值的选择规则，不生成真实密钥或计算哈希。切换不会累计已公开的秘密值；真实 Lamport 密钥只能安全签署一条消息，重复使用的风险见第 5 节。";

      function render() {
        columns.forEach(({ button, secrets }, index) => {
          button.textContent = bits[index];
          button.setAttribute("aria-pressed", String(bits[index] === 1));
          secrets.forEach(({ secret, mark }, value) => {
            const selected = bits[index] === value;
            secret.dataset.selected = String(selected);
            mark.textContent = selected ? " ✓" : "";
          });
        });
        digest.textContent = bits.join("");
        signature.replaceChildren();
        bits.forEach((bit, index) => {
          if (index) signature.append(" ‖ ");
          signature.append(secretLabel(index + 1, bit));
        });
      }

      render();
      root.replaceChildren(title, grid, hint, summary, reset, note);
      root.dataset.initialized = "true";
      root.hidden = false;
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
  // Also initialize after page changes if instant navigation is enabled later.
  if (typeof document$ !== "undefined") document$.subscribe(initialize);
})();
