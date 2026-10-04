"""Check generated pages, internal links, equations and footnotes before publishing."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ARTICLE = "basic-lattice-cryptography-notes-zh"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.math = 0
        self.display_math = 0
        self.footnotes = 0
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if "arithmatex" in attrs.get("class", "").split():
            self.math += 1
            self.display_math += tag == "div"
        if attrs.get("id", "").startswith("fn:"):
            self.footnotes += 1
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def main():
    assert (SITE / "index.html").is_file(), "Build the site first."
    pages = {p.resolve(): Page(p) for p in SITE.rglob("*.html")}
    prefix = urlsplit(tomllib.loads((ROOT / "zensical.toml").read_text())["project"]["site_url"]).path
    checked = 0
    for path, page in pages.items():
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            relative = unquote(url.path)
            if relative.startswith("/"):
                assert relative.startswith(prefix), f"Wrong project prefix: {link}"
                target = SITE / relative[len(prefix):]
            else:
                target = path.parent / relative if relative else path
            if target.is_dir():
                target /= "index.html"
            target = target.resolve()
            assert target.is_relative_to(SITE.resolve()), f"Link escapes site: {link}"
            assert target.is_file(), f"Missing target in {path.relative_to(SITE)}: {link}"
            if url.fragment and target in pages:
                assert unquote(url.fragment) in pages[target].ids, f"Missing anchor: {link}"
            checked += 1
    article = pages[(SITE / ARTICLE / "index.html").resolve()]
    source = (ROOT / "docs" / f"{ARTICLE}.md").read_text()
    expected_footnotes = len(re.findall(r"^\[\^[^\]]+\]:", source, re.M))
    assert article.footnotes == expected_footnotes > 0
    assert article.math > 100, "Math markup was not rendered into protected elements."
    expected_display = len(re.findall(r"^\$\$[ \t]*$", source, re.M)) // 2
    assert article.display_math == expected_display, "Display math parsed as inline: check blank lines around $$."
    assert (SITE / "assets/vendor/mathjax/tex-chtml.js").is_file()
    assert (SITE / "assets/vendor/mathjax-newcm-font/chtml.js").is_file()
    print(json.dumps({"pages": len(pages), "internal_links": checked,
                      "math_elements": article.math, "display_math": article.display_math,
                      "footnotes": article.footnotes}, ensure_ascii=False))


if __name__ == "__main__":
    main()
