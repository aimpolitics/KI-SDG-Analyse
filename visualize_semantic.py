import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def load_data():
    """Lädt die semantische Analyse"""
    with open('data/semantic_analysis.json', 'r', encoding='utf-8') as f:
        semantic_data = json.load(f)
    return semantic_data

def create_confidence_plot(semantic_data):
    """Erstellt eine Visualisierung der Konfidenzintervalle und Ähnlichkeitsverteilung"""
    # Sammle alle Ähnlichkeitswerte
    similarities = []
    for semester in semantic_data['semantic_analysis'].values():
        for course in semester['courses']:
            similarities.extend([
                match['similarity'] 
                for match in course['semantic_matches'].values()
            ])
    
    similarities = np.array(similarities)
    
    # Erstelle Figure mit zwei Subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Plot 1: Verteilung der Ähnlichkeitswerte
    sns.histplot(similarities, bins=50, kde=True, ax=ax1)
    ax1.axvline(x=0.8, color='r', linestyle='--', label='Hohe Ähnlichkeit (0.8)')
    ax1.axvline(x=0.7, color='orange', linestyle='--', label='Mittlere Ähnlichkeit (0.7)')
    ax1.set_title('Verteilung der semantischen Ähnlichkeitswerte')
    ax1.set_xlabel('Ähnlichkeitswert')
    ax1.set_ylabel('Anzahl')
    ax1.legend()
    
    # Plot 2: Konfidenzintervalle pro SDG
    sdgs = [f"SDG {i}" for i in range(1, 18)]
    means = []
    errors = []
    
    for sdg in sdgs:
        sdg_similarities = []
        for semester in semantic_data['semantic_analysis'].values():
            for course in semester['courses']:
                if sdg in course['semantic_matches']:
                    sdg_similarities.append(course['semantic_matches'][sdg]['similarity'])
        
        mean = np.mean(sdg_similarities)
        std = np.std(sdg_similarities)
        ci = 1.96 * std / np.sqrt(len(sdg_similarities))  # 95% Konfidenzintervall
        
        means.append(mean)
        errors.append(ci)
    
    ax2.errorbar(sdgs, means, yerr=errors, fmt='o', capsize=5)
    ax2.set_title('Mittlere Ähnlichkeit und 95% Konfidenzintervalle pro SDG')
    ax2.set_xlabel('SDG')
    ax2.set_ylabel('Mittlere Ähnlichkeit')
    ax2.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Layout optimieren
    plt.tight_layout()
    
    # Speichere die Grafik
    Path("plots").mkdir(exist_ok=True)
    plt.savefig('plots/confidence_intervals.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    # Lade Daten
    semantic_data = load_data()
    
    # Erstelle Konfidenzintervall-Plot
    create_confidence_plot(semantic_data)
    print("Konfidenzintervall-Plot erstellt: plots/confidence_intervals.png")

if __name__ == "__main__":
    main() 