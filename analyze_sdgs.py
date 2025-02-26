import json
from sdg_keywords import SDG_KEYWORDS
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import os
from datetime import datetime

def normalize_text(text: str) -> str:
    """Text für besseres Matching normalisieren."""
    if not text:
        return ""
    # Konvertiere Text zu Kleinbuchstaben
    text = text.lower()
    # Ersetze Umlaute
    text = text.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    return text

def find_sdgs_in_text(text: str) -> Dict[str, Set[str]]:
    """
    SDGs in einem Text basierend auf Keywords finden.
    Gibt ein Dictionary zurück mit SDGs als Schlüssel und gefundenen Keywords als Werte.
    Verwendet Wortgrenzen für exakte Übereinstimmungen.
    """
    text = normalize_text(text)
    # Teile Text in Wörter auf
    words = set(re.findall(r'\b\w+\b', text))
    sdg_findings = {}
    
    for sdg, info in SDG_KEYWORDS.items():
        found_keywords = set()
        for keyword in info['keywords']:
            # Normalisiere auch das Keyword
            normalized_keyword = normalize_text(keyword)
            # Prüfe auf exakte Wortübereinstimmung
            if normalized_keyword in words:
                found_keywords.add(keyword)
            # Prüfe auch auf Phrasen (für Keywords mit mehreren Wörtern)
            elif len(normalized_keyword.split()) > 1:
                if normalized_keyword in text:
                    found_keywords.add(keyword)
        if found_keywords:
            sdg_findings[sdg] = found_keywords
    
    return sdg_findings

def analyze_course(course: Dict) -> Dict[str, Set[str]]:
    """
    Analysiert einen einzelnen Kurs auf SDG-Relevanz basierend auf Keywords.
    
    Returns:
        Dict mit SDGs als Schlüssel und gefundenen Keywords als Werte
    """
    return find_sdgs_in_text(' '.join([
        course.get('title', ''),
        course.get('subtitle', ''),
        course.get('objectives_and_content', '')
    ]))

def analyze_semester_data(semester_path: str) -> Dict:
    """
    Analysiert die Daten eines Semesters und gibt strukturierte Analyseergebnisse zurück.
    """
    # Lade Semester-Info
    with open(os.path.join(semester_path, 'semester_info.json'), 'r', encoding='utf-8') as f:
        semester_info = json.load(f)
    
    # Finde neueste Kursdatei
    course_files = [f for f in os.listdir(semester_path) 
                   if f.startswith('courses_') and f.endswith('.json')]
    if not course_files:
        return None
        
    latest_course_file = max(course_files)
    
    # Lade Kursdaten
    with open(os.path.join(semester_path, latest_course_file), 'r', encoding='utf-8') as f:
        data = json.load(f)
        courses = data['courses']
    
    # Analysiere Kurse
    sdg_analysis = defaultdict(list)
    for course in courses:
        sdg_findings = analyze_course(course)
        for sdg, found_keywords in sdg_findings.items():
            course_with_keywords = course.copy()
            course_with_keywords['found_keywords'] = list(found_keywords)
            sdg_analysis[sdg].append(course_with_keywords)
    
    # Erstelle Analysezusammenfassung
    analysis_summary = {
        'semester_info': semester_info,
        'total_courses': len(courses),
        'sdg_distribution': {
            sdg: {
                'count': len(courses_list),
                'percentage': (len(courses_list) / len(courses)) * 100,
                'courses': courses_list,
                'all_found_keywords': sorted(set(
                    keyword
                    for course in courses_list
                    for keyword in course['found_keywords']
                ))
            }
            for sdg, courses_list in sdg_analysis.items()
        },
        'courses_without_sdgs': [
            course for course in courses
            if not analyze_course(course)
        ],
        'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return analysis_summary

def analyze_all_semesters() -> Dict:
    """
    Analysiert alle Semester und erstellt eine Gesamtanalyse.
    """
    data_dir = 'data'
    
    # Finde alle Semester-Verzeichnisse
    semester_dirs = [d for d in os.listdir(data_dir) 
                    if os.path.isdir(os.path.join(data_dir, d)) 
                    and d.startswith('semester_')]
    
    # Analysiere jedes Semester
    all_analyses = {}
    for semester_dir in sorted(semester_dirs, reverse=True):  # Neueste zuerst
        semester_path = os.path.join(data_dir, semester_dir)
        analysis = analyze_semester_data(semester_path)
        
        if analysis:
            semester_name = analysis['semester_info']['semester_name']
            all_analyses[semester_name] = analysis
    
    # Erstelle Gesamtanalyse
    total_analysis = {
        'semester_analyses': all_analyses,
        'overall_statistics': {
            'total_courses': sum(analysis['total_courses'] for analysis in all_analyses.values()),
            'sdg_coverage': {
                sdg: {
                    'total_count': sum(
                        semester['sdg_distribution'].get(sdg, {'count': 0})['count']
                        for semester in all_analyses.values()
                    )
                }
                for sdg in SDG_KEYWORDS.keys()
            }
        },
        'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Speichere Analyseergebnisse
    output_file = os.path.join(data_dir, 'keyword_analysis.json')  # Geändert von sdg_analysis.json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(total_analysis, f, ensure_ascii=False, indent=2)
    
    return total_analysis

if __name__ == "__main__":
    print("="*80)
    print("Starte Keyword-basierte SDG-Analyse")
    print("="*80)
    
    analysis_results = analyze_all_semesters()
    
    print("\nAnalyse abgeschlossen!")
    print(f"Analysierte Semester: {list(analysis_results['semester_analyses'].keys())}")
    print(f"Gesamtanzahl der Kurse: {analysis_results['overall_statistics']['total_courses']}")
    print("\nDie Ergebnisse wurden in data/keyword_analysis.json gespeichert.")
    print("="*80) 