# Realističniji model kuće u 3D pogledu

Stanje 5. 11. 2026., grana `kuca-3d`.

## Što radi

3D pogled kuću iz simulatora crta biblioteka three.js 0.149 (MIT, `vendor/three-0.149.0`). Učitava se tek kad se 3D pogled otvori. Kuća je zaseban sloj u MapLibreu i dijeli dubinu s terenom i okolnim zgradama.

Model ima:
- **krov:** prave plohe (dvostrešni, četverostrešni ili ravni s atikom i opšavom), strehu od 0,5 m, zabatni prepust od 0,4 m, podgled, sljeme, dimnjak, olučne horizontale i vertikale;
- **zidove:** od žbuke s podnožjem; drvena obloga u izgledu »moderni s drvenom oblogom«;
- **otvore:** prozore s okvirom, klupčicom i roletom; ulaz s vratima i nadstrešnicom (kosom ili ravnom) i podestom; staklenu stijenu u prizemlju prema vrtu; prozore u zabatima kad je krov visok;
- **ostalo:** garažu s ravnim krovom i sekcijskim vratima, solarne panele (na ravnom krovu na nosačima, na kosom na kosini prema odabranoj orijentaciji);
- **okoliš:** terasa prema vrtu (kad okućnica nema svoju), kod modernog ravnog krova s pergolom, šljunčani rub uz zidove, kontaktna sjena;
- **balkon** sa staklenom ogradom kad ga model iz kataloga ima: kod katnice na katu prema vrtu, kod kuće s potkrovljem na zabatu;
- **svjetlo:** sunce s istim smjerom kao sjena na tlu, sjene na samoj kući (streha na zidu, nadstrešnica, dimnjak).

Mjere su iste kao u simulatoru: širina, dubina, visina do vijenca, nagib, smjer sljemena i okret. Materijali i raspored prozora samo su ilustracija.

**Teren:** pod kuće je na najnižoj točki terena ispod tlocrta, pa kuća nigdje ne lebdi. Na kosom terenu viša strana ulazi u padinu, a terasa i okućnica uz nižu stranu ostaju u razini poda (odluka 7. 11. 2026., nakon čestice 11098 k.o. Čučerje Novo s nagibom oko 54 %). Pločice terena bez učitanog modela visina se preskaču. Visina se uzima iz pločice terena koju karta u tom trenutku crta: kad se odzumira, karta crta grublji teren (osobito na mobitelu), pa bi kuća inače lebdjela.

Bez WebGL-a, ili ako se biblioteka ne učita, ostaje dosadašnji model od kvadara.

## Testovi

`tests/run.js`, `tri3dTests`: geometrija iz three.js u jsdomu:
- broj ploha krova;
- visina sljemena: vijenac + tg(nagib) × pola raspona;
- prepusti;
- zidovi prema simulatoru;
- ulaz, staklena stijena, obloga, garaža, paneli.

Ukupno 1107 / 1107.
