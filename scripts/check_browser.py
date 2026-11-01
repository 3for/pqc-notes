"""Exercise the real built site under the GitHub Pages project prefix, offline."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import unquote, urlsplit
import argparse
import hashlib
import json
import os
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = "basic-lattice-cryptography-notes-zh"
BLOCKCHAIN = "blockchain/pqc-migration"
LAMPORT = "hash-based-pqc/lamport"
WOTS = "hash-based-pqc/WOTS"
MSS = "hash-based-pqc/MSS"
PREFIX = "/pqc-notes/"


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = "/" + path[len(PREFIX):]
        return super().translate_path(path)

    def log_message(self, *_args):
        pass


def check_math(page, minimum=101):
    page.wait_for_function("window.MathJax?.startup?.promise !== undefined")
    page.evaluate("async () => { await MathJax.startup.promise; await document.fonts.ready; }")
    errors = page.locator("mjx-merror, [data-mjx-error]")
    assert errors.count() == 0, errors.all_text_contents()
    assert page.locator(".arithmatex mjx-container").count() >= minimum
    missing = page.locator(".arithmatex").evaluate_all(
        "nodes => nodes.filter(n => !n.querySelector('mjx-container')).map(n => n.textContent.slice(0, 100))"
    )
    assert not missing, f"Unrendered math at {page.url}: {missing[:5]}"


def check_lamport(page, browser, base, screenshots, local_only):
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(base + LAMPORT + "/", wait_until="networkidle")
    check_math(page, minimum=29)
    demo = page.locator("[data-lamport-demo]")
    demo.wait_for(state="visible")
    buttons = [demo.locator(f"[data-lamport-bit='{i}']") for i in range(4)]

    def check_state(digest):
        assert demo.locator("[data-lamport-digest]").text_content().strip() == digest
        secrets = [f"sk{i + 1},{bit}" for i, bit in enumerate(digest)]
        assert demo.locator("[data-lamport-signature]").text_content().strip() == " ‖ ".join(secrets)
        selected = demo.locator(".lamport-demo__secret[data-selected='true']").all_text_contents()
        selected = [" ".join(text.split()) for text in selected]
        assert len(selected) == 4, selected
        for i, bit in enumerate(digest):
            assert buttons[i].get_attribute("aria-pressed") == str(bit == "1").lower()
            assert any(f"{secrets[i]} ✓" in text for text in selected), selected

    check_state("1010")
    for value in range(16):
        digest = f"{value:04b}"
        for i, bit in enumerate(digest):
            if buttons[i].get_attribute("aria-pressed") != str(bit == "1").lower():
                buttons[i].click()
        check_state(digest)

    demo.locator("[data-lamport-reset]").click()
    check_state("1010")
    buttons[0].focus()
    buttons[0].press("Space")
    check_state("0010")
    buttons[0].press("Enter")
    check_state("1010")
    if screenshots:
        demo.screenshot(path=str(screenshots / "lamport-desktop.png"))

    page.set_viewport_size({"width": 390, "height": 844})
    dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
    assert dimensions["page"] <= dimensions["viewport"] + 1, dimensions
    assert demo.evaluate("node => node.scrollWidth <= node.clientWidth + 1"), "Lamport demo overflows."
    buttons[3].click()
    check_state("1011")
    demo.locator("[data-lamport-reset]").click()
    check_state("1010")
    if screenshots:
        demo.screenshot(path=str(screenshots / "lamport-mobile.png"))

    scheme = page.locator("body").get_attribute("data-md-color-scheme")
    page.locator("body").evaluate("node => node.setAttribute('data-md-color-scheme', 'slate')")
    assert all(button.is_visible() for button in buttons)
    buttons[1].click()
    check_state("1110")
    demo.locator("[data-lamport-reset]").click()
    check_state("1010")
    if screenshots:
        demo.screenshot(path=str(screenshots / "lamport-dark.png"))
    page.locator("body").evaluate("(node, scheme) => node.setAttribute('data-md-color-scheme', scheme)", scheme)

    fallback_context = browser.new_context(java_script_enabled=False)
    try:
        fallback_context.route("**/*", local_only)
        fallback = fallback_context.new_page()
        response = fallback.goto(base + LAMPORT + "/", wait_until="networkidle")
        assert response.status == 200
        assert fallback.locator("[data-lamport-demo]").count() == 1
        assert fallback.locator("[data-lamport-demo]").is_hidden()
        assert fallback.locator("article table").first.is_visible()
        assert fallback.locator(".arithmatex").filter(has_text="H(M)=1010").is_visible()
        signature = fallback.locator(".arithmatex").filter(has_text=r"\sigma").filter(has_text="sk_{1,1}")
        assert signature.is_visible()
        assert all(secret in signature.text_content() for secret in ("sk_{2,0}", "sk_{3,1}", "sk_{4,0}"))
    finally:
        fallback_context.close()
    print("Lamport states, keyboard, reset, themes, mobile layout and no-JS fallback passed.", flush=True)
    return dimensions


def check_wots(page, browser, base, screenshots, local_only):
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(base + WOTS + "/", wait_until="networkidle")
    check_math(page, minimum=49)
    article = page.locator("article")
    assert article.locator("h1").count() == 1, "Demo values must not become article headings."
    headings = article.locator("h1, h2, h3, h4, h5, h6").evaluate_all(
        "nodes => nodes.map(n => ({level: Number(n.tagName.slice(1)), text: n.textContent.trim()}))"
    )
    for previous, current in zip(headings, headings[1:]):
        assert current["level"] <= previous["level"] + 1, headings
    assert not any(re.fullmatch(r"\d+(?:\s*次)?[¶\s]*", heading["text"]) for heading in headings), headings
    section_ids = set(article.locator("[id]").evaluate_all("nodes => nodes.map(n => n.id)"))
    section_links = page.locator("article a[href^='#'], .md-sidebar a[href^='#']").evaluate_all(
        "nodes => nodes.map(n => n.getAttribute('href')).filter(href => href.length > 1)"
    )
    assert section_links, "WOTS section links are missing."
    assert all(unquote(link[1:]) in section_ids for link in section_links), section_links
    article.locator("a[href='#checksum']").first.click()
    assert urlsplit(page.url).fragment == "checksum"

    chain = page.locator("[data-wots-chain-demo]")
    parameters = page.locator("[data-wots-parameter-demo]")
    checksum = page.locator("[data-wots-checksum-demo]")
    demos = [("chain", chain), ("parameters", parameters), ("checksum", checksum)]
    for _, demo in demos:
        demo.wait_for(state="visible")
    digit = chain.locator("[data-wots-digit]")

    def check_chain(value):
        assert digit.input_value() == str(value)
        assert chain.locator("[data-wots-sign-steps]").text_content().strip() == str(value)
        assert chain.locator("[data-wots-verify-steps]").text_content().strip() == str(15 - value)
        assert chain.locator("[data-wots-chain-signature]").text_content().strip() == f"x{value}"
        nodes = chain.locator("[data-wots-node]")
        assert nodes.count() == 16
        for index in range(16):
            expected = "sign" if index < value else "signature" if index == value else "verify"
            assert chain.locator(f"[data-wots-node='{index}']").get_attribute("data-stage") == expected

    check_chain(6)
    for value in range(16):
        digit.evaluate("(node, value) => { node.value = value; node.dispatchEvent(new Event('input', {bubbles: true})); }", str(value))
        check_chain(value)
    digit.press("Home")
    check_chain(0)
    digit.press("ArrowRight")
    check_chain(1)
    digit.press("End")
    check_chain(15)
    chain.locator("[data-wots-chain-reset]").click()
    check_chain(6)

    parameter = parameters.locator("[data-wots-parameter]")
    parameter_fields = ("message-chains", "checksum-chains", "total-chains", "signature-bytes", "total-steps")
    parameter_cases = {4: (128, 5, 133, 4256, 399), 16: (64, 3, 67, 2144, 1005), 256: (32, 2, 34, 1088, 8670)}

    def check_parameter(value):
        parameter.select_option(str(value))
        for field, expected in zip(parameter_fields, parameter_cases[value]):
            assert parameters.locator(f"[data-wots-{field}]").text_content().strip() == str(expected)

    assert parameter.input_value() == "16"
    for value in parameter_cases:
        check_parameter(value)
    check_parameter(16)

    target = checksum.locator("[data-wots-target]")
    cases = {
        "ABCE": ("0D", ["same", "same", "same", "forward", "same", "backward"]),
        "ABCD": ("0E", ["same"] * 6),
        "0000": ("3C", ["backward"] * 4 + ["forward", "backward"]),
        "FFFF": ("00", ["forward"] * 4 + ["same", "backward"]),
        "ABCC": ("0F", ["same", "same", "same", "backward", "same", "forward"]),
        "ABCB": ("10", ["same", "same", "same", "backward", "forward", "backward"]),
    }

    def check_checksum(value):
        target.fill(value)
        expected_checksum, directions = cases[value.upper()]
        assert target.get_attribute("aria-invalid") in (None, "false")
        assert checksum.locator("[data-wots-checksum-error]").is_hidden()
        assert checksum.locator("[data-wots-checksum-result]").is_visible()
        assert checksum.locator("[data-wots-checksum-value]").text_content().strip() == expected_checksum
        rows = checksum.locator("[data-wots-comparison-row]")
        assert rows.count() == 6
        assert rows.evaluate_all("nodes => nodes.map(n => n.dataset.direction)") == directions
        expected_status = "unchanged" if value.upper() == "ABCD" else "blocked"
        assert checksum.locator("[data-wots-attack-status]").get_attribute("data-result") == expected_status

    assert target.input_value() == "ABCE"
    for value in cases:
        check_checksum(value)
    check_checksum("abce")
    for value in ("", "ABC", "ABCG"):
        target.fill(value)
        assert target.get_attribute("aria-invalid") == "true"
        assert checksum.locator("[data-wots-checksum-error]").is_visible()
        assert checksum.locator("[data-wots-checksum-result]").is_hidden()
    checksum.locator("[data-wots-checksum-reset]").click()
    assert target.input_value() == "ABCE"
    assert checksum.locator("[data-wots-checksum-result]").is_visible()
    check_checksum("ABCE")

    def capture(mode):
        if screenshots:
            for name, demo in demos:
                demo.screenshot(path=str(screenshots / f"wots-{name}-{mode}.png"),
                                style=".md-header, .md-tabs, .md-top { visibility: hidden !important; }")

    capture("desktop")
    page.set_viewport_size({"width": 390, "height": 844})
    dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
    assert dimensions["page"] <= dimensions["viewport"] + 1, dimensions
    for name, demo in demos:
        assert demo.evaluate("node => node.scrollWidth <= node.clientWidth + 1"), f"WOTS {name} overflows."
    digit.press("Home")
    check_chain(0)
    chain.locator("[data-wots-chain-reset]").click()
    check_chain(6)
    check_parameter(256)
    check_parameter(16)
    check_checksum("ABCB")
    check_checksum("ABCE")
    capture("mobile")

    scheme = page.locator("body").get_attribute("data-md-color-scheme")
    page.locator("body").evaluate("node => node.setAttribute('data-md-color-scheme', 'slate')")
    digit.press("ArrowRight")
    check_chain(7)
    chain.locator("[data-wots-chain-reset]").click()
    check_parameter(4)
    check_parameter(16)
    check_checksum("ABCD")
    check_checksum("ABCE")
    capture("dark")
    page.locator("body").evaluate("(node, scheme) => node.setAttribute('data-md-color-scheme', scheme)", scheme)

    fallback_context = browser.new_context(java_script_enabled=False)
    try:
        fallback_context.route("**/*", local_only)
        fallback = fallback_context.new_page()
        response = fallback.goto(base + WOTS + "/", wait_until="networkidle")
        assert response.status == 200
        for name in ("chain", "parameter", "checksum"):
            demo = fallback.locator(f"[data-wots-{name}-demo]")
            assert demo.count() == 1 and demo.is_hidden()
        assert fallback.locator("article table").first.is_visible()
        assert fallback.locator(".arithmatex").filter(has_text=r"\underset{\text{私钥}}{x_0}").is_visible()
        assert fallback.locator(".arithmatex").filter(has_text=r"H^9(\sigma)").is_visible()
        assert fallback.locator("article table").filter(has_text="2,144 B").count() >= 1
    finally:
        fallback_context.close()
    print("WOTS formulas, headings, 16 chain positions, parameters, checksum, keyboard, themes, mobile and no-JS fallback passed.", flush=True)
    return dimensions


def check_mss(page, browser, base, screenshots, local_only):
    page.set_viewport_size({"width": 1440, "height": 1000})
    page.goto(base + MSS + "/", wait_until="networkidle")
    source = (ROOT / "docs" / f"{MSS}.md").read_text()
    display_count = len(re.findall(r"^\$\$[ \t]*$", source, re.M)) // 2
    check_math(page, minimum=display_count)
    article = page.locator("article")
    assert article.locator("h1").count() == 1
    assert article.locator("div.arithmatex").count() == display_count > 0
    assert "$" not in article.inner_text(), "MSS contains unparsed dollar-delimited math."
    headings = article.locator("h1, h2, h3, h4, h5, h6").evaluate_all(
        "nodes => nodes.map(n => ({level:Number(n.tagName.slice(1)), text:n.textContent.trim()}))"
    )
    for previous, current in zip(headings, headings[1:]):
        assert current["level"] <= previous["level"] + 1, headings
    section_ids = set(article.locator("[id]").evaluate_all("nodes => nodes.map(n => n.id)"))
    section_links = page.locator("article a[href^='#'], .md-sidebar a[href^='#']").evaluate_all(
        "nodes => nodes.map(n => n.getAttribute('href')).filter(href => href.length > 1)"
    )
    assert section_links and all(unquote(link[1:]) in section_ids for link in section_links), section_links
    first_section = article.locator("h2[id]").first.get_attribute("id")
    article.locator(f"a[href='#{first_section}']").first.click()
    assert unquote(urlsplit(page.url).fragment) == first_section
    diagram = article.locator("img[src$='mss-tree.svg']")
    assert diagram.count() == 1 and diagram.is_visible()
    assert diagram.evaluate("node => node.complete && node.naturalWidth > 0"), "MSS tree SVG did not load."

    # Independently reproduce the documented byte encoding, including domain tags.
    def parent(left, right):
        return hashlib.sha256(b"\x01" + left + right).digest()

    leaves = [hashlib.sha256(b"\x00" + f"MSS demo public key {index}".encode("utf-8")).digest() for index in range(4)]
    parents = [parent(leaves[0], leaves[1]), parent(leaves[2], leaves[3])]
    trusted_root = parent(*parents)
    values = {"Root": trusted_root, "P0": parents[0], "P1": parents[1],
              **{f"L{index}": value for index, value in enumerate(leaves)}}
    demo = page.locator("[data-mss-demo]")
    demo.wait_for(state="visible")
    buttons = [demo.locator(f"[data-mss-leaf='{index}']") for index in range(4)]
    tamper = demo.locator("[data-mss-tamper]")

    def check_digest(locator, expected):
        assert locator.get_attribute("title") == expected.hex()
        assert locator.text_content().strip() == expected.hex()[:8]

    def check_state(index, changed=False):
        parent_index = index // 2
        sibling = index ^ 1
        sibling_parent = parent_index ^ 1
        first_auth = bytearray(leaves[sibling])
        if changed:
            first_auth[0] ^= 1
        first_auth = bytes(first_auth)
        rebuilt_parent = parent(leaves[index], first_auth) if index % 2 == 0 else parent(first_auth, leaves[index])
        rebuilt_root = parent(rebuilt_parent, parents[sibling_parent]) if parent_index == 0 else parent(parents[sibling_parent], rebuilt_parent)
        page.wait_for_function("expected => { const root = document.querySelector('[data-mss-demo]'); return root?.dataset.selectedLeaf === expected.index && root?.dataset.tampered === expected.changed && !root.hasAttribute('aria-busy') && root.querySelector('[data-mss-computed-root]')?.title === expected.hash; }",
                               arg={"index": str(index), "changed": str(changed).lower(), "hash": rebuilt_root.hex()})
        for position, button in enumerate(buttons):
            assert button.get_attribute("aria-pressed") == str(position == index).lower()
        assert tamper.is_checked() == changed
        authentication = {f"L{sibling}", f"P{sibling_parent}"}
        path = {f"L{index}", f"P{parent_index}", "Root"}
        assert demo.locator("[data-mss-node]").count() == 7
        for name, value in values.items():
            node = demo.locator(f"[data-mss-node='{name}']")
            expected_role = "authentication" if name in authentication else "path" if name in path else "other"
            assert node.get_attribute("data-role") == expected_role
            check_digest(node.locator("code"), value)
        check_digest(demo.locator("[data-mss-auth='0']"), first_auth)
        check_digest(demo.locator("[data-mss-auth='1']"), parents[sibling_parent])
        check_digest(demo.locator("[data-mss-step-hash='0']"), rebuilt_parent)
        check_digest(demo.locator("[data-mss-step-hash='1']"), rebuilt_root)
        check_digest(demo.locator("[data-mss-expected-root]"), trusted_root)
        check_digest(demo.locator("[data-mss-computed-root]"), rebuilt_root)
        leaf_names = [f"L{2 * parent_index}", f"L{2 * parent_index + 1}"]
        if changed:
            leaf_names[sibling % 2] += "*"
        parent_names = ["P0′", "P1"] if parent_index == 0 else ["P0", "P1′"]
        assert demo.locator("[data-mss-step='0']").get_attribute("data-order") == ",".join(leaf_names)
        assert demo.locator("[data-mss-step='1']").get_attribute("data-order") == ",".join(parent_names)
        assert demo.locator("[data-mss-result]").get_attribute("data-valid") == str(not changed).lower()
        assert (rebuilt_root == trusted_root) == (not changed)

    check_state(2)
    for index in range(4):
        buttons[index].click()
        check_state(index)
        tamper.check()
        check_state(index, changed=True)
        tamper.uncheck()
        check_state(index)
    buttons[0].focus()
    buttons[0].press("Enter")
    check_state(0)
    buttons[3].focus()
    buttons[3].press("Space")
    check_state(3)
    tamper.focus()
    tamper.press("Space")
    check_state(3, changed=True)
    tamper.press("Space")
    check_state(3)
    buttons[2].click()
    check_state(2)

    def capture(mode):
        if screenshots:
            demo.screenshot(path=str(screenshots / f"mss-{mode}.png"),
                            style=".md-header, .md-tabs, .md-top { visibility: hidden !important; }")

    capture("desktop")
    mobile_dimensions = []
    for width in (390, 320):
        page.set_viewport_size({"width": width, "height": 844})
        page.wait_for_function("document.documentElement.scrollWidth <= innerWidth + 1")
        dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
        assert dimensions["page"] <= width + 1, dimensions
        assert demo.evaluate("node => node.scrollWidth <= node.clientWidth + 1"), "MSS demo overflows."
        assert diagram.evaluate("node => node.getBoundingClientRect().width <= innerWidth"), "MSS static tree overflows."
        buttons[1].click()
        check_state(1)
        tamper.check()
        check_state(1, changed=True)
        tamper.uncheck()
        buttons[2].click()
        check_state(2)
        capture(f"mobile-{width}")
        mobile_dimensions.append(dimensions)
    scheme = page.locator("body").get_attribute("data-md-color-scheme")
    page.locator("body").evaluate("node => node.setAttribute('data-md-color-scheme', 'slate')")
    tamper.check()
    check_state(2, changed=True)
    capture("dark-invalid")
    tamper.uncheck()
    check_state(2)
    capture("dark")
    page.locator("body").evaluate("(node, scheme) => node.setAttribute('data-md-color-scheme', scheme)", scheme)

    fallback_context = browser.new_context(java_script_enabled=False)
    try:
        fallback_context.route("**/*", local_only)
        fallback = fallback_context.new_page()
        response = fallback.goto(base + MSS + "/", wait_until="networkidle")
        assert response.status == 200
        assert fallback.locator("[data-mss-demo]").count() == 1
        assert fallback.locator("[data-mss-demo]").is_hidden()
        static_tree = fallback.locator("article img[src$='mss-tree.svg']")
        assert static_tree.is_visible() and static_tree.evaluate("node => node.complete && node.naturalWidth > 0")
        assert fallback.locator("article .arithmatex").first.is_visible()
        assert fallback.locator("article div.arithmatex").count() == display_count
        assert fallback.locator("article table").first.is_visible()
    finally:
        fallback_context.close()
    print("MSS formulas, anchors, SVG, four independent SHA-256 proofs, tampering, keyboard, themes, mobile and no-JS fallback passed.", flush=True)
    return mobile_dimensions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    assert (ROOT / "site/index.html").exists(), "Build the site first."
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT / "site")))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}{PREFIX}"
    problems = []
    try:
        with sync_playwright() as playwright:
            options = {"headless": True}
            chrome = os.environ.get("PQC_BROWSER_EXECUTABLE", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            if Path(chrome).is_file():
                options["executable_path"] = chrome
            browser = playwright.chromium.launch(**options)
            context = browser.new_context(viewport={"width": 1440, "height": 1000}, locale="zh-CN")

            def local_only(route):
                if urlsplit(route.request.url).hostname == "127.0.0.1":
                    route.continue_()
                else:
                    problems.append(f"External dependency: {route.request.url}")
                    route.abort()

            context.route("**/*", local_only)
            page = context.new_page()
            page.on("pageerror", lambda error: problems.append(str(error)))
            page.on("response", lambda response: problems.append(f"HTTP {response.status}: {response.url}") if response.status >= 400 else None)
            page.goto(base + ARTICLE + "/", wait_until="networkidle")
            check_math(page)
            print("Full-article math rendering passed.", flush=True)
            formula_count = page.locator(".arithmatex mjx-container").count()
            source = (ROOT / "docs" / f"{ARTICLE}.md").read_text()
            tags = re.findall(r"\\tag\{([^}]+)\}", source)
            numbered = page.locator("[id^='mjx-eqn:']").evaluate_all("nodes => nodes.map(n => n.id)")
            for tag in tags:
                assert f"mjx-eqn:{tag}" in numbered, f"Missing equation number {tag}"
            assert page.locator("table .arithmatex mjx-container").count() > 0
            assert page.locator(".footnote .arithmatex mjx-container").count() > 0
            section_ids = set(page.locator("article [id]").evaluate_all("nodes => nodes.map(n => n.id)"))
            images = page.locator("article img").evaluate_all("nodes => nodes.map(n => ({src:n.src, loaded:n.complete && n.naturalWidth > 0}))")
            assert len(images) == 3 and all(image["loaded"] for image in images), images

            page.locator("a.footnote-ref").first.click()
            assert unquote(urlsplit(page.url).fragment).startswith("fn:")
            page.locator(".footnote-backref").first.click()
            assert unquote(urlsplit(page.url).fragment).startswith("fnref:")

            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
                page.screenshot(path=str(args.screenshots / "article-desktop.png"))

            queries = ["高斯消元", "拒绝采样", "Kyber", "ML-KEM", "数论变换"]
            for query in queries:
                print(f"Checking search: {query}", flush=True)
                page.goto(base, wait_until="networkidle")
                page.locator(".md-search__button").click()
                field = page.get_by_role("combobox")
                field.fill(query)
                result = page.locator(f"a[href*='{ARTICLE}']").filter(has_text=query)
                result.first.wait_for(state="visible", timeout=15000)
                target = urlsplit(result.first.get_attribute("href"))
                if query not in {"Kyber", "ML-KEM"}:
                    assert target.fragment, f"Search did not link to a section: {query}"
                if target.fragment:
                    assert unquote(target.fragment) in section_ids, f"Search links to a missing section: {query}"

            # Follow an actual result, and catch search/MathJax integration races.
            result.first.click()
            page.wait_for_url(re.compile(ARTICLE))
            check_math(page)
            assert urlsplit(page.url).fragment, "Search did not navigate to the matching section."

            page.set_viewport_size({"width": 390, "height": 844})
            page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            check_math(page)
            dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
            assert dimensions["page"] <= dimensions["viewport"] + 1, dimensions
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "article-mobile.png"))

            # Exercise the new topic through its published reading links.
            page.set_viewport_size({"width": 1440, "height": 1000})
            page.goto(base, wait_until="networkidle")
            page.get_by_role("link", name="阅读 PQC 与区块链专题", exact=True).click()
            page.wait_for_url(base + "blockchain/")
            page.get_by_role("link", name="阅读首篇：区块链后量子迁移现状", exact=True).click()
            page.wait_for_url(base + BLOCKCHAIN + "/")
            chapter = page.locator(".md-sidebar--primary a[href='#implementations']")
            assert chapter.is_visible(), "Blockchain chapter navigation is missing."
            chapter.click()
            assert urlsplit(page.url).fragment == "implementations"
            page.locator("article a[href='#ref-quantum-canary']").first.click()
            assert urlsplit(page.url).fragment == "ref-quantum-canary"
            if args.screenshots:
                page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
                page.screenshot(path=str(args.screenshots / "blockchain-desktop.png"))

            blockchain_queries = ["后量子迁移", "零知识证明"]
            for query in blockchain_queries:
                print(f"Checking blockchain search: {query}", flush=True)
                page.goto(base, wait_until="networkidle")
                page.locator(".md-search__button").click()
                page.get_by_role("combobox").fill(query)
                # Search results live in a shadow-root ordered list, outside the
                # header dialog. Exclude matching sidebar and article links.
                result = page.locator(f"ol a[href*='{BLOCKCHAIN}']").filter(has_text=query)
                result.first.wait_for(state="visible", timeout=15000)
                result.first.click()
                page.wait_for_url(re.compile(BLOCKCHAIN))

            page.set_viewport_size({"width": 390, "height": 844})
            page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            blockchain_dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
            assert blockchain_dimensions["page"] <= blockchain_dimensions["viewport"] + 1, blockchain_dimensions
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "blockchain-mobile.png"))
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.goto(base, wait_until="networkidle")
                page.screenshot(path=str(args.screenshots / "home-desktop.png"))
            lamport_dimensions = check_lamport(page, browser, base, args.screenshots, local_only)
            wots_dimensions = check_wots(page, browser, base, args.screenshots, local_only)
            mss_dimensions = check_mss(page, browser, base, args.screenshots, local_only)
            assert not problems, problems
            print(json.dumps({"math_elements": formula_count, "equation_numbers": len(tags),
                              "images": len(images), "search_queries": queries,
                              "footnote_roundtrip": "passed", "mobile_width": dimensions,
                              "blockchain_search_queries": blockchain_queries,
                              "blockchain_mobile_width": blockchain_dimensions,
                              "lamport_states": 16, "lamport_mobile_width": lamport_dimensions,
                              "lamport_keyboard_reset_and_no_js": "passed",
                              "wots_chain_positions": 16, "wots_parameters": [4, 16, 256],
                              "wots_mobile_width": wots_dimensions, "wots_checksum_and_no_js": "passed",
                              "mss_leaf_proofs": 4, "mss_mobile_widths": mss_dimensions,
                              "mss_sha256_tampering_and_no_js": "passed",
                              "external_requests": 0}, ensure_ascii=False))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
