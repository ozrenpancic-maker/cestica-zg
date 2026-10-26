# Neovisne tekstualne oznake – PPUG Krk, članci 22 i 23

Izvor: korisnički dostavljen `ppug_cl22_23_izvorni_tekst.txt`, oznake iz prvog dijela pročišćenog teksta SN PGŽ 29/2020. Nisam koristio Claudeov referentni JSON niti `rules_krk.json` za sastavljanje 55 oznaka. Međutim, ChatGPT je ranije vidio opis Claudeova pristupa i izvještaj o početnom testu. Stoga ovo jesu oznake **drugog označivača**, ali **nisu strogo dvostruko slijepa studija**.

## Pravila označavanja

- Svaka brojčana vrijednost za zaseban tip kuće (slobodnostojeća, dvojna, ugrađena) predstavlja zaseban zapis. To je izbor *granularnosti* koji utječe na broj redaka; ne mora odgovarati Claudeovom modelu.
- Stavak (2) koji uređuje poljoprivredne gospodarske građevine također je u opsegu. Uključeni su i ključni opisni uvjeti; nije potpuno popisan svaki oblikovni zahtjev iz odlomka.
- `JASAN` = dokazni tekst jasno sadrži opisanu vrijednost. To **ne znači** da je pravilo pravno važeće ili da je odmah primjenjivo na neku česticu.
- `PREGLED` = nužno je provjeriti semantiku/sinonim/referentnu točku/opseg primjene; takvo pravilo nije sigurno za automatski izračun.
- `kis_nadzemni_max` i `kis_uz_podrum_max` **namjerno su različiti parametri**.
- Povijesne graditeljske cjeline iz PPUG-a **ne poistovjećuju se automatski** s kulturno-povijesnim zonama UPU-a.
- Svi navodi `dokaz` doslovni su podnizovi korisnički dostavljenog teksta. Oznake retka 1003 i 1076 naslijeđene su iz izvoda.
- Bez provjere drugih članaka, provedbenih izmjena ili kartografskih slojeva; **pravna potvrda: 0**.

## Rezultat

- 55 označenih zapisa: 31 u članku 22, 24 u članku 23.
- 46 `JASAN`, 9 `PREGLED`.
- Nije izračunata točnost čitača jer nema njegova PPUG izlaza nakon treniranja; postojeći početni test je 0 prijedloga.
- Pritom oznake nisu konačni potpuni pravni katalog: pojedine nenumeričke i oblikovne odredbe nisu izdvojene kao zasebna pravila.

## Preporučeni evaluacijski postupak

1. Zamrznuti ove oznake i provjeriti SHA-256 učitanog izvornog teksta.
2. Usporediti predložena pravila prema ključu `(clanak, stavak, tocka, vrsta, gradjevina, parametar, vrijednost, jedinica, vrsta_pravila)`, uz prethodno **ručno dogovorenu mapu sinonima** i granularnosti.
3. Razliku između `PREGLED`, propuštenog i pogrešnog bilježiti odvojeno.
4. Svako iznimno pravilo dodatno ocijeniti prema punom uvjetu, ne samo brojci.
5. Provjeriti da se na UPU-u 2 nakon generalizacije ne pojave nova lažno pozitivna pravila.
