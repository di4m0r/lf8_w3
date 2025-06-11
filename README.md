<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
</head>
<body>
  <h1>AntiQue Fahrzeugvermietung – Datenbank‑Rebuild</h1>
  <p><strong>Lernfeld&nbsp;8 · Woche&nbsp;3</strong><br>
     Fachinformatiker: Systemintegration (FI‑SI)</p>

  <h2>🚗 Projekt‑Overview</h2>
  <table>
    <tr><th>Scope</th><td>Fuhrpark, Kunden, Personal, Preisgruppen, Verleihdaten<br><em>Kein</em> Werkstatt‑Modul (separate DB)</td></tr>
    <tr><th>Erwartetes Ergebnis</th><td>MariaDB‑Instanz mit Schema&nbsp;v1, ETL‑Skripten, Views &amp; Prozeduren + Kurz‑Doku</td></tr>
  </table>

  <h2>🗺️ Roadmap Woche&nbsp;3</h2>
  <table>
    <thead>
      <tr><th>Tag</th><th>Milestone</th><th>Deliverable</th></tr>
    </thead>
    <tbody>
      <tr><td><strong>Mo</strong></td><td>Kick‑off 📋 &amp; Infra Setup 🐳</td><td><code>_docs/Projekt-Steckbrief.md</code> · laufender Docker‑Container</td></tr>
      <tr><td><strong>Di</strong></td><td>ER‑Modell ✔️</td><td><code>drawio/antiQue.erdiagram</code></td></tr>
      <tr><td><strong>Mi</strong></td><td>DDL‑Script 💾</td><td><code>sql/create_schema.sql</code> · DB deploy</td></tr>
      <tr><td><strong>Do</strong></td><td>ETL‑Import 🔄</td><td><code>python/etl_load.py</code> · Daten gefüllt</td></tr>
      <tr><td><strong>Fr</strong></td><td>Views &amp; Procs 📈</td><td><code>sql/create_views.sql</code> · <code>sql/proc_rental.sql</code></td></tr>
    </tbody>
  </table>

  <h2>🛠️ Tech‑Stack</h2>
  <table>
    <thead><tr><th>Layer</th><th>Technische Wahl</th></tr></thead>
    <tbody>
      <tr><td>Datenbank</td><td><strong>MariaDB 10.11</strong> (Docker‑Image: <code>mariadb:10.11</code>)</td></tr>
      <tr><td>Scripting</td><td>Python 3.11 + pandas, mysql‑connector‑python</td></tr>
      <tr><td>Diagramme</td><td>draw.io (Database Toolkit)</td></tr>
    </tbody>
  </table>

  <h2>📁 Repository‑Struktur</h2>
  <pre><code>.
├─ sql/
│   ├─ create_schema.sql       # Tabellen &amp; Constraints
│   ├─ create_views.sql        # Standard-Sichten
│   └─ proc_rental.sql         # SP: verleihen(), zurücknehmen()
├─ python/
│   └─ etl_load.py             # Excel → CSV → DB Import
├─ data/
│   ├─ raw/                    # Original-Excel-Backups (nicht im Git)
│   └─ staging/                # temporäre CSVs (gitignored)
├─ drawio/                     # ER-Diagramm-Quelle
└─ README.md                   # Dieses File</code></pre>

  <h2>⚙️ Setup &amp; Start</h2>
  <ol>
    <li><strong>Clone</strong> das Repo</li>
    <li><strong>.env</strong> anlegen (siehe <code>.env.example</code>)</li>
    <li><strong>Docker</strong> hochfahren
      <pre><code>docker compose up -d db</code></pre></li>
    <li><strong>Schema</strong> einspielen
      <pre><code>docker exec -i antique-db mariadb -uroot -p$MYSQL_ROOT_PASSWORD &lt; sql/create_schema.sql</code></pre></li>
    <li><strong>ETL</strong> starten
      <pre><code>python python/etl_load.py --source ./data/raw --db antique_db</code></pre>
      <p><em>Alle Befehle funktionieren auch ohne Docker, wenn MariaDB lokal läuft.</em></p>
    </li>
  </ol>

  <h2>🔄 Datenmigration (ETL‑Flow)</h2>
  <pre><code class="mermaid">flowchart TD
    Excel[Excel-Backups] -->|pandas| CSV[Staging-CSVs]
    CSV -->|LOAD DATA| MariaDB[(MariaDB Schema v1)]
    MariaDB --> QA[Test-SQL]</code></pre>
  <ul>
    <li><strong>Duplicate Check</strong>: Kundennummer + Name</li>
    <li><strong>Datums-Normalisierung</strong>: <code>dd.mm.yyyy</code> → <code>yyyy-mm-dd</code></li>
    <li><strong>FK-Validation</strong>: auto / preisgruppe / kunde / personal</li>
  </ul>

  <h2>🗄️ Schema Snippets</h2>
  <pre><code>CREATE TABLE kunde (
    Kundennumm INT PRIMARY KEY,
    Nachname VARCHAR(30),
    Vorname VARCHAR(30),
    Strasse VARCHAR(50),
    Ort VARCHAR(30),
    PLZ VARCHAR(5),
    Land VARCHAR(30),
    Geburtsdatum DATE,
    Telefon VARCHAR(20)
);</code></pre>
  <p>Vollständiges Schema siehe <code>sql/create_schema.sql</code>.</p>

  <h2>✅ Tests &amp; Quality</h2>
  <ul>
    <li><strong>Unit-Tests</strong>: <code>tests/test_views.sql</code> (GitHub Action)</li>
    <li><strong>Coverage</strong>: Mindestwert 80 %</li>
    <li><strong>SQLLint</strong>: <code>sqlfluff lint sql/</code></li>
  </ul>

  <h2>👥 Contributing</h2>
  <ol>
    <li>Feature‑Branch aus <code>dev</code> erstellen</li>
    <li>Meaningful Commits mit konventionellem Prefix (<code>feat:</code>, <code>fix:</code> …)</li>
    <li>Pull‑Request + SQL‑Unit‑Tests</li>
  </ol>
  <p><em>Code of Conduct</em> und PR‑Template liegen im Ordner <code>.github/</code>.</p>

  <h2>🎓 Lernfeld‑Bezug (LF 8)</h2>
  <ul>
    <li><strong>Datenbanken anpassen, sichern, wiederherstellen</strong> – Schema‑Design, Normalisierung, DDL + DML</li>
    <li><strong>Schnittstellen entwickeln &amp; nutzen</strong> – Python‑ETL, Stored Procedures, Views</li>
    <li><strong>Systemdokumentation erstellen</strong> – ER‑Diagramm, README, Install‑Guide</li>
  </ul>

  <h2>📝 Lizenz</h2>
  <p>Dieses Ausbildungsprojekt steht unter der <strong>MIT‑Lizenz</strong>; siehe <code>LICENSE</code>.</p>
</body>
</html>
