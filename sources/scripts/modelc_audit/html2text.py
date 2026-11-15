import sys, html
from html.parser import HTMLParser
SKIP = {"script", "style", "noscript", "svg", "head"}
BLOCK = {"p", "div", "section", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "br", "figcaption", "figure", "table", "caption", "dt", "dd", "article", "header", "footer", "blockquote"}
class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in SKIP: self.skip += 1
        elif tag in BLOCK: self.out.append("\n")
        if tag in ("td", "th"): self.out.append("\t")
    def handle_endtag(self, tag):
        if tag in SKIP and self.skip: self.skip -= 1
        elif tag in BLOCK: self.out.append("\n")
    def handle_data(self, d):
        if not self.skip: self.out.append(d)
p = P(); p.feed(open(sys.argv[1], encoding="utf-8", errors="replace").read())
text = "".join(p.out)
lines = [" ".join(l.split()) for l in text.split("\n")]
res, blank = [], 0
for l in lines:
    if l: res.append(l); blank = 0
    else:
        blank += 1
        if blank == 1: res.append("")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(res).strip() + "\n")
