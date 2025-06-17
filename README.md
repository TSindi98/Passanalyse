# Passanalyse

Eine interaktive Webanwendung zur Analyse von Passnetzwerken im Fußball, entwickelt mit Streamlit.

## Features

- Visualisierung von Passnetzwerken auf einem Fußballfeld
- Interaktive Filterung von Daten
- Farbkodierung von Pässen basierend auf verschiedenen Kriterien
- Unterscheidung zwischen hohen und normalen Pässen
- Statistische Auswertungen
- Responsive Benutzeroberfläche

## Installation

1. Klonen Sie das Repository:
```bash
git clone https://github.com/yourusername/Passanalyse.git
cd Passanalyse
```

2. Installieren Sie die erforderlichen Pakete:
```bash
pip install -r requirements.txt
```

## Verwendung

1. Starten Sie die Anwendung:
```bash
streamlit run app_coordinates.py
```

2. Öffnen Sie einen Webbrowser und navigieren Sie zu `http://localhost:8501`

3. Laden Sie Ihre CSV-Datei hoch, die folgende Spalten enthalten sollte:
   - X, Y: Startkoordinaten des Passes
   - X2, Y2: Endkoordinaten des Passes
   - Weitere optionale Spalten wie 'Passhöhe', 'Outcome', 'Gegnerdruck'

## Datenformat

Die CSV-Datei sollte folgende Spalten enthalten:

- X, Y: Startkoordinaten (numerisch)
- X2, Y2: Endkoordinaten (numerisch)
- Passhöhe (optional): "hoch" für hohe Pässe
- Outcome (optional): "Erfolgreich" oder "Nicht erfolgreich"
- Gegnerdruck (optional): Verschiedene Kategorien

## Technische Details

- Entwickelt mit Python und Streamlit
- Verwendet Matplotlib für die Visualisierung
- Unterstützt verschiedene Dateikodierungen (latin1, utf-8, cp1252)

## Lizenz

MIT License

## Autor

[TSindi98]

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request für größere Änderungen. 