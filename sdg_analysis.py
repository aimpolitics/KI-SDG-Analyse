import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
import os

def get_sdg_descriptions():
    """Liefert die SDG-Beschreibungen"""
    return {
        "SDG 1": "Keine Armut",
        "SDG 2": "Kein Hunger",
        "SDG 3": "Gesundheit und Wohlergehen",
        "SDG 4": "Hochwertige Bildung",
        "SDG 5": "Geschlechtergleichheit",
        "SDG 6": "Sauberes Wasser und Sanitäreinrichtungen",
        "SDG 7": "Bezahlbare und saubere Energie",
        "SDG 8": "Menschenwürdige Arbeit und Wirtschaftswachstum",
        "SDG 9": "Industrie, Innovation und Infrastruktur",
        "SDG 10": "Weniger Ungleichheiten",
        "SDG 11": "Nachhaltige Städte und Gemeinden",
        "SDG 12": "Nachhaltige/r Konsum und Produktion",
        "SDG 13": "Maßnahmen zum Klimaschutz",
        "SDG 14": "Leben unter Wasser",
        "SDG 15": "Leben an Land",
        "SDG 16": "Frieden, Gerechtigkeit und starke Institutionen",
        "SDG 17": "Partnerschaften zur Erreichung der Ziele"
    }

def load_keyword_data():
    """Lädt die Keyword-Analyse Daten"""
    try:
        with open("data/keyword_analysis.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Daten: {str(e)}")
        return None

def create_sdg_temporal_plot(keyword_data):
    """Erstellt die zeitliche Entwicklung der SDGs"""
    if not keyword_data:
        return None
    
    # Definiere die korrekte chronologische Reihenfolge der Semester
    semester_order = [
        'Sommersemester 2023',
        'Wintersemester 2023',
        'Sommersemester 2024',
        'Wintersemester 2024'
    ]
    
    # Stelle sicher, dass nur verfügbare Semester verwendet werden
    semesters = [sem for sem in semester_order if sem in keyword_data['semester_analyses']]
    sdg_descriptions = get_sdg_descriptions()
    
    # Erstelle ein Dictionary für die Daten
    data = {semester: {} for semester in semesters}
    
    # Fülle die Daten
    for semester, analysis in keyword_data['semester_analyses'].items():
        if semester in semesters:  # Nur Daten für die definierten Semester verwenden
            for sdg in sdg_descriptions.keys():
                # Hole die Anzahl der Kurse für dieses SDG (0 wenn nicht vorhanden)
                courses = len(analysis.get('sdg_distribution', {}).get(sdg, {}).get('courses', []))
                data[semester][sdg] = courses
    
    # Erstelle die Matplotlib-Figur
    plt.figure(figsize=(15, 10))
    
    # Füge eine Linie für jedes SDG hinzu
    for sdg, description in sdg_descriptions.items():
        y_values = [data[sem][sdg] for sem in semesters]
        plt.plot(range(len(semesters)), y_values, marker='o', label=f"{sdg} - {description}")
    
    # Layout anpassen
    plt.title('Zeitliche Entwicklung der SDG-Bezüge in Kursen', pad=20, size=14)
    plt.xlabel('Semester')
    plt.ylabel('Anzahl Kurse')
    
    # X-Achsen-Labels anpassen
    plt.xticks(range(len(semesters)), semesters, rotation=45)
    
    # Legende außerhalb des Plots
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    
    # Layout optimieren
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    return plt.gcf()

def save_plot(fig, filename):
    """Speichert die Grafik als PNG"""
    # Erstelle Plots-Ordner, falls nicht vorhanden
    Path("plots").mkdir(exist_ok=True)
    
    # Speichere als PNG in hoher Auflösung
    fig.savefig(f"plots/{filename}.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

def create_metrics_table(keyword_data):
    """Erstellt eine Tabelle mit den wichtigsten Kennzahlen pro Semester"""
    if not keyword_data:
        return None
    
    metrics = []
    for semester, analysis in keyword_data['semester_analyses'].items():
        # Sammle alle SDG-Bezüge für dieses Semester
        sdg_counts = Counter()
        all_courses = set()  # Set für alle Kurse mit SDG-Bezügen
        
        # Zähle die SDG-Bezüge und sammle die Kurse
        for sdg, data in analysis.get('sdg_distribution', {}).items():
            courses = data.get('courses', [])
            sdg_counts[sdg] = len(courses)
            for course in courses:
                all_courses.add(course['number'])  # Verwende die Kursnummer als eindeutigen Identifier
        
        # Berechne die Kennzahlen
        total_courses = analysis.get('total_courses', 0)
        courses_with_sdg_count = len(all_courses)
        avg_sdgs_per_course = sum(sdg_counts.values()) / total_courses if total_courses > 0 else 0
        
        # Finde das häufigste SDG
        most_common_sdg = max(sdg_counts.items(), key=lambda x: x[1])[0] if sdg_counts else "Keine"
        
        metrics.append({
            'Semester': semester,
            'Gesamtzahl Kurse': total_courses,
            'Kurse mit SDG-Bezug': courses_with_sdg_count,
            'Anteil Kurse mit SDG (%)': round(courses_with_sdg_count / total_courses * 100, 1) if total_courses > 0 else 0,
            'Ø SDGs pro Kurs': round(avg_sdgs_per_course, 2),
            'Häufigstes SDG': most_common_sdg
        })
    
    # Erstelle DataFrame und speichere als CSV
    df = pd.DataFrame(metrics)
    Path("plots").mkdir(exist_ok=True)
    df.to_csv('plots/semester_metrics.csv', index=False)
    
    return df

def create_sdg_distribution_plot(keyword_data, target_semester):
    """Erstellt ein Balkendiagramm der SDG-Verteilung für ein bestimmtes Semester"""
    if not keyword_data or target_semester not in keyword_data['semester_analyses']:
        return None
    
    # Hole die Daten für das Zielsemester
    semester_data = keyword_data['semester_analyses'][target_semester]
    sdg_descriptions = get_sdg_descriptions()
    
    # Sammle die Anzahl der Kurse pro SDG
    sdg_counts = []
    sdg_labels = []
    
    for sdg, description in sdg_descriptions.items():
        count = len(semester_data.get('sdg_distribution', {}).get(sdg, {}).get('courses', []))
        if count > 0:  # Nur SDGs mit mindestens einem Kurs anzeigen
            sdg_counts.append(count)
            sdg_labels.append(f"{sdg}\n{description}")
    
    # Sortiere die Daten nach Anzahl (absteigend)
    sorted_data = sorted(zip(sdg_counts, sdg_labels), reverse=True)
    sdg_counts, sdg_labels = zip(*sorted_data)
    
    # Erstelle die Matplotlib-Figur
    plt.figure(figsize=(15, 8))
    
    # Erstelle das Balkendiagramm
    bars = plt.bar(range(len(sdg_counts)), sdg_counts)
    
    # Layout anpassen
    plt.title(f'Verteilung der SDG-Bezüge in Kursen ({target_semester})', pad=20, size=14)
    plt.xlabel('Sustainable Development Goals (SDGs)')
    plt.ylabel('Anzahl Kurse')
    
    # X-Achsen-Labels anpassen
    plt.xticks(range(len(sdg_counts)), sdg_labels, rotation=45, ha='right')
    
    # Füge Werte über den Balken hinzu
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    # Layout optimieren
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    return plt.gcf()

def create_course_keyword_table(keyword_data):
    """Erstellt eine Tabelle mit Kursen und gefundenen Schlagwörtern für alle Semester"""
    if not keyword_data:
        return None
    
    print("\nVerfügbare Semester:", list(keyword_data['semester_analyses'].keys()))
    
    # Erstelle eine Liste aller Kurse und ihrer Schlagwörter
    courses_data = []
    
    # Gehe durch alle Semester
    for semester, semester_data in keyword_data['semester_analyses'].items():
        print(f"\nVerarbeite {semester}...")
        
        # Hole alle Kurse des Semesters aus der neuesten courses_*.json Datei
        semester_code = semester.split()[-1]
        if semester.startswith('Wintersemester'):
            semester_dir = f"data/semester_WS{semester_code}"
        else:
            semester_dir = f"data/semester_SS{semester_code}"
            
        course_files = [f for f in os.listdir(semester_dir) 
                       if f.startswith('courses_') and f.endswith('.json')]
        if not course_files:
            print(f"Keine Kursdaten gefunden für {semester}")
            continue
            
        latest_course_file = max(course_files)
        with open(os.path.join(semester_dir, latest_course_file), 'r', encoding='utf-8') as f:
            all_courses = json.load(f)['courses']
        
        print(f"Gesamtzahl Kurse: {len(all_courses)}")
        
        # Erstelle ein Dictionary für schnellen Zugriff auf SDGs und Keywords pro Kurs
        course_sdgs = {}
        course_keywords = {}
        
        # Sammle SDGs und Keywords für jeden Kurs mit SDG-Bezügen
        for sdg, sdg_data in semester_data.get('sdg_distribution', {}).items():
            for course in sdg_data.get('courses', []):
                if not isinstance(course, dict) or 'number' not in course:
                    continue
                    
                course_number = course['number']
                if course_number not in course_sdgs:
                    course_sdgs[course_number] = set()
                    course_keywords[course_number] = set()
                course_sdgs[course_number].add(sdg)
                if 'found_keywords' in course:
                    course_keywords[course_number].update(course['found_keywords'])
        
        # Erstelle Einträge für ALLE Kurse
        for course in all_courses:
            course_number = course.get('number', 'N/A')
            
            # Prüfe auf fehlende oder leere Felder
            missing_fields = []
            if not course.get('title', '').strip():
                missing_fields.append('Titel')
            if not course.get('objectives_and_content', '').strip():
                missing_fields.append('Inhalt')
            
            # Bestimme Status und Grund
            if course_number in course_sdgs:
                status = "Analysiert"
                sdgs = ', '.join(sorted(course_sdgs[course_number]))
                keywords = ', '.join(sorted(course_keywords[course_number]))
            else:
                if missing_fields:
                    status = f"Nicht analysierbar - Fehlende Felder: {', '.join(missing_fields)}"
                    sdgs = "Keine Analyse möglich"
                    keywords = "Keine Analyse möglich"
                else:
                    status = "Analysiert - Keine SDGs gefunden"
                    sdgs = "Keine"
                    keywords = "Keine"
            
            courses_data.append({
                'Semester': semester,
                'Kursnummer': course_number,
                'Kurstitel': course.get('title', 'N/A'),
                'Kurstyp': course.get('type', 'N/A'),
                'Status': status,
                'SDGs': sdgs,
                'Gefundene Schlagwörter': keywords
            })
    
    if not courses_data:
        print("\nKeine Kursdaten gefunden!")
        return None
    
    # Erstelle DataFrame
    df = pd.DataFrame(courses_data)
    print(f"\nErstellte Tabelle mit {len(df)} Einträgen")
    print("Verfügbare Spalten:", df.columns.tolist())
    
    # Sortiere nach Semester und Kursnummer
    try:
        semester_order = ['Wintersemester 2023', 'Sommersemester 2024', 'Wintersemester 2024']
        df['Semester'] = pd.Categorical(df['Semester'], categories=semester_order, ordered=True)
        df = df.sort_values(['Semester', 'Kursnummer'])
    except Exception as e:
        print(f"\nFehler beim Sortieren: {str(e)}")
        print("Fahre ohne Sortierung fort...")
    
    # Speichere als CSV
    Path("plots").mkdir(exist_ok=True)
    df.to_csv('plots/kurse_schlagworte_alle_semester.csv', index=False, encoding='utf-8')
    print("\nTabelle wurde gespeichert als: plots/kurse_schlagworte_alle_semester.csv")
    
    # Erstelle Statistik über die Analyse-Status
    print("\nAnalyse-Status pro Semester:")
    status_stats = df.groupby(['Semester', 'Status']).size().unstack(fill_value=0)
    print(status_stats)
    
    return df

def main():
    # Lade Daten
    keyword_data = load_keyword_data()
    if not keyword_data:
        return
    
    # Erstelle und speichere Plot
    fig = create_sdg_temporal_plot(keyword_data)
    if fig:
        save_plot(fig, "sdg_entwicklung")
        print("Grafik wurde gespeichert als:")
        print("- plots/sdg_entwicklung.png")
    
    # Erstelle und speichere SDG-Verteilung für WS 2024
    fig_dist = create_sdg_distribution_plot(keyword_data, "Wintersemester 2024")
    if fig_dist:
        save_plot(fig_dist, "sdg_verteilung_ws2024")
        print("\nSDG-Verteilung wurde gespeichert als:")
        print("- plots/sdg_verteilung_ws2024.png")
    
    # Erstelle und zeige Kennzahlen
    metrics_df = create_metrics_table(keyword_data)
    if metrics_df is not None:
        print("\nKennzahlen pro Semester:")
        print(metrics_df.to_string(index=False))
        print("\nDie Kennzahlen wurden gespeichert als:")
        print("- plots/semester_metrics.csv")
    
    # Erstelle und zeige Kurs-Schlagwort-Tabelle für alle Semester
    course_keyword_df = create_course_keyword_table(keyword_data)
    if course_keyword_df is not None:
        print("\nKurse und Schlagwörter (Auszug der ersten 20 Zeilen):")
        print(course_keyword_df.head(20).to_string(index=False))
        print("\n... (weitere Einträge)")
        print("\nDie vollständige Kurs-Schlagwort-Tabelle wurde gespeichert als:")
        print("- plots/kurse_schlagworte_alle_semester.csv")

if __name__ == "__main__":
    main() 