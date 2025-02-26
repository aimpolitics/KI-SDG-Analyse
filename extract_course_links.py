import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

def get_semester_info(url):
    """
    Extrahiert und mapped die korrekten Semester-Informationen
    """
    match = re.search(r'path=(\d+)', url)
    if not match:
        raise ValueError(f"Keine Semester-ID in URL gefunden: {url}")
    
    path_id = match.group(1)
    
    # Korrigiertes Semester-Mapping mit richtigen Beschreibungen
    semester_mapping = {
        '314583': {'id': 'WS2024', 'name': 'Wintersemester 2024'},      
        '306282': {'id': 'SS2024', 'name': 'Sommersemester 2024'},      
        '297842': {'id': 'WS2023', 'name': 'Wintersemester 2023'},      
        '290492': {'id': 'SS2023', 'name': 'Sommersemester 2023'}       
    }
    
    if path_id not in semester_mapping:
        raise ValueError(f"Unbekannte Semester-ID: {path_id}")
    
    return {
        'path_id': path_id,
        'semester_id': semester_mapping[path_id]['id'],
        'semester_name': semester_mapping[path_id]['name']
    }

def get_course_links(url):
    print(f"\nLade Kursliste von: {url}")
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    if response.status_code != 200:
        raise Exception(f"Fehler beim Laden der URL: {response.status_code}")
    
    print("Webseite erfolgreich geladen")
    soup = BeautifulSoup(response.text, 'html.parser')
    course_lists = soup.find_all(class_='lv-and-exam-list')
    print(f"Gefundene Kurslisten: {len(course_lists)}")
    
    course_links = []
    for i, course_list in enumerate(course_lists, 1):
        links = course_list.find_all('a')
        print(f"Verarbeite Liste {i}/{len(course_lists)}: {len(links)} Links gefunden")
        for link in links:
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = 'https://ufind.univie.ac.at/de/' + href.lstrip('/')
                course_links.append(href)
    
    print(f"Insgesamt {len(course_links)} Kurs-Links extrahiert")
    return course_links

def process_semester(url):
    print(f"\nVerarbeite Semester von URL: {url}")
    
    # Hole korrekte Semester-Informationen
    semester_info = get_semester_info(url)
    semester_dir = f"data/semester_{semester_info['semester_id']}"
    os.makedirs(semester_dir, exist_ok=True)
    print(f"Verzeichnis erstellt/gefunden: {semester_dir}")
    
    # Speichere Semester-Informationen
    info_file = os.path.join(semester_dir, 'semester_info.json')
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(semester_info, f, ensure_ascii=False, indent=2)
    
    # Hole und speichere Kurs-Links
    links = get_course_links(url)
    links_file = os.path.join(semester_dir, 'course_links.json')
    
    print(f"\nSpeichere {len(links)} Links in: {links_file}")
    with open(links_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)
    print("Links erfolgreich gespeichert")
    
    return semester_info['semester_id'], len(links)

if __name__ == '__main__':
    print("="*80)
    print("Starte Extraktion der Kurs-Links")
    print("="*80)
    
    os.makedirs("data", exist_ok=True)
    print("\nDaten-Verzeichnis bereit")
    
    # Aktualisierte URLs mit korrekter Zuordnung
    urls = [
        'https://ufind.univie.ac.at/de/vvz_sub.html?path=314583',  # Wintersemester 2024
        'https://ufind.univie.ac.at/de/vvz_sub.html?path=306282',  # Sommersemester 2024
        'https://ufind.univie.ac.at/de/vvz_sub.html?path=297842',  # Wintersemester 2023
        'https://ufind.univie.ac.at/de/vvz_sub.html?path=290492'   # Sommersemester 2023
    ]
    print(f"\nZu verarbeitende Semester: {len(urls)}")
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"\nVerarbeite Semester {i}/{len(urls)}")
        print("-"*40)
        try:
            semester_id, num_links = process_semester(url)
            results.append({
                'url': url,
                'semester_id': semester_id,
                'num_courses': num_links,
                'status': 'success',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"\n✅ Erfolgreich verarbeitet: {semester_id}")
            print(f"   Gefundene Kurse: {num_links}")
        except Exception as e:
            results.append({
                'url': url,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            print(f"\n❌ Fehler bei URL {url}:")
            print(f"   {str(e)}")
    
    # Speichere Verarbeitungszusammenfassung
    summary_file = 'data/processing_summary.json'
    print(f"\nSpeichere Zusammenfassung in: {summary_file}")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print("Extraktion der Kurs-Links abgeschlossen!")
    print("="*80) 