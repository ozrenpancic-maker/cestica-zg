-- Čestica HR: zahtjevi za napredni pristup, pristupni kodovi, dnevnik administratorskih radnji, sesije,
-- ograničenja učestalosti i skupna (anonimna) statistika. Primjena: npx wrangler d1 migrations apply cesticahr --remote
CREATE TABLE IF NOT EXISTS zahtjev (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL,
  email_h TEXT NOT NULL UNIQUE,          -- sažetak adrese (HMAC) za provjeru višestrukih zahtjeva
  namjena TEXT,                          -- kupujem | gradnja | arhitekt | agencija | investitor | ostalo
  status TEXT NOT NULL,                  -- nepotvrden | ceka | odobren | odbijen | opozvan (istekao se izvodi iz roka)
  stvoren INTEGER NOT NULL,
  potvrda_h TEXT,                        -- sažetak tokena iz e-maila za potvrdu adrese (samo dok nije potvrđeno)
  potvrden INTEGER,
  odluka INTEGER,                        -- vrijeme odobrenja ili odbijanja
  kod_h TEXT UNIQUE,                     -- sažetak pristupnog koda (kod se nigdje ne sprema u čitljivom obliku)
  kod_izdan INTEGER,                     -- vrijeme izdavanja koda; novi kod poništava stari i sve prijave s njim
  kod_rok INTEGER,                       -- do kada se kod može aktivirati
  dana INTEGER,                          -- trajanje od aktivacije; NULL = neograničeno
  aktiviran INTEGER,
  istice INTEGER,                        -- NULL = neograničeno ili još nije aktiviran
  zadnja_akt INTEGER,
  trazi_produzenje INTEGER,
  podsjetnik INTEGER,
  admin_dodao INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS zahtjev_status ON zahtjev(status);
CREATE TABLE IF NOT EXISTS dnevnik (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  t INTEGER NOT NULL,
  akter TEXT NOT NULL,                   -- admin | korisnik | sustav
  radnja TEXT NOT NULL,
  zahtjev_id TEXT,
  detalj TEXT                            -- bez e-mail adresa i kodova
);
CREATE INDEX IF NOT EXISTS dnevnik_z ON dnevnik(zahtjev_id);
CREATE TABLE IF NOT EXISTS sesija (h TEXT PRIMARY KEY, istice INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ogranicenje (k TEXT PRIMARY KEY, n INTEGER NOT NULL, istice INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS postavke (k TEXT PRIMARY KEY, v TEXT);
-- skupna statistika po danu: vrsta događaja i jedna dimenzija (županija ili izvor dolaska); bez korisnika i bez čestica
CREATE TABLE IF NOT EXISTS dogadaj (dan TEXT NOT NULL, vrsta TEXT NOT NULL, dim TEXT NOT NULL DEFAULT '', n INTEGER NOT NULL, PRIMARY KEY (dan, vrsta, dim));
-- jednokratni sažeci za uklanjanje ponovljenih događaja (brišu se nakon jednog dana)
CREATE TABLE IF NOT EXISTS ponavljanje (h TEXT PRIMARY KEY, istice INTEGER NOT NULL);
-- samo uz privolu: sažetak nasumičnog identifikatora preglednika po danu (za povratne korisnike); briše se nakon 90 dana
CREATE TABLE IF NOT EXISTS posjetitelj (dan TEXT NOT NULL, v_h TEXT NOT NULL, PRIMARY KEY (dan, v_h));
