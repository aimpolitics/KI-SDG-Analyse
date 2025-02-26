import torch
from transformers import AutoTokenizer, AutoModel
from typing import Dict, List, Set
import numpy as np
from scipy.spatial.distance import cosine

class SemanticSDGAnalyzer:
    def __init__(self):
        # Wir verwenden ein deutsches BERT-Modell
        self.model_name = "deepset/gbert-large"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Ausführliche SDG Beschreibungen für semantischen Vergleich
        self.sdg_descriptions = {
            "SDG 1": """Armut in allen ihren Formen und überall beenden. Extreme Armut beseitigen, soziale 
                Sicherungssysteme einführen, gleiche Rechte auf wirtschaftliche Ressourcen sicherstellen, 
                Widerstandsfähigkeit der Armen erhöhen, Entwicklungszusammenarbeit mobilisieren.""",
            
            "SDG 2": """Den Hunger beenden, Ernährungssicherheit und bessere Ernährung erreichen und eine nachhaltige 
                Landwirtschaft fördern. Zugang zu sicheren Nahrungsmitteln, nachhaltige Nahrungsmittelproduktion, 
                genetische Vielfalt erhalten, Agrarmarktverzerrungen korrigieren.""",
            
            "SDG 3": """Ein gesundes Leben für alle Menschen jeden Alters gewährleisten und ihr Wohlergehen fördern. 
                Müttersterblichkeit reduzieren, vermeidbare Todesfälle bei Neugeborenen verhindern, Epidemien bekämpfen, 
                universelle Gesundheitsversorgung, Zugang zu medizinischer Grundversorgung.""",
            
            "SDG 4": """Inklusive, gleichberechtigte und hochwertige Bildung gewährleisten und Möglichkeiten lebenslangen 
                Lernens für alle fördern. Kostenlose Grundschulbildung, Berufsbildung, Hochschulbildung, nachhaltige 
                Entwicklung verstehen, Bildungseinrichtungen ausbauen.""",
            
            "SDG 5": """Geschlechtergleichstellung erreichen und alle Frauen und Mädchen zur Selbstbestimmung befähigen. 
                Diskriminierung beenden, Gewalt beseitigen, gleiche Führungsrollen ermöglichen, gleicher Zugang zu 
                Ressourcen, Technologie für Gleichstellung nutzen.""",
            
            "SDG 6": """Verfügbarkeit und nachhaltige Bewirtschaftung von Wasser und Sanitärversorgung für alle gewährleisten. 
                Zugang zu sauberem Trinkwasser, Wasserqualität verbessern, Wassereffizienz steigern, Wasserressourcen schützen, 
                Ökosysteme im Zusammenhang mit Wasser schützen.""",
            
            "SDG 7": """Zugang zu bezahlbarer, verlässlicher, nachhaltiger und moderner Energie für alle sichern. 
                Erneuerbare Energien ausbauen, Energieeffizienz steigern, internationale Zusammenarbeit, moderne 
                Energieversorgung, saubere Energietechnologien.""",
            
            "SDG 8": """Dauerhaftes, breitenwirksames und nachhaltiges Wirtschaftswachstum, produktive Vollbeschäftigung und 
                menschenwürdige Arbeit für alle fördern. Wirtschaftliche Produktivität, ressourceneffizientes Wachstum, 
                Arbeitsrechte schützen, Jugendarbeitslosigkeit reduzieren.""",
            
            "SDG 9": """Eine widerstandsfähige Infrastruktur aufbauen, breitenwirksame und nachhaltige Industrialisierung 
                fördern und Innovationen unterstützen. Nachhaltige Industrien, Forschung und Entwicklung, technologische 
                Kapazitäten, Informationstechnologie, resiliente Infrastruktur.""",
            
            "SDG 10": """Ungleichheit in und zwischen Ländern verringern. Einkommenswachstum der ärmsten 40%, 
                Chancengleichheit, diskriminierungsfreie Gesetze und Politiken, geordnete Migration, internationale 
                Finanzströme regulieren.""",
            
            "SDG 11": """Städte und Siedlungen inklusiv, sicher, widerstandsfähig und nachhaltig gestalten. 
                Bezahlbarer Wohnraum, nachhaltige Verkehrssysteme, partizipative Stadtplanung, Kulturerbe schützen, 
                Katastrophenresilienz, Umweltbelastung reduzieren.""",
            
            "SDG 12": """Nachhaltige Konsum- und Produktionsmuster sicherstellen. Ressourceneffizienz, 
                Lebensmittelverschwendung reduzieren, Chemikalienmanagement, Abfallaufkommen verringern, nachhaltige 
                Beschaffung, Nachhaltigkeitsberichterstattung.""",
            
            "SDG 13": """Umgehend Maßnahmen zur Bekämpfung des Klimawandels und seiner Auswirkungen ergreifen. 
                Klimaresilienz, Klimaschutzmaßnahmen, Klimabildung, Klimafinanzierung, nationale Klimapolitik, 
                Pariser Klimaabkommen.""",
            
            "SDG 14": """Ozeane, Meere und Meeresressourcen im Sinne nachhaltiger Entwicklung erhalten und nachhaltig nutzen. 
                Meeresverschmutzung reduzieren, marine Ökosysteme schützen, Überfischung beenden, Meeresforschung, 
                kleine Fischereibetriebe unterstützen.""",
            
            "SDG 15": """Landökosysteme schützen, wiederherstellen und ihre nachhaltige Nutzung fördern. Wälder nachhaltig 
                bewirtschaften, Wüstenbildung bekämpfen, Biodiversitätsverlust stoppen, Bergökosysteme schützen, 
                Wilderei bekämpfen.""",
            
            "SDG 16": """Friedliche und inklusive Gesellschaften für eine nachhaltige Entwicklung fördern. Gewalt reduzieren, 
                Rechtsstaatlichkeit fördern, Korruption bekämpfen, leistungsfähige Institutionen aufbauen, partizipative 
                Entscheidungsfindung, Grundfreiheiten schützen.""",
            
            "SDG 17": """Umsetzungsmittel stärken und die Globale Partnerschaft für nachhaltige Entwicklung mit neuem Leben 
                erfüllen. Entwicklungsfinanzierung, Technologietransfer, Kapazitätsaufbau, gerechter Handel, systemische 
                Fragen, Multi-Akteur-Partnerschaften."""
        }
        
        # Erweiterte Konfiguration für das Modell
        self.threshold_config = {
            'base_threshold': 0.7,  # Grundschwelle für Ähnlichkeit
            'high_confidence': 0.85,  # Schwelle für hohe Konfidenz
            'min_word_count': 50,  # Minimale Wortanzahl für volle Analyse
        }
        
        # Vorberechnete Embeddings für SDG-Beschreibungen
        print("Initialisiere semantische Analyse...")
        self.sdg_embeddings = self._prepare_sdg_embeddings()
        print("Semantische Analyse bereit.")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Berechnet das semantische Embedding für einen Text."""
        # Textvorverarbeitung
        text = ' '.join(text.split())  # Normalisiere Whitespace
        
        # Tokenisierung mit Padding und Truncation
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Berechne Embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Verwende den [CLS] Token als Satz-Embedding
        embedding = outputs.last_hidden_state[:, 0, :].numpy()
        return embedding[0]
    
    def _prepare_sdg_embeddings(self) -> Dict[str, np.ndarray]:
        """Berechnet Embeddings für alle SDG-Beschreibungen."""
        embeddings = {}
        for sdg, description in self.sdg_descriptions.items():
            print(f"Berechne Embedding für {sdg}...")
            embeddings[sdg] = self._get_embedding(description)
        return embeddings
    
    def analyze_text(self, text: str, threshold: float = None) -> Dict[str, float]:
        """
        Analysiert einen Text auf semantische Ähnlichkeit zu SDGs.
        
        Args:
            text: Zu analysierender Text
            threshold: Optional. Überschreibt base_threshold wenn angegeben
            
        Returns:
            Dictionary mit SDGs und ihrer semantischen Ähnlichkeit
        """
        if not text.strip():
            return {}
            
        # Verwende Standard-Threshold wenn keiner angegeben
        if threshold is None:
            threshold = self.threshold_config['base_threshold']
        
        # Passe Threshold basierend auf Textlänge an
        word_count = len(text.split())
        if word_count < self.threshold_config['min_word_count']:
            threshold = threshold * (word_count / self.threshold_config['min_word_count'])
        
        # Berechne Embedding für den Input-Text
        text_embedding = self._get_embedding(text)
        
        # Berechne Ähnlichkeiten zu allen SDGs
        similarities = {
            sdg: 1 - cosine(text_embedding, sdg_embedding)
            for sdg, sdg_embedding in self.sdg_embeddings.items()
        }
        
        # Klassifiziere Konfidenz und filtere nach Threshold
        relevant_sdgs = {}
        for sdg, similarity in similarities.items():
            if similarity >= threshold:
                relevant_sdgs[sdg] = {
                    'similarity': similarity,
                    'confidence': 'high' if similarity >= self.threshold_config['high_confidence'] else 'medium'
                }
        
        return relevant_sdgs

def analyze_course_semantic(course: Dict, analyzer: SemanticSDGAnalyzer) -> Dict[str, float]:
    """Analysiert einen Kurs mit semantischer Analyse."""
    # Kombiniere relevante Textfelder
    relevant_text = " ".join([
        course.get('title', ''),
        course.get('subtitle', ''),
        course.get('objectives_and_content', '')
    ])
    
    # Führe semantische Analyse durch
    analysis_results = analyzer.analyze_text(relevant_text)
    
    # Extrahiere nur die Similarity-Werte für die Kompatibilität
    return {sdg: details['similarity'] for sdg, details in analysis_results.items()} 