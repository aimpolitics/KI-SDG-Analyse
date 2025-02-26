# SDG-Analyse von Lehrveranstaltungen

Dieses Projekt analysiert Lehrveranstaltungen der Universität Wien auf ihre Bezüge zu den UN Sustainable Development Goals (SDGs). Es verwendet sowohl eine keyword-basierte als auch eine semantische Analyse mittels KI.

## Projektstruktur

### Hauptskripte

1. **main.py**
   - Zentraler Einstiegspunkt für die Datenerfassung
   - Orchestriert die Ausführung der Extraktions- und Analyseskripte
   - Führt die Skripte in der richtigen Reihenfolge aus:
     1. extract_course_links.py
     2. extract_course_info.py
     3. analyze_sdgs.py

2. **extract_course_links.py**
   - Extrahiert Links zu allen Lehrveranstaltungen eines Semesters
   - Speichert die Links in `course_links.json`
   - Basis für die spätere detaillierte Kursextraktion

3. **extract_course_info.py**
   - Crawlt die detaillierten Informationen für jeden Kurs
   - Verarbeitet die Links aus `course_links.json`
   - Speichert Kursinformationen in `courses_[TIMESTAMP].json`

4. **analyze_sdgs.py**
   - Führt die keyword-basierte SDG-Analyse durch
   - Verwendet Schlagwörter aus `sdg_keywords.py`
   - Speichert Ergebnisse in `keyword_analysis.json`

5. **analyze_semantic.py** & **semantic_analysis.py**
   - Führt die KI-basierte semantische Analyse durch
   - Verwendet das BERT-Modell "deepset/gbert-large"
   - Speichert Ergebnisse in `semantic_analysis.json`

6. **sdg_analysis.py**
   - Erstellt Visualisierungen und Statistiken
   - Generiert:
     - Zeitliche Entwicklung der SDG-Bezüge
     - SDG-Verteilung pro Semester
     - Kennzahlen und Metriken
   - Speichert Ergebnisse im `plots/` Verzeichnis

7. **visualize_semantic.py**
   - Visualisiert die Ergebnisse der semantischen Analyse
   - Erstellt Heatmaps der semantischen Ähnlichkeiten
   - Vergleicht semantische und keyword-basierte Analyse
   - Generiert detaillierte Kursanalysen

### Unterstützende Dateien

- **sdg_keywords.py**
  - Enthält die Schlagwörter für die SDG-Zuordnung
  - Definiert die Mapping-Logik zwischen Keywords und SDGs

### Datenstruktur

```
data/
├── keyword_analysis.json     # Ergebnisse der Keyword-Analyse
├── semantic_analysis.json    # Ergebnisse der semantischen Analyse
├── course_info_summary.json  # Zusammenfassung der Kursinformationen
└── semester_[CODE]/         # Semesterspezifische Daten
    ├── semester_info.json   # Metadaten zum Semester
    ├── course_links.json    # Extrahierte Kurs-URLs
    └── courses_*.json       # Detaillierte Kursinformationen

plots/
├── sdg_entwicklung.png              # Zeitliche Entwicklung
├── sdg_verteilung_*.png             # SDG-Verteilung pro Semester
├── semester_metrics.csv             # Kennzahlen pro Semester
├── semantic_heatmap_*.png           # Semantische Ähnlichkeiten
└── analysis_comparison_*.png        # Vergleich der Analysemethoden
```

## Ausführung

1. **Virtuelle Umgebung erstellen und aktivieren:**
   ```bash
   # Virtuelle Umgebung erstellen
   python -m venv .venv

   # Unter Windows aktivieren
   .venv\Scripts\activate

   # Unter Linux/Mac aktivieren
   source .venv/bin/activate
   ```

2. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Datenerfassung:**
   ```bash
   python main.py
   ```

4. **SDG-Analyse:**
   ```bash
   python sdg_analysis.py
   ```

5. **Semantische Analyse:**
   ```bash
   python analyze_semantic.py
   ```

6. **Visualisierung:**
   ```bash
   python visualize_semantic.py
   ```


## Methodologie

### Keyword-basierte Analyse
- Sucht nach definierten Schlagwörtern in Kurstexten
- Direkte Zuordnung zu SDGs basierend auf Keyword-Matches
- Präzise, aber möglicherweise eingeschränkt

### Semantische Analyse
- Verwendet KI (BERT) für kontextbasierte Analyse
- Erkennt auch implizite thematische Verbindungen
- Berechnet Ähnlichkeiten zwischen Kursinhalten und SDG-Beschreibungen

## Ergebnisse

Die Ergebnisse werden in verschiedenen Formaten gespeichert:
- CSV-Dateien für quantitative Analysen
- PNG-Dateien für Visualisierungen
- JSON-Dateien für detaillierte Analyseergebnisse

Alle Visualisierungen werden im `plots/` Verzeichnis gespeichert und bieten verschiedene Perspektiven auf die SDG-Abdeckung in den Lehrveranstaltungen.

## Datenerfassung

### Kurs-URLs hinzufügen
Die URLs der zu analysierenden Kurse müssen in `extract_course_links.py` eingefügt werden:

```python
# In extract_course_links.py
COURSE_URLS = [
    "https://ufind.univie.ac.at/de/course.html?lv=...",
    "https://ufind.univie.ac.at/de/course.html?lv=...",
    # Weitere Kurs-URLs hier einfügen
]
```

### Ausführungsreihenfolge
1. **Kurs-Links extrahieren:**
   ```bash
   python extract_course_links.py
   ```
   Erstellt `course_links.json`

2. **Kursdetails extrahieren:**
   ```bash
   python extract_course_info.py
   ```
   Erstellt `courses_[TIMESTAMP].json`

3. **Semantische Analyse durchführen:**
   ```bash
   python analyze_semantic.py
   ```
   Erstellt `semantic_analysis.json`

4. **Konfidenzintervalle visualisieren:**
   ```bash
   python visualize_semantic.py
   ```
   Erstellt `plots/confidence_intervals.png` 