import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

st.set_page_config(page_title="Passnetzwerk-Analyse (Koordinaten)", layout="wide")

st.title("Passnetzwerk-Analyse (Koordinaten)")

# Datei-Upload
uploaded_file = st.file_uploader("Wählen Sie Ihre CSV-Datei aus", type=['csv'])

if uploaded_file is not None:
    # Daten einlesen mit korrekter Kodierung
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
    except:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except:
            df = pd.read_csv(uploaded_file, encoding='cp1252')
    
    # Debug: Zeige die tatsächlichen Spaltennamen
    st.write("Verfügbare Spalten in der CSV:")
    st.write(df.columns.tolist())
    
    # Zeige die ersten Zeilen der Daten
    st.subheader("Vorschau der Daten")
    st.dataframe(df.head())
    
    # Sidebar für Filter
    st.sidebar.header("Filter")
    
    # Farb-Zuordnung
    st.sidebar.header("Farb-Zuordnung")
    color_column = st.sidebar.selectbox(
        "Spalte für Farb-Zuordnung auswählen",
        [col for col in df.columns if col not in ['X', 'Y', 'X2', 'Y2']]
    )
    
    # Erstelle Farb-Auswahl für jeden einzigartigen Wert
    color_mapping = {}
    if color_column:
        unique_values = sorted(df[color_column].unique())
        for value in unique_values:
            if not pd.isna(value):  # Überspringe NaN-Werte
                # Standardfarben als Hex-Codes
                default_color = '#0000FF' if value == 'Erfolgreich' else '#FF0000' if value == 'Nicht erfolgreich' else '#FFFF00'
                color = st.sidebar.color_picker(
                    f"Farbe für '{value}'",
                    value=default_color
                )
                color_mapping[value] = color
    
    # Erstelle dynamisch Filter für alle Spalten außer X, Y, X2, Y2
    excluded_columns = ['X', 'Y', 'X2', 'Y2', 'Time']
    df_filtered = df.copy()  # Initialisiere df_filtered mit allen Daten
    for column in df.columns:
        if column not in excluded_columns:
            unique_values = sorted(df[column].unique())
            if len(unique_values) > 0:  # Nur wenn es Werte gibt
                if len(unique_values) <= 10:  # Für wenige Optionen: Multiselect
                    selected_values = st.sidebar.multiselect(
                        f"{column} auswählen",
                        unique_values,
                        default=unique_values
                    )
                    df_filtered = df_filtered[df_filtered[column].isin(selected_values)]
                else:  # Für viele Optionen: Selectbox
                    selected_value = st.sidebar.selectbox(
                        f"{column} auswählen",
                        unique_values
                    )
                    df_filtered = df_filtered[df_filtered[column] == selected_value]
    
    # Erstelle das Spielfeld
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Spielfeldmaße (in Einheiten des Tagging-Tools)
    field_width = 105
    field_height = 68
    
    # Zeichne das Spielfeld
    ax.add_patch(patches.Rectangle((-field_width/2, -field_height/2), field_width, field_height, 
                                 fill=True, color='#036602', alpha=0.3))
    ax.add_patch(patches.Rectangle((-field_width/2, -field_height/2), field_width, field_height, 
                                 fill=False, color='white', linewidth=2))
    
    # Mittellinie (durchgehend)
    ax.plot([0, 0], [-field_height/2, field_height/2], 'w-', alpha=0.5)
    
    # Mittelfeldkreis
    center_circle = patches.Circle((0, 0), 10, fill=False, color='white', linewidth=1)
    ax.add_patch(center_circle)
    
    # Strafräume
    penalty_area_width = 16.5
    penalty_area_height = 40.32
    ax.add_patch(patches.Rectangle((-field_width/2, -penalty_area_height/2), penalty_area_width, penalty_area_height, 
                                 fill=False, color='white', linewidth=1))
    ax.add_patch(patches.Rectangle((field_width/2 - penalty_area_width, -penalty_area_height/2), 
                                 penalty_area_width, penalty_area_height, fill=False, color='white', linewidth=1))
    
    # Strafraumkreise (nur außerhalb des Strafraums sichtbar)
    Elfmeterpunkt_links = [-field_width/2 + 11, 0]
    Elfmeterpunkt_rechts = [field_width/2 - 11.1, 0]
    penalty_arc_radius = 9.15
    
    # Berechne den Winkel für den Schnittpunkt mit dem Strafraum
    # Der Kreis schneidet den Strafraum bei x = -field_width/2 + penalty_area_width
    # Für den linken Strafraum:
    x_intersect = -field_width/2 + penalty_area_width
    dx = x_intersect - Elfmeterpunkt_links[0]  # Abstand vom Elfmeterpunkt zum Schnittpunkt
    angle_intersect = np.arccos(dx / penalty_arc_radius)  # Winkel in Radiant
    angle_intersect_deg = np.degrees(angle_intersect)  # Winkel in Grad
    
    # Linker Strafraumkreis
    arc_left = patches.Arc(Elfmeterpunkt_links, 
                         2*penalty_arc_radius, 2*penalty_arc_radius,
                         theta1=-angle_intersect_deg, theta2=angle_intersect_deg, 
                         color='white', linewidth=1)
    ax.add_patch(arc_left)
    
    # Rechter Strafraumkreis
    arc_right = patches.Arc(Elfmeterpunkt_rechts, 
                          2*penalty_arc_radius, 2*penalty_arc_radius,
                          theta1=180-angle_intersect_deg, theta2=180+angle_intersect_deg, 
                          color='white', linewidth=1)
    ax.add_patch(arc_right)
    
    # Torräume
    goal_area_width = 6
    goal_area_height = 20
    ax.add_patch(patches.Rectangle((-field_width/2, -goal_area_height/2), goal_area_width, goal_area_height, 
                                 fill=False, color='white', linewidth=1))
    ax.add_patch(patches.Rectangle((field_width/2 - goal_area_width, -goal_area_height/2), 
                                 goal_area_width, goal_area_height, fill=False, color='white', linewidth=1))
    
    # Elfmeterpunkte
    penalty_spot_radius = 0.3  # Radius des Elfmeterpunktes
    penalty_spot_left = patches.Circle(Elfmeterpunkt_links, penalty_spot_radius, 
                                     fill=True, color='white', linewidth=1)
    penalty_spot_right = patches.Circle(Elfmeterpunkt_rechts, penalty_spot_radius, 
                                      fill=True, color='white', linewidth=1)
    ax.add_patch(penalty_spot_left)
    ax.add_patch(penalty_spot_right)
    
# Mittelpunkt
    center_circle = patches.Circle((0, 0), 0.3, 
                                      fill=True, color='white', linewidth=1)
    ax.add_patch(center_circle)

    # Zeichne die Pässe
    for _, row in df_filtered.iterrows():
        # Startkoordinaten
        start_x = row['X']
        start_y = row['Y']
        
        # Prüfe, ob es sich um einen hohen Pass handelt
        is_high_pass = False
        if 'Passhöhe' in row and isinstance(row['Passhöhe'], str):
            is_high_pass = 'hoch' in row['Passhöhe'].lower()
        
        # Bestimme die Farbe
        color = '#0000FF'  # Standardfarbe (blau)
        
        # Prüfe zuerst die Farb-Zuordnung
        if color_column and color_column in row:
            value = row[color_column]
            if value in color_mapping:
                color = color_mapping[value]
        
        # Wenn es ein hoher Pass ist, überschreibe die Farbe mit Gelb
        if is_high_pass:
            color = '#FFFF00'
        
        # Setze Transparenz
        alpha = 0.4
        line_width = 2  # Erhöhte Linienbreite
        
        # Zeichne den Startpunkt (kleiner)
        ax.plot(start_x, start_y, 'o', color=color, markersize=7, alpha=alpha)
        
        # Prüfe, ob Endkoordinaten vorhanden sind
        if 'X2' in row and 'Y2' in row and not pd.isna(row['X2']) and not pd.isna(row['Y2']):
            end_x = row['X2']
            end_y = row['Y2']
            
            # Berechne den Mittelpunkt
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Berechne die Passrichtung
            dx = end_x - start_x
            dy = end_y - start_y
            length = np.sqrt(dx**2 + dy**2)
            angle = np.arctan2(dy, dx)
            
            if is_high_pass:
                # Für hohe Pässe: gebogene Linie
                # Zeichne die durchgehende gebogene Linie
                ax.annotate("",
                           xy=(end_x, end_y), xycoords='data',
                           xytext=(start_x, start_y), textcoords='data',
                           arrowprops=dict(arrowstyle="-|>", color=color,
                                         linewidth=line_width,
                                         alpha=alpha,
                                         connectionstyle="arc3,rad=0.3",
                                         shrinkA=0, shrinkB=0,
                                         mutation_scale=17),  # Größe der Pfeilspitze
                           )
            else:
                # Für normale Pässe: gerade Linie
                # Zeichne die durchgehende Linie
                ax.plot([start_x, end_x], [start_y, end_y], color=color, linewidth=line_width, alpha=alpha)
                
                # Berechne die Position der Pfeilspitze
                arrow_pos = 0.5  # Position auf der Linie (0 bis 1)
                arrow_x = start_x + (end_x - start_x) * arrow_pos
                arrow_y = start_y + (end_y - start_y) * arrow_pos
                
                # Berechne die Pfeilspitzen-Punkte basierend auf der Passrichtung
                arrow_length = 0.5  # Länge der Pfeilspitze
                arrow_dx = np.cos(angle) * arrow_length
                arrow_dy = np.sin(angle) * arrow_length
                
                # Füge nur die Pfeilspitze in der Mitte hinzu
                ax.annotate("",
                           xy=(arrow_x + arrow_dx, arrow_y + arrow_dy), xycoords='data',
                           xytext=(arrow_x - arrow_dx, arrow_y - arrow_dy), textcoords='data',
                           arrowprops=dict(arrowstyle="->", color=color,
                                         linewidth=line_width,
                                         alpha=1,
                                         shrinkA=0, shrinkB=0),
                           )
            
            # Zeichne den Endpunkt (größer)
            ax.plot(end_x, end_y, 'o', color=color, markersize=11, alpha=alpha)
        else:
            # Wenn keine Endkoordinaten vorhanden sind (z.B. bei Schüssen),
            # zeichne nur einen größeren Punkt
            ax.plot(start_x, start_y, 'o', color=color, markersize=11, alpha=alpha)
    
    # Setze Achsen-Limits und entferne Achsen
    ax.set_xlim(-field_width/2, field_width/2)
    ax.set_ylim(-field_height/2, field_height/2)
    ax.axis('off')
    
    # Zeige das Diagramm
    st.pyplot(fig)
    plt.close()
    
    # Statistiken
    st.subheader("Statistiken")
    
    # Passverteilung nach Höhe
    if 'Passhöhe' in df_filtered.columns:
        st.write("Verteilung der Passhöhen:")
        pass_height_counts = df_filtered['Passhöhe'].value_counts()
        st.bar_chart(pass_height_counts)
    
    # Passverteilung nach Outcome
    if 'Outcome' in df_filtered.columns:
        st.write("Verteilung der Pass-Outcomes:")
        outcome_counts = df_filtered['Outcome'].value_counts()
        st.bar_chart(outcome_counts)
    
    # Gegnerdruck-Verteilung
    if 'Gegnerdruck' in df_filtered.columns:
        st.write("Verteilung des Gegnerdrucks:")
        pressure_counts = df_filtered['Gegnerdruck'].value_counts()
        st.bar_chart(pressure_counts)
    
    # Durchschnittliche Passlänge
    df_filtered['Passlänge'] = np.sqrt(
        (df_filtered['X2'] - df_filtered['X'])**2 + 
        (df_filtered['Y2'] - df_filtered['Y'])**2
    )
    avg_pass_length = df_filtered['Passlänge'].mean()
    st.write(f"Durchschnittliche Passlänge: {avg_pass_length:.2f} Einheiten") 