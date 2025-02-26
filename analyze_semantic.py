import json
from semantic_analysis import SemanticSDGAnalyzer
from pathlib import Path
from datetime import datetime
import os

def analyze_courses_semantic():
    """
    Führt eine rein semantische Analyse der Kurse durch.
    Speichert die Ergebnisse in einer separaten JSON-Datei.
    """
    print("="*80)
    print("Starte semantische Analyse der Kurse")
    print("="*80)
    
    # Initialisiere semantischen Analyzer
    analyzer = SemanticSDGAnalyzer()
    data_dir = Path("data")
    
    # Finde alle Semester-Verzeichnisse
    semester_dirs = [d for d in os.listdir(data_dir) 
                    if os.path.isdir(data_dir / d) 
                    and d.startswith('semester_')]
    
    semantic_results = {}
    
    for semester_dir in sorted(semester_dirs, reverse=True):
        print(f"\nAnalysiere {semester_dir}...")
        
        # Lade Semester-Info
        with open(data_dir / semester_dir / 'semester_info.json', 'r', encoding='utf-8') as f:
            semester_info = json.load(f)
        
        # Finde neueste Kursdatei
        course_files = [f for f in os.listdir(data_dir / semester_dir) 
                       if f.startswith('courses_') and f.endswith('.json')]
        if not course_files:
            continue
            
        latest_course_file = max(course_files)
        
        # Lade Kursdaten
        with open(data_dir / semester_dir / latest_course_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            courses = data['courses']
        
        # Analysiere jeden Kurs semantisch
        semester_results = []
        for course in courses:
            course_text = ' '.join([
                course.get('title', ''),
                course.get('subtitle', ''),
                course.get('objectives_and_content', '')
            ])
            
            semantic_matches = analyzer.analyze_text(course_text)
            if semantic_matches:
                course_result = {
                    'course_info': {
                        'title': course.get('title', ''),
                        'type': course.get('type', ''),
                        'ects': course.get('ects', None),
                        'url': course.get('url', '')
                    },
                    'semantic_matches': semantic_matches
                }
                semester_results.append(course_result)
        
        semantic_results[semester_info['semester_name']] = {
            'semester_info': semester_info,
            'courses': semester_results
        }
        
        print(f"  ✓ {len(semester_results)} Kurse analysiert")
    
    # Speichere Gesamtergebnisse
    output = {
        'semantic_analysis': semantic_results,
        'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model_info': {
            'name': analyzer.model_name,
            'threshold': analyzer.threshold_config
        }
    }
    
    output_file = data_dir / 'semantic_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\nAnalyse abgeschlossen!")
    print(f"Ergebnisse wurden in {output_file} gespeichert.")
    print("="*80)

if __name__ == "__main__":
    analyze_courses_semantic() 