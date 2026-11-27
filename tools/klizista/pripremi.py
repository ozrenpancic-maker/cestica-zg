#!/usr/bin/env python3
"""Priprema sloja rizika od klizišta (PRI-MJER, RGN, 2023., M 1:100 000) za aplikaciju.

Ulaz: korisnikova GIS rekonstrukcija karte A14 (paket CesticaHR_Klizista_RH_GIS.zip, uz dopuštenje autora):
  - rizik_klizista_RH_3765.tif  GeoTIFF, HTRS96/TM (EPSG:3765), 150 m, vrijednosti 0 (bez podataka), 1 nizak, 2 srednji, 3 visok
  - rizik_klizista_RH.mbtiles   PNG pločice (EPSG:3857), razine 5-10
Izlaz:
  - data/klizista/rizik.bin     razredi po recima, RLE (format ispod), za očitanje razreda u pregledniku
  - data/klizista/t/{z}/{x}/{y}.png  pločice za sloj na karti (XYZ)

Format rizik.bin (little-endian):
  0  "KLZ1"   4 B
  4  W, H     uint16, uint16  (stupci, reci)
  8  x0, y0   int32, int32    (gornji lijevi kut mreže, HTRS96/TM, m)
  16 cell     uint16          (veličina ćelije, m)
  18 rezerva  uint16
  20 off[H+1] uint32          (početak niza za redak, u jedinicama od 2 B)
  ...  run    uint16          (razred = run >> 14, duljina = run & 0x3FFF)
Pokretanje: python3 -I tools/klizista/pripremi.py <mapa_s_ulazima> <korijen_repozitorija>
"""
import sys, struct, sqlite3, pathlib
import numpy as np, tifffile

src, root = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out = root / "data/klizista"; out.mkdir(parents=True, exist_ok=True)

t = tifffile.TiffFile(src / "rizik_klizista_RH_3765.tif"); p = t.pages[0]
sc, tp = p.tags["ModelPixelScaleTag"].value, p.tags["ModelTiepointTag"].value
gk = p.tags["GeoKeyDirectoryTag"].value
assert 3765 in gk, "očekivan HTRS96/TM (EPSG:3765)"
assert sc[0] == sc[1] and float(sc[0]).is_integer() and tp[0] == 0 and tp[1] == 0
a = p.asarray(); H, W = a.shape
assert set(np.unique(a)) <= {0, 1, 2, 3}
runs, off = [], [0]
for r in a:
    ch = np.flatnonzero(np.diff(r)) + 1
    st = np.concatenate(([0], ch)); en = np.concatenate((ch, [W]))
    for s, e in zip(st, en):
        v, n = int(r[s]), int(e - s)
        while n > 0:
            k = min(n, 0x3FFF); runs.append((v << 14) | k); n -= k
    off.append(len(runs))
hdr = b"KLZ1" + struct.pack("<HHiiHH", W, H, int(tp[3]), int(tp[4]), int(sc[0]), 0)
(out / "rizik.bin").write_bytes(hdr + struct.pack(f"<{H+1}I", *off) + struct.pack(f"<{len(runs)}H", *runs))

db = sqlite3.connect(src / "rizik_klizista_RH.mbtiles"); n = 0
for z, x, yt, d in db.execute("select zoom_level,tile_column,tile_row,tile_data from tiles"):
    y = (1 << z) - 1 - yt; f = out / "t" / str(z) / str(x) / f"{y}.png"
    f.parent.mkdir(parents=True, exist_ok=True); f.write_bytes(d); n += 1
print(f"rizik.bin: {W}x{H}, {len(runs)} nizova, {(out/'rizik.bin').stat().st_size} B; pločica: {n}")
