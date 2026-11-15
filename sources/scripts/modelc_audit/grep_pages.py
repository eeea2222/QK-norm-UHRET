import sys, re
path, pat = sys.argv[1], sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 150
t = open(path, encoding="utf-8", errors="replace").read()
pages = t.split("\f")
n = 0
for i, p in enumerate(pages, 1):
    for m in re.finditer(pat, p, flags=re.I):
        n += 1
        s = p[max(0, m.start()-ctx): m.end()+ctx].replace("\n", " ")
        print(f"[p{i}] ...{s}...")
print("hits:", n, file=sys.stderr)
