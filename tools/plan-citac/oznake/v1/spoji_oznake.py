#!/usr/bin/env python3
"""Oznake v1: spremanje oznaka dvaju označivača (A, B), sparivanje i popis razlika za suca.

    python3 spoji_oznake.py spremi      # iz zapisa pomoćnih agenata u oznake_A_*.json / oznake_B_*.json
    python3 spoji_oznake.py usporedi    # sporovi.json (za stranicu suca) + sazetak

Sparivanje: članak, stavak, blok, parametar, vrsta građevine (kodovi iz vrste_gradevina + oblik) i vrijednost.
Razlike se bilježe po poljima; sitne razlike koje ne mijenjaju značenje (dužina citata, tekst obrazloženja) se ne broje.
Razlike istog oblika (isto polje, iste vrijednosti A i B) grupiraju se u UZORAK, da sudac odluči jednom za sve.
"""
import hashlib, json, re, sys
from pathlib import Path

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parent.parent))
import vrste_gradevina as vg

ZADACI = "/tmp/claude-0/-home-claude/c31048c0-670e-5bd6-aeac-98e3c724fbf0/tasks/{}.output"
AGENTI = {("G1_ppug_22_23", "A"): "a05902aa5785c3302", ("G1_ppug_22_23", "B"): "a2592607305b4b5bb",
          ("G2_ppug_25_33", "A"): "a63bf81095875cd8c", ("G2_ppug_25_33", "B"): "a47f02def8f34244e",
          ("G3_ppug_20_38_39_50", "A"): "a775d749f42dfcfa0", ("G3_ppug_20_38_39_50", "B"): "a4c40db9694af3105",
          ("G4_upu1_14", "A"): "adc09a98e27eeddf0", ("G4_upu1_14", "B"): "a98bcea82e6e12118",
          ("G5_upu1_24", "A"): "acfc8abc430a8ac7e", ("G5_upu1_24", "B"): "a1fcf28eb85d3bcf4"}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
n = lambda s: re.sub(r"\s+", " ", str(s if s is not None else "")).strip().lower()


def iz_zapisa(agent):
    kand = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and '{"oznacivac"' in x:
            for m in re.finditer(r'\{"oznacivac"', x):
                try:
                    kand.append(json.JSONDecoder().raw_decode(x[m.start():])[0])
                except Exception:
                    pass
    p = Path(ZADACI.format(agent))
    if not p.exists():
        return None
    for l in p.open():
        try:
            walk(json.loads(l))
        except json.JSONDecodeError:
            pass
    k = [c for c in kand if isinstance(c.get("zapisi"), list) and c["zapisi"]]
    return k[-1] if k else None


def spremi():
    out = {}
    for (g, o), a in AGENTI.items():
        d = iz_zapisa(a)
        if d is None:
            out[f"{g}/{o}"] = "NEDOSTAJE"; continue
        tekst = (D / f"tekst_{g}.txt").read_text(encoding="utf-8")
        nedoslovni = [z["id"] for z in d["zapisi"] if n(z.get("citat")) not in n(tekst)]
        d["metapodaci"] = {"oznacivac": o, "skupina": g, "ulaz": f"tekst_{g}.txt", "sha256_ulaza": sha(D / f"tekst_{g}.txt"),
                           "upute": "UPUTE_OZNACAVANJA_v1.md", "sha256_uputa": sha(D / "UPUTE_OZNACAVANJA_v1.md"),
                           "postupak": "pomoćni agent u zasebnom kontekstu, bez alata, bez uvida u izlaze čitača i u oznake drugog označivača",
                           "citati_nisu_doslovni": nedoslovni}
        p = D / f"oznake_{o}_{g}.json"
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        out[f"{g}/{o}"] = {"zapisa": len(d["zapisi"]), "nedoslovni_citati": len(nedoslovni), "sha256": sha(p)}
    return out


def kljuc_vrste(s):
    s = s or ""
    r = vg.prepoznaj(s)
    kod = "+".join(r["kodovi"]) if r else n(re.sub(r"\(.*?\)", "", s.split("–")[0]))
    ob = n(s.split("–")[1]) if "–" in s else ""
    ob = re.sub(r"\(.*?\)", "", ob).strip()
    ob = {"samostojeća": "samostojeća", "slobodnostojeća": "slobodnostojeća"}.get(ob, ob)
    stanje = "postojeća" if "postojeć" in s else ("nova" if "(nova)" in s else "")
    return (kod, ob, stanje)


def kljuc_vrijednosti(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return round(float(v), 6)
    return n(v)


def kljuc(z):
    return (z.get("clanak"), z.get("stavak"), z.get("blok"), n(z.get("parametar")), kljuc_vrste(z.get("vrsta_gradevine")), kljuc_vrijednosti(z.get("vrijednost")))


POLJA = ["tocka", "alineja_rb", "operator", "jedinica", "uvjet_primjene", "modal", "vrsta_pravila", "jednoznacnost"]


def usp_polje(f, a, b):
    if f == "uvjet_primjene":
        A = {n(x) for x in (a or "").split(";") if n(x)}; B = {n(x) for x in (b or "").split(";") if n(x)}
        return A == B
    return n(a) == n(b)


def usporedi():
    sporovi, sazetak = [], {}
    for g in sorted({g for g, _ in AGENTI}):
        pa, pb = D / f"oznake_A_{g}.json", D / f"oznake_B_{g}.json"
        if not (pa.exists() and pb.exists()):
            sazetak[g] = "NEDOSTAJE"; continue
        A = json.loads(pa.read_text(encoding="utf-8"))["zapisi"]; B = json.loads(pb.read_text(encoding="utf-8"))["zapisi"]
        uzeto = [False] * len(B)
        parovi, samo_a = [], []
        for a in A:
            i = next((i for i, b in enumerate(B) if not uzeto[i] and kljuc(b) == kljuc(a)), None)
            if i is None:
                samo_a.append(a)
            else:
                uzeto[i] = True; parovi.append((a, B[i]))
        # drugi i treći prolaz: isti članak/stavak/parametar, a razlikuje se samo vrsta građevine ili samo vrijednost
        for slabi in (lambda z: kljuc(z)[:4] + (kljuc(z)[5],), lambda z: kljuc(z)[:5],
                      lambda z: kljuc(z)[:4] + (n(z.get("citat")),), lambda z: kljuc(z)[:4],
                      # slobodni nazivi »drugo: …« razlikuju se u sročenosti: isti citat i ista vrijednost
                      lambda z: kljuc(z)[:3] + (n(z.get("citat")), kljuc(z)[5]),
                      lambda z: kljuc(z)[:3] + (n(z.get("citat")),),
                      lambda z: kljuc(z)[:3] + ("drugo" if n(z.get("parametar")).startswith("drugo") else n(z.get("parametar")), kljuc(z)[5])):
            ostali_a = []
            for a in samo_a:
                i = next((i for i, b in enumerate(B) if not uzeto[i] and slabi(b) == slabi(a)), None)
                if i is None:
                    ostali_a.append(a)
                else:
                    uzeto[i] = True; parovi.append((a, B[i]))
            samo_a = ostali_a
        samo_b = [b for i, b in enumerate(B) if not uzeto[i]]
        slaganje = 0
        for a, b in parovi:
            raz = [f for f in POLJA if not usp_polje(f, a.get(f), b.get(f))]
            pa_, pb_ = n(a.get("parametar")), n(b.get("parametar"))
            if pa_ != pb_ and not (pa_.startswith("drugo") and pb_.startswith("drugo")):
                raz.insert(0, "parametar")
            if kljuc(a)[4] != kljuc(b)[4]:
                raz.insert(0, "vrsta_gradevine")
            va, vb = a.get("vrijednost"), b.get("vrijednost")
            brojcano = any(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (va, vb))
            # tekstualne vrijednosti (opis) razlikuju se u sročenosti; to nije spor, osim kad je jedna brojka
            if kljuc(a)[5] != kljuc(b)[5] and (brojcano or va is None or vb is None):
                raz.insert(0, "vrijednost")
            if not raz:
                slaganje += 1; continue
            sporovi.append({"id": f"{g}:{a['id']}~{b['id']}", "skupina": g, "vrsta": "RAZLIKA", "polja": raz, "A": a, "B": b})
        for a in samo_a:
            sporovi.append({"id": f"{g}:{a['id']}~", "skupina": g, "vrsta": "SAMO_A", "polja": [], "A": a, "B": None})
        for b in samo_b:
            sporovi.append({"id": f"{g}:~{b['id']}", "skupina": g, "vrsta": "SAMO_B", "polja": [], "A": None, "B": b})
        sazetak[g] = {"A": len(A), "B": len(B), "sparenih": len(parovi), "potpuno_isti": slaganje,
                      "razlika_u_poljima": len(parovi) - slaganje, "samo_A": len(samo_a), "samo_B": len(samo_b)}
    # uzorci: isto polje i isti par vrijednosti → jedna odluka
    for s in sporovi:
        if s["vrsta"] == "RAZLIKA" and len(s["polja"]) == 1:
            f = s["polja"][0]
            if f == "uvjet_primjene":
                ua = {n(x) for x in (s["A"].get(f) or "").split(";") if n(x)}
                ub = {n(x) for x in (s["B"].get(f) or "").split(";") if n(x)}
                dio = []
                if ub - ua:
                    dio.append("B dodaje: " + "; ".join(sorted(ub - ua)))
                if ua - ub:
                    dio.append("A dodaje: " + "; ".join(sorted(ua - ub)))
                s["uzorak"] = "uvjet · " + " · ".join(dio)
            else:
                s["uzorak"] = f"{f}: A={n(s['A'].get(f))} | B={n(s['B'].get(f))}"
    return sporovi, sazetak


if __name__ == "__main__":
    if sys.argv[1] == "spremi":
        print(json.dumps(spremi(), ensure_ascii=False, indent=1))
    else:
        sp, sz = usporedi()
        (D / "sporovi.json").write_text(json.dumps(sp, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(sz, ensure_ascii=False, indent=1))
        from collections import Counter
        print(len(sp), Counter(s["vrsta"] for s in sp), Counter(f for s in sp for f in s["polja"]))
        print(Counter(s.get("uzorak") for s in sp if s.get("uzorak")).most_common(25))
