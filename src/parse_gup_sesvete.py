import re, json, sys
src = open(sys.argv[1], encoding="utf-8").read().splitlines()
# strip headers/footers/page numbers
clean = []
for l in src:
    s = l.strip()
    if not s: continue
    if "ODLUKA O DONOŠENJU GUP" in s or "NESLUŽBENI PROČIŠĆENI" in s or "GENERALNOGA URBANISTIČKOG PLANA SESVETA" in s or s.startswith("Odredbe za provedbu – izmjene"): continue
    if re.fullmatch(r"\d{1,3}", s): continue
    clean.append(s)
text = "\n".join(clean)
# split into articles
parts = re.split(r"\n(Članak \d+\.(?:[a-z]\.?)?)\n", "\n" + text)
arts = {}
for i in range(1, len(parts), 2):
    num = parts[i].replace("Članak ", "").strip()
    arts.setdefault(num, parts[i + 1])
wanted = [k for k in arts if re.match(r"^(5[7-9]|6\d|7[0-5])\.", k)]
KEYS = {
    "cestica": r"^najmanja (površina|veličina) građevne čestice|^najmanja građevna čestica",
    "izgradenost": r"^(najveća )?izgrađenost",
    "kis": r"^najveći kis|^najveći kisn|najveći kisn",
    "gbp": r"najveći GBP|najveća GBP",
    "visina": r"^najveća visina",
    "teren": r"^(najmanji )?prirodni teren",
    "meda": r"udaljenost građevin\w* od međe",
    "jedinice": r"samostalne uporabne jedinice|stambenih jedinica",
    "pgm": r"PGM",
}
def join_items(lines):
    """Join wrapped lines into numbered items."""
    items, cur = [], None
    for l in lines:
        m = re.match(r"^(\d{1,2})\.\s+(.*)", l)
        if m:
            if cur: items.append(cur)
            cur = m.group(2)
        elif cur is not None:
            cur += " " + l
        else:
            items.append(l)
    if cur: items.append(cur)
    return [re.sub(r"(?<=\w)-\s+(?=[a-zčćšžđ])", "", re.sub(r"\s+", " ", it)).strip() for it in items]

rules = {}
for a in wanted:
    body = arts.get(a)
    if not body: continue
    flat = re.sub(r"\s+", " ", body)
    m = re.search(r"\((\d\.\d+\.(?:\d\.)?)\)", flat)
    if not m: continue
    code = m.group(1)
    # title: text between "(1)" and the code
    tm = re.search(r"(?:\(1\)\s*)?(.*?)\s*\(" + re.escape(code) + r"\)", flat)
    title = tm.group(1).strip() if tm else ""
    title = re.sub(r"^\(1\)\s*", "", title)
    pm = re.search(r"\(" + re.escape(code) + r"\)\s*-?\s*prostori:?\s*(.*?)(?:\(2\)|$)", flat)
    prostori = pm.group(1).strip() if pm else ""
    lines = body.split("\n")
    # locate detaljna pravila
    di = next((k for k, l in enumerate(lines) if re.match(r"^\(\d+\)\s*Detaljna pravila", l)), None)
    oi = next((k for k, l in enumerate(lines) if re.match(r"^\(\d+\)\s*Opća pravila", l)), None)
    opca = []
    if oi is not None:
        end = di if di is not None else len(lines)
        seg = []
        for l in lines[oi + 1:end]:
            if re.match(r"^\(\d+\)", l): break
            seg.append(l)
        opca = join_items(seg)
    zones = []
    if di is not None:
        seg = lines[di + 1:]
        # stop at next paragraph (n) that is not inside
        cut = []
        for l in seg:
            if re.match(r"^\(\d+\)\s", l) and not re.match(r"^\(\d+\)\s*Detaljna", l):
                break
            cut.append(l)
        cur = {"zona": "sve zone", "lines": []}
        for l in cut:
            zm = re.match(r"^([a-g])\.\s+(u zoni.*|za .*|na .*)", l, re.I)
            if zm:
                if cur["lines"]: zones.append(cur)
                cur = {"zona": zm.group(2).rstrip(":"), "lines": []}
            else:
                cur["lines"].append(l)
        if cur["lines"]: zones.append(cur)
        for z in zones:
            # zone header may wrap: absorb leading non-numbered lines into zone name
            while z["lines"] and not re.match(r"^\d{1,2}\.\s", z["lines"][0]):
                z["zona"] = (z["zona"] + " " + z["lines"].pop(0)).rstrip(":")
            z["items"] = join_items(z.pop("lines"))
            key = {}
            for it in z["items"]:
                for k, rx in KEYS.items():
                    if k not in key and re.search(rx, it, re.I):
                        key[k] = it
            z["key"] = key
    # full article as paragraphs (fallback for rules without zone structure)
    paras = re.split(r"\s(?=\(\d+\)\s)", flat)
    paras = [re.sub(r"(?<=\w)-\s+(?=[a-zčćšžđ])", "", p).strip() for p in paras if p.strip()]
    rules[code] = {"clanak": a.rstrip("."), "naziv": title, "prostori": prostori, "opca": opca, "zone": zones, "tekst": paras}
json.dump(rules, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c, r in rules.items():
    print(c, "čl.", r["clanak"], "|", r["naziv"][:60], "| zone:", [ (z["zona"][:40], sorted(z["key"].keys())) for z in r["zone"]])
