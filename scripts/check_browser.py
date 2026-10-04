"""Exercise the real built site under the GitHub Pages project prefix, offline."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import unquote, urlsplit
import argparse
import json
import os
import re

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = "basic-lattice-cryptography-notes-zh"
PREFIX = "/pqc-notes/"


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.startswith(PREFIX):
            path = "/" + path[len(PREFIX):]
        return super().translate_path(path)

    def log_message(self, *_args):
        pass


def check_math(page):
    page.wait_for_function("window.MathJax?.startup?.promise !== undefined")
    page.evaluate("async () => { await MathJax.startup.promise; await document.fonts.ready; }")
    errors = page.locator("mjx-merror, [data-mjx-error]")
    assert errors.count() == 0, errors.all_text_contents()
    assert page.locator(".arithmatex mjx-container").count() > 100
    missing = page.locator(".arithmatex").evaluate_all(
        "nodes => nodes.filter(n => !n.querySelector('mjx-container')).map(n => n.textContent.slice(0, 100))"
    )
    assert not missing, f"Unrendered math at {page.url}: {missing[:5]}"


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
                page.evaluate("window.scrollTo(0, 0)")
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
            page.evaluate("window.scrollTo(0, 0)")
            check_math(page)
            dimensions = page.evaluate("({viewport:innerWidth, page:document.documentElement.scrollWidth})")
            assert dimensions["page"] <= dimensions["viewport"] + 1, dimensions
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "article-mobile.png"))
                page.set_viewport_size({"width": 1440, "height": 1000})
                page.goto(base, wait_until="networkidle")
                page.screenshot(path=str(args.screenshots / "home-desktop.png"))
            assert not problems, problems
            print(json.dumps({"math_elements": formula_count, "equation_numbers": len(tags),
                              "images": len(images), "search_queries": queries,
                              "footnote_roundtrip": "passed", "mobile_width": dimensions,
                              "external_requests": 0}, ensure_ascii=False))
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
