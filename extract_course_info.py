import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import sys
import os
import glob
from typing import Dict, List, Optional
import re

def load_semester_info(semester_dir: str) -> Dict:
    """
    Lädt die Semester-Informationen aus der semester_info.json
    """
    info_file = os.path.join(semester_dir, 'semester_info.json')
    if not os.path.exists(info_file):
        raise FileNotFoundError(f"Semester-Info-Datei nicht gefunden: {info_file}")
    
    with open(info_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_course_info(url: str) -> Optional[Dict]:
    try:
        print(f"Verarbeite Kurs: {url}")
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Fehler beim Laden von {url}: Status code {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        course_info = {'url': url}
        
        # Extrahiere Semester aus URL und mappe auf korrektes Format
        semester_match = re.search(r'semester=(\d{4})([SW])', url)
        if semester_match:
            year = semester_match.group(1)
            term = semester_match.group(2)
            semester_code = f"{'WS' if term == 'W' else 'SS'}{year}"
            course_info['semester_code'] = semester_code
        
        # Extract course number and type
        title = soup.find('h1', class_='title')
        if title:
            number_span = title.find('span', class_='number')
            type_span = title.find('abbr', class_='type')
            what_span = title.find('span', class_='what')
            when_span = title.find('span', class_='when')
            
            course_info['number'] = number_span.text.strip() if number_span else None
            course_info['type'] = type_span.text.strip() if type_span else None
            course_info['title'] = what_span.text.strip() if what_span else None
            course_info['semester'] = when_span.text.strip() if when_span else None
        
        # Extract subtitle
        subtitle = soup.find('h2', class_='subtitle')
        if subtitle:
            course_info['subtitle'] = subtitle.text.strip()
        
        # Extract ECTS and SWS
        details = soup.find('div', class_='details')
        if details:
            ects_span = details.find('span', class_='ects')
            sws_span = details.find('span', class_='sws')
            course_info['ects'] = float(ects_span.text.strip()) if ects_span else None
            course_info['sws'] = float(sws_span.text.strip()) if sws_span else None
        
        # Extract lecturers
        lecturers = soup.find('ul', class_='lecturers')
        if lecturers:
            course_info['lecturers'] = [a.text.strip() for a in lecturers.find_all('a', class_='name')]
        
        # Extract course objectives and content
        comment = soup.find('div', class_='comment text')
        if comment:
            course_info['objectives_and_content'] = comment.text.strip()
        
        # Extract examination info
        performance = soup.find('div', class_='performance text')
        if performance:
            course_info['examination_info'] = performance.text.strip()
        
        # Extract minimum requirements
        preconditions = soup.find('div', class_='preconditions text')
        if preconditions:
            course_info['minimum_requirements'] = preconditions.text.strip()
        
        # Extract literature
        literature = soup.find('div', class_='literature text')
        if literature:
            course_info['literature'] = literature.text.strip()
        
        return course_info
    
    except requests.RequestException as e:
        print(f"Netzwerkfehler bei {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Fehler bei der Verarbeitung von {url}: {str(e)}")
        return None

def crawl_all_courses(links: List[str], delay: float = 1.0) -> List[Dict]:
    courses = []
    total = len(links)
    
    print(f"Starte Verarbeitung von {total} Kursen...")
    start_time = time.time()
    
    for i, url in enumerate(links, 1):
        progress = (i / total) * 100
        elapsed = time.time() - start_time
        avg_time = elapsed / i
        remaining = avg_time * (total - i)
        
        sys.stdout.write(f"\rFortschritt: {progress:.1f}% ({i}/{total}) - Verbleibende Zeit: {remaining:.0f}s")
        sys.stdout.flush()
        
        course_info = extract_course_info(url)
        if course_info:
            courses.append(course_info)
        
        time.sleep(delay)
    
    print("\nVerarbeitung abgeschlossen!")
    return courses

def process_semester(semester_dir: str, delay: float = 1.0) -> Dict:
    """
    Verarbeitet ein Semester mit der korrigierten Struktur
    """
    # Lade Semester-Informationen
    semester_info = load_semester_info(semester_dir)
    
    # Lade Kurs-Links
    links_file = os.path.join(semester_dir, 'course_links.json')
    if not os.path.exists(links_file):
        raise FileNotFoundError(f"Kurs-Links-Datei nicht gefunden: {links_file}")
    
    with open(links_file, 'r', encoding='utf-8') as f:
        course_links = json.load(f)
    
    # Verarbeite alle Kurse
    all_courses = crawl_all_courses(course_links, delay)
    
    # Generiere Ausgabedatei mit korrektem Zeitstempel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(semester_dir, f'courses_{timestamp}.json')
    
    # Füge Semester-Informationen hinzu
    result = {
        'semester_info': semester_info,
        'extraction_timestamp': timestamp,
        'courses': all_courses
    }
    
    # Speichere Ergebnisse
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return {
        'semester': semester_info['semester_id'],
        'status': 'success',
        'courses_saved': len(all_courses),
        'total_links': len(course_links),
        'output_file': output_file,
        'success_rate': (len(all_courses)/len(course_links))*100 if course_links else 0
    }

if __name__ == '__main__':
    print("="*80)
    print("Starte Extraktion der Kurs-Informationen")
    print("="*80)
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("Daten-Verzeichnis nicht gefunden. Bitte zuerst extract_course_links.py ausführen.")
        sys.exit(1)
    
    # Finde alle Semester-Verzeichnisse mit der neuen Struktur
    semester_dirs = [d for d in os.listdir(data_dir) 
                    if os.path.isdir(os.path.join(data_dir, d)) 
                    and d.startswith('semester_')]
    
    if not semester_dirs:
        print("Keine Semester-Verzeichnisse gefunden. Bitte zuerst extract_course_links.py ausführen.")
        sys.exit(1)
    
    # Verarbeite jedes Semester
    results = []
    for semester_dir in semester_dirs:
        full_dir = os.path.join(data_dir, semester_dir)
        print(f"\nVerarbeite {semester_dir}...")
        try:
            result = process_semester(full_dir)
            print(f"✅ {result['courses_saved']} Kurse gespeichert in {result['output_file']}")
            print(f"   Erfolgsrate: {result['success_rate']:.1f}%")
            results.append(result)
        except Exception as e:
            print(f"❌ Fehler bei {semester_dir}: {str(e)}")
            results.append({
                'semester': semester_dir,
                'status': 'error',
                'error': str(e)
            })
    
    # Speichere Verarbeitungszusammenfassung
    summary_file = os.path.join(data_dir, 'course_info_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print("Extraktion der Kurs-Informationen abgeschlossen!")
    print("="*80) 