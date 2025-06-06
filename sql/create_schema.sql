-- SQL Schema für Autovermietung
-- Exakt nach den vorgegebenen Tabellen

-- Tabelle: preisgruppe
CREATE TABLE preisgruppe (
    id_preisgruppe INT PRIMARY KEY,
    preis_stunde DECIMAL(10,2),
    preis_tag DECIMAL(10,2),
    preis_km DECIMAL(10,2)
);

-- Tabelle: personal
CREATE TABLE personal (
    id_personal INT PRIMARY KEY,
    ma_nachname VARCHAR(50),
    ma_vorname VARCHAR(50),
    telefon VARCHAR(20)
);

-- Tabelle: kunde
CREATE TABLE kunde (
    Kundennumm INT PRIMARY KEY,
    Nachname VARCHAR(30),
    Vorname VARCHAR(30),
    Strasse VARCHAR(50),
    Ort VARCHAR(30),
    PLZ VARCHAR(5),
    Land VARCHAR(30),
    Geburtsdatum DATE,
    Telefon VARCHAR(20)
);

-- Tabelle: auto
CREATE TABLE auto (
    id_auto INT PRIMARY KEY,
    kennzeichen VARCHAR(10),
    hersteller VARCHAR(20),
    typ VARCHAR(30),
    baujahr SMALLINT,
    ps SMALLINT,
    ccm INT,
    farbe VARCHAR(20),
    kraftstoff VARCHAR(10),
    sitzplaetze TINYINT,
    extras VARCHAR(50),
    zubehoer1 VARCHAR(20),
    zubehoer2 VARCHAR(20),
    versicherungs_nr VARCHAR(20),
    tuv DATE,
    asu DATE,
    preisgruppe_id_preisgruppe INT,
    FOREIGN KEY (preisgruppe_id_preisgruppe) REFERENCES preisgruppe(id_preisgruppe)
);

-- Tabelle: verleihdaten
CREATE TABLE verleihdaten (
    ausleihdatum DATE,
    rueckgabedatum DATE,
    anfangs_km INT,
    ende_km INT,
    kunde_id_kunde INT,
    personal_id_personal INT,
    auto_id_auto INT,
    auto_preisgruppe_id_preisgruppe INT,
    FOREIGN KEY (kunde_id_kunde) REFERENCES kunde(Kundennumm),
    FOREIGN KEY (personal_id_personal) REFERENCES personal(id_personal),
    FOREIGN KEY (auto_id_auto) REFERENCES auto(id_auto),
    FOREIGN KEY (auto_preisgruppe_id_preisgruppe) REFERENCES auto(preisgruppe_id_preisgruppe)
);