#!/usr/bin/env python3
"""
etl_load.py  Ein durchgängiges ETL-Skript für Altdaten

    ▸ liest eine oder mehrere Excel-Dateien (Pattern: INPUT_PATTERN)
    ▸ bereinigt Datumsfelder (Liste DATE_COLS → Format YYYY-MM-DD)
    ▸ speichert jedes Blatt als CSV in einen Ordner out/
    ▸ führt alle Blätter zu einem DataFrame zusammen und legt es in
      LOAD DATA.xlsx / Karte7 ab
    ▸ (optional) lädt die Daten direkt in eine MariaDB-Tabelle

Voraussetzungen:
    pip install pandas openpyxl sqlalchemy mariadb
"""

from pathlib import Path
import sys

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


# ───────────────────────────────
# 1) KONFIGURATION
# ───────────────────────────────
INPUT_PATTERN: str = "customers_clean.xlsx"        # z. B. "input/*.xlsx"
CSV_DIR: Path = Path("out")                        # Ablageort für CSVs
OUTPUT_BOOK: Path = Path("LOAD DATA.xlsx")         # Sammel-Arbeitsmappe
OUTPUT_SHEET: str = "Karte7"                       # Ziel-Sheet in OUTPUT_BOOK
DATE_COLS: list[str] = ["Geburtsdatum"]            # zu säubernde Datumsspalten

DB_CFG: dict = {                                   # Direkt-Upload (optional)
    "host": "127.0.0.1",
    "port": 3306,
    "user": "app_user",
    "password": "secret",
    "database": "crm",
    "table": "customers",
    "if_exists": "replace",                        # 'append', 'replace', 'fail'
}
DO_DB_UPLOAD: bool = False                         # True = to_sql ausführen


# ───────────────────────────────
# 2) HILFSFUNKTIONEN
# ───────────────────────────────
def clean_date(val: object) -> str | None:
    """
    Konvertiert einen beliebigen Datumswert in das Format YYYY-MM-DD.
    Nicht interpretierbare Werte → None.
    """
    ts = pd.to_datetime(val, errors="coerce")
    return ts.strftime("%Y-%m-%d") if not pd.isna(ts) else None


def read_excel_files(pattern: str) -> list[tuple[str, pd.DataFrame]]:
    """
    Liest alle Excel-Dateien, die auf das Pattern passen, inklusive
    sämtlicher Tabellenblätter.

    Returns
    -------
    list[(name, df)]
        name = "Dateiname_Sheetname"
        df   = DataFrame des Blattes
    """
    files = list(Path().glob(pattern))
    if not files:
        sys.exit(f"[ABBRUCH] Keine Dateien passend zu {pattern!r} gefunden.")

    dataframes: list[tuple[str, pd.DataFrame]] = []
    for fp in files:
        # sheet_name=None liest alle Blätter als Dict[str, DataFrame]
        workbook = pd.read_excel(fp, sheet_name=None)
        for sheet_name, df in workbook.items():
            # Zusatzspalten, um Herkunft im Datensatz sichtbar zu machen
            df["__source_file"] = fp.name
            df["__source_sheet"] = sheet_name
            dataframes.append((f"{fp.stem}_{sheet_name}", df))
    return dataframes


def write_csv(csv_dir: Path, name: str, df: pd.DataFrame) -> None:
    """Speichert ein DataFrame im angegebenen Ordner als UTF-8-CSV."""
    csv_dir.mkdir(exist_ok=True)
    csv_path = csv_dir / f"{name}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"  ⇢ CSV geschrieben: {csv_path}")


def merge_to_excel(df: pd.DataFrame, xlsx_path: Path, sheet_name: str) -> None:
    """
    Schreibt das DataFrame in 'xlsx_path' → 'sheet_name'.
    Existiert die Datei bereits, wird das Blatt ersetzt.
    """
    mode = "a" if xlsx_path.exists() else "w"
    with pd.ExcelWriter(
        xlsx_path,
        engine="openpyxl",
        mode=mode,
        if_sheet_exists="replace",
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"✔ Excel-Export beendet → {xlsx_path} / {sheet_name}")


def upload_to_db(df: pd.DataFrame, cfg: dict) -> None:
    """Lädt ein DataFrame via pandas.to_sql direkt in MariaDB."""
    url = (
        f"mariadb+mariadbconnector://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}?charset=utf8mb4"
    )
    engine = create_engine(url, echo=False, future=True)
    try:
        df.to_sql(
            cfg["table"],
            con=engine,
            if_exists=cfg["if_exists"],
            index=False,
            chunksize=1_000,
            method="multi",
        )
        print(f"✔ {len(df):,} Zeilen in MariaDB-Tabelle {cfg['table']!r} importiert")
    except SQLAlchemyError as exc:
        sys.exit(f"[ABBRUCH] Upload nach MariaDB fehlgeschlagen: {exc}")


# ───────────────────────────────
# 3) HAUPTPROZESS
# ───────────────────────────────
def main() -> None:
    """Steuert den kompletten ETL-Ablauf."""
    # 3.1 Excel-Dateien einlesen
    frames = read_excel_files(INPUT_PATTERN)

    merged_rows: list[pd.DataFrame] = []  # für Sammel-Export / DB-Import

    for name, df in frames:
        print(f"→ Verarbeite Blatt {name!r}: {len(df):,} Zeilen")

        # 3.2 Datums-Bereinigung
        for col in DATE_COLS:
            if col in df.columns:
                df[col] = df[col].apply(clean_date)
                print(f"    • Spalte {col!r} bereinigt")
            else:
                print(f"    • Warnung: Spalte {col!r} nicht vorhanden")

        # 3.3 Einzel-CSV ablegen
        write_csv(CSV_DIR, name, df)

        # 3.4 DataFrame für Gesamtausgabe sammeln
        merged_rows.append(df)

    # 3.5 DataFrames zusammenführen
    merged_df = pd.concat(merged_rows, ignore_index=True)
    print(f"✔ Zusammengeführt: {len(merged_df):,} Gesamtzeilen")

    # 3.6 In LOAD DATA.xlsx / Karte7 schreiben
    merge_to_excel(merged_df, OUTPUT_BOOK, OUTPUT_SHEET)

    # 3.7 Optional: Direkt in MariaDB einspielen
    if DO_DB_UPLOAD:
        upload_to_db(merged_df, DB_CFG)
    else:
        # Alternativ: LOAD DATA LOCAL INFILE-Snippet ausgeben
        print("\n--- MariaDB-Beispiel (LOAD DATA LOCAL INFILE) ------------------")
        print(f"""\
LOAD DATA LOCAL INFILE '{CSV_DIR / "*.csv"}'
INTO TABLE {DB_CFG['database']}.{DB_CFG['table']}
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' ENCLOSED BY '\"'
LINES TERMINATED BY '\\n'
IGNORE 1 ROWS;""")


# ───────────────────────────────
# 4) Skripteinstieg
# ───────────────────────────────
if __name__ == "__main__":
    main()
