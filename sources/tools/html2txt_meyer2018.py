"""Convert a saved HTML page (untrusted data) to readable plain text.

Usage: python -I html2txt.py <in.html> <out.txt> <mode>
mode = pmc  : keep the PMC article (citation block .. references), drop site chrome
mode = nist : keep <main> content only
Headings are written on their own line prefixed with '#'s; table rows become
'cell | cell' lines; <sup> outside MathML is written as '^x'; script/style/svg/button/nav content is dropped.
"""
import sys
import re
from html.parser import HTMLParser

BLOCK = {"p", "div", "section", "article", "li", "ul", "ol", "table", "tr", "thead",
         "tbody", "figure", "figcaption", "br", "dl", "dt", "dd", "blockquote", "header",
         "footer", "aside", "h1", "h2", "h3", "h4", "h5", "h6", "caption", "hr", "math"}
SKIP = {"script", "style", "svg", "noscript", "button", "template", "form", "select", "nav"}
VOID = {"br", "hr", "img", "meta", "link", "input", "source", "wbr", "area", "base", "col",
        "embed", "param", "track"}


class Conv(HTMLParser):
    def __init__(self, mode):
        super().__init__(convert_charrefs=True)
        self.mode = mode
        self.out = []
        self.skip = 0
        self.active = False
        self.done = False
        self.depth_main = 0
        self.stack = []
        self.in_math = 0

    def _start_active(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if self.mode == "pmc":
            if tag == "section" and "pmc-layout__citation" in cls:
                self.active = True
            if tag == "section" and "pmc-sidenav__container" in cls:
                self.active = False
                self.done = True
        elif self.mode == "nist":
            if a.get("id") == "main-content" and not self.done:
                self.active = True
            if tag == "footer" and "nist-footer" in cls:
                self.active = False
                self.done = True

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        self._start_active(tag, attrs)
        if tag not in VOID:
            self.stack.append(tag)
        if not self.active:
            return
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in BLOCK:
            self.out.append("\n")
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("#" * int(tag[1]) + " ")
        if tag in ("td", "th"):
            self.out.append(" | ")
        if tag == "li":
            self.out.append("- ")
        if tag == "sup" and not self.in_math:
            self.out.append("^")
        if tag == "math":
            self.in_math += 1
        if tag == "img":
            alt = dict(attrs).get("alt")
            if alt:
                self.out.append(f"[image: {alt}]")

    def handle_endtag(self, tag):
        if self.done:
            return
        # pop stack
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                if t == tag:
                    break
        if not self.active:
            return
        if tag in SKIP:
            if self.skip:
                self.skip -= 1
            return
        if self.skip:
            return
        if tag == "math" and self.in_math:
            self.in_math -= 1
        if tag in BLOCK:
            self.out.append("\n")
        if self.mode == "nist" and tag == "main":
            self.active = False
            self.done = True

    def handle_data(self, data):
        if self.done or not self.active or self.skip:
            return
        self.out.append(data)

    def text(self):
        s = "".join(self.out)
        s = s.replace(" ", " ")
        lines = []
        for ln in s.split("\n"):
            ln = re.sub(r"[ \t\r\f\v]+", " ", ln).strip()
            lines.append(ln)
        s = "\n".join(lines)
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip() + "\n"


def main():
    src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(src, encoding="utf-8", errors="replace") as f:
        html = f.read()
    c = Conv(mode)
    c.feed(html)
    c.close()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(c.text())


if __name__ == "__main__":
    main()
