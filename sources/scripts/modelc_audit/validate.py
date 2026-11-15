import json, re, sys, openpyxl
from openpyxl.utils import column_index_from_string
d = json.load(open("items_draft.json"))
docs = {x["doc_id"]: x for x in d["documents"]}
norm = lambda s: " ".join(s.split())
W = "/home/efeai/Desktop/NasaSpaceApps/external/model_c/data/raw/PSI-101_Analyzed Data_SAME, SAME-R_Results.xlsx"
wbs = {True: openpyxl.load_workbook(W, data_only=False), False: openpyxl.load_workbook(W, data_only=True)}
cache = {}
bad = 0
for it in d["items"]:
    doc = docs[it["doc_id"]]; a = it["anchor_quote"]
    nw = len(a.split())
    ok = None
    if "_xlsx" in it:
        sheet, cell, formula = it["_xlsx"]
        v = wbs[formula][sheet][cell].value
        ok = (str(v) == a)
    else:
        tp = doc["text_path"]
        if tp not in cache: cache[tp] = open(tp, encoding="utf-8", errors="replace").read()
        t = cache[tp]
        if it["pdf_page"]:
            pages = t.split("\f"); t = pages[it["pdf_page"] - 1]
        ok = norm(a) in norm(t)
    flag = "OK " if ok and nw <= 15 else "BAD"
    if flag == "BAD": bad += 1
    print(flag, it["item_id"], it["category"], it["doc_id"], it["pdf_page"], nw, "|", a[:80])
print("bad:", bad)
