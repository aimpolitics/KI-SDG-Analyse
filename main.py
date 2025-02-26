import subprocess
import sys
import time
from datetime import datetime
import os

def run_script(script_name, description):
    """
    Führt ein Python-Skript aus und zeigt den Status an
    """
    print(f"\n{'='*80}")
    print(f"Starte: {description}")
    print(f"Skript: {script_name}")
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*80 + "\n")
    
    try:
        # Führe das Skript mit Python aus der virtuellen Umgebung aus
        venv_python = os.path.join('.venv', 'bin', 'python')
        # Keine Ausgabeumleitung - zeige alles direkt im Terminal
        process = subprocess.run([venv_python, script_name])
        
        if process.returncode == 0:
            print(f"\n✅ {script_name} erfolgreich ausgeführt!")
            return True
        else:
            print(f"\n❌ Fehler beim Ausführen von {script_name}")
            return False
            
    except Exception as e:
        print(f"\n❌ Fehler beim Ausführen von {script_name}: {str(e)}")
        return False

def main():
    # Liste der auszuführenden Skripte mit Beschreibungen
    scripts = [
        ("extract_course_links.py", "Extrahiere Kurs-Links von der Univie-Website"),
        ("extract_course_info.py", "Extrahiere detaillierte Kurs-Informationen"),
        ("analyze_sdgs.py", "Analysiere SDG-Relevanz der Kurse")
    ]
    
    print("\n🚀 Starte Datenextraktion und Analyse...")
    
    for script_name, description in scripts:
        if not run_script(script_name, description):
            print(f"\n❌ Prozess abgebrochen aufgrund von Fehlern in {script_name}")
            sys.exit(1)
        print("\nWarte 2 Sekunden vor dem nächsten Schritt...")
        time.sleep(2)
    
    print("\n✨ Datenextraktion und Analyse abgeschlossen!")

if __name__ == "__main__":
    main() 