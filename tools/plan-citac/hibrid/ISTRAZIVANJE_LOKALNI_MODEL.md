# Lokalni model otvorenih težina: istraživanje (bez integracije)

Status: istraživačka bilješka. Ništa iz nje nije integrirano niti pokrenuto. Integracija je moguća tek nakon odobrenja.

## 1. Što je izmjereno, a što nije
- **Izmjereno:** ništa. Nijedan lokalni model nije pokrenut na ovom zadatku.
- **Kvaliteta na hrvatskom tekstu prostornih planova:** Podaci nisu dostupni.
- **Opće hrvatske i južnoslavenske ocjene:** postoje javne evaluacije (CLASSLA: COPA, PIQA, sentiment, teme, žanr; Global-PIQA; Serbian SuperGLUE, LoResLM 2026). Te evaluacije ne mjere izdvajanje doslovnih citata ni JSON sheme, pa ne zamjenjuju vlastito mjerenje.
- **Brzina i potrošnja memorije:** donji brojevi preuzeti su iz javnih vodiča (izvori niže). Ovdje nisu provjereni.

## 2. Zahtjevi zadatka koji određuju izbor
- Ulaz po skupu je oko 1 000 do 7 000 tokena teksta i oko 2 500 tokena uputa. Izlaz je dug JSON: na razvojnim skupovima 40 do 240 kandidata, generator v1/v2 trošio je oko 90 000 do 200 000 tokena po skupu (uključujući razmišljanje).
- Potreban je kontekst od najmanje 32 000 tokena. Bolje je 64 000 do 128 000 tokena, ili obrada po članku.
- Potrebno je strogo poštivanje doslovnih citata. Deterministička provjera odbacuje svaki nedoslovni citat, pa slabiji model daje manju pokrivenost, a ne više pogrešaka. Ta tvrdnja vrijedi samo uz nepromijenjenu provjeru.
- Poželjno je ograničeno dekodiranje prema JSON shemi (npr. gramatike u llama.cpp ili vLLM guided decoding). Ono uklanja neispravan JSON, ali ne jamči ispravan sadržaj.

## 3. Kandidati i približni hardverski zahtjevi (javni izvori, listopad 2026)
| Razred | Primjeri modela | Težine pri 4 bita (približno) | Tipičan hardver |
|---|---|---|---|
| Mali, 8–14 B | Qwen 3 8B, Qwen 3.5 9B, Gemma 4 12B, Phi-4 14B | 5–9 GB | GPU s 12–16 GB ili Apple M s 16–24 GB |
| Srednji, 24–32 B | Qwen 3.x 27B/32B, Gemma 4 31B, Mistral Small 3.2 24B | 14–20 GB | GPU s 24 GB (RTX 3090/4090) ili Apple M s 32–64 GB |
| MoE srednji | Gemma 4 26B-A4B, Qwen 3.5/3.6 35B-A3B | 18–24 GB | 24 GB; kod 35B-A3B pri Q4 vodiči navode da ne ostaje mjesta za kontekst |
| Veliki, 70 B | Llama 3.3 70B, Qwen2.5 72B | 35–40 GB | 2×24 GB ili 48 GB GPU; ili djelomično u RAM (sporo) |

- Uz težine treba rezervirati još 20–30 % memorije za kontekst (KV cache).
- Q4_K_M/Q5_K_M vodiči opisuju kao blizu pune preciznosti; ispod oko 4 bita kvaliteta mjerljivo pada.
- Okvirne brzine generiranja na RTX 4090 pri Q4 iz vodiča: modeli od 8 B oko 95–130 tokena/s, modeli od 30 B i više oko 30–40 tokena/s.
- Procjena (izračun, ne mjerenje): izlaz od 100 000 tokena po skupu pri 35 tokena/s traje oko 48 minuta po planu. Pri 8 B modelu traje oko 15 minuta, uz vjerojatno manju pokrivenost.
- Licence se razlikuju po modelu (Apache 2.0, Gemma terms, Llama licence). Treba ih provjeriti prije svake uporabe; ovdje nisu provjerene.

## 4. Preporučeni postupak ako se odobri ispitivanje
1. Ne mijenjati zamrznute upute, provjeru ni usporedbu. Lokalni model mijenja samo generator.
2. Pokrenuti 1–2 modela srednjeg razreda (npr. 27–32 B pri Q4–Q5, ograničeno JSON dekodiranje) na četiri razvojna skupa, istim ulazima (`hibrid/razvoj/*.txt`, SHA u `ulazi.json`).
3. Mjeriti istim `hibrid/mjeri.py`: pogrešno prihvaćeni, pokrivenost JASAN, stopa pogrešaka među tehnički provjerenima, broj za pregled, vrijeme i hardver.
4. Tek ako je pogrešno prihvaćenih 0 i pokrivenost usporediva, predložiti slijepi test na novom planu.

## Izvori
- Spheron, best open-source LLMs to self-host 2026, VRAM guide (objavljeno 23. 6. 2026., ažurirano 19. 10. 2026.): https://www.spheron.network/blog/best-open-source-llms-self-host-2026-vram-guide/
- IntuitionLabs, Local LLM deployment on 24GB GPUs (revidirano 10. 10. 2026.): https://intuitionlabs.ai/articles/local-llm-deployment-24gb-gpu-optimization
- CLASSLA godišnji pregled 2025 (južnoslavenske evaluacije LLM-a): https://mailman.ijs.si/pipermail/classla/20251229/000050.html
- Serbian SuperGLUE, LoResLM 2026: https://aclanthology.org/2026.loreslm-1.30
