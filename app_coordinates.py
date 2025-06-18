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
        [col for col in df.columns if col not in ['X', 'Y', 'X2', 'Y2', 'Time']]
    )
    
    # Erstelle Farb-Auswahl für jeden einzigartigen Wert
    color_mapping = {}
    if color_column:
        unique_values = sorted(df[color_column].unique())
        for value in unique_values:
            if not pd.isna(value):  # Überspringe NaN-Werte
                # Standardfarben als Hex-Codes
                default_color = '#00CD00' if value == 'Erfolgreich' else '#00CD00' if value == 'Nicht erfolgreich' else '#FFFF00'
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
    # Feste Basis-Größe für das Spielfeld
    fig_width = 12  # Basis-Breite
    fig_height = fig_width * (68/105)  # Verhältnis 105:68 beibehalten
    
    # Erstelle das Spielfeld mit responsiver Größe
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
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
    
    # Mittelfeldkreis (relativ zur Feldgröße)
    center_circle_radius = field_width * 0.095  # Etwa 10% der Feldbreite
    center_circle = patches.Circle((0, 0), center_circle_radius, fill=False, color='white', linewidth=1)
    ax.add_patch(center_circle)
    
    # Strafräume (relativ zur Feldgröße)
    penalty_area_width = field_width * 0.157  # Etwa 16.5m
    penalty_area_height = field_height * 0.593  # Etwa 40.32m
    ax.add_patch(patches.Rectangle((-field_width/2, -penalty_area_height/2), penalty_area_width, penalty_area_height, 
                                 fill=False, color='white', linewidth=1))
    ax.add_patch(patches.Rectangle((field_width/2 - penalty_area_width, -penalty_area_height/2), 
                                 penalty_area_width, penalty_area_height, fill=False, color='white', linewidth=1))
    
    # Strafraumkreise (relativ zur Feldgröße)
    Elfmeterpunkt_links = [-field_width/2 + field_width * 0.105, 0]  # Etwa 11m
    Elfmeterpunkt_rechts = [field_width/2 - field_width * 0.106, 0]  # Etwa 11.1m
    penalty_arc_radius = field_width * 0.087  # Etwa 9.15m
    
    # Berechne den Winkel für den Schnittpunkt mit dem Strafraum
    x_intersect = -field_width/2 + penalty_area_width
    dx = x_intersect - Elfmeterpunkt_links[0]
    angle_intersect = np.arccos(dx / penalty_arc_radius)
    angle_intersect_deg = np.degrees(angle_intersect)
    
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
    
    # Torräume (relativ zur Feldgröße)
    goal_area_width = field_width * 0.057  # Etwa 6m
    goal_area_height = field_height * 0.294  # Etwa 20m
    ax.add_patch(patches.Rectangle((-field_width/2, -goal_area_height/2), goal_area_width, goal_area_height, 
                                 fill=False, color='white', linewidth=1))
    ax.add_patch(patches.Rectangle((field_width/2 - goal_area_width, -goal_area_height/2), 
                                 goal_area_width, goal_area_height, fill=False, color='white', linewidth=1))
    
    # Elfmeterpunkte (relativ zur Feldgröße)
    penalty_spot_radius = field_width * 0.003  # Etwa 0.3m
    penalty_spot_left = patches.Circle(Elfmeterpunkt_links, penalty_spot_radius, 
                                     fill=True, color='white', linewidth=1)
    penalty_spot_right = patches.Circle(Elfmeterpunkt_rechts, penalty_spot_radius, 
                                      fill=True, color='white', linewidth=1)
    ax.add_patch(penalty_spot_left)
    ax.add_patch(penalty_spot_right)
    
    # Mittelpunkt (relativ zur Feldgröße)
    center_spot_radius = field_width * 0.003  # Etwa 0.3m
    center_circle = patches.Circle((0, 0), center_spot_radius, 
                                 fill=True, color='white', linewidth=1)
    ax.add_patch(center_circle)

    # Zeichne die Pässe mit responsiven Größen
    for _, row in df_filtered.iterrows():
        # Startkoordinaten
        start_x = row['X']
        start_y = row['Y']

        # Standardfarbe (grün)
        color = '#00CD00'

        # Prüfe zuerst die Farb-Zuordnung aus der Sidebar
        if color_column and color_column in row:
            value = row[color_column]
            if value in color_mapping:
                color = color_mapping[value]
        
            
        # Prüfe, ob es sich um einen nicht erfolgreichen Pass handelt
        is_Fehlpass = False
        if 'Outcome' in row and isinstance(row['Outcome'], str):
            is_Fehlpass = 'nicht erfolgreich' in row['Outcome'].lower()
            
        # Wenn es ein nicht erfolgreicher Pass ist, überschreibe die Farbe mit Rot
        if is_Fehlpass:
            color = '#FF0000'

        is_high_pass = False
        if 'Passhöhe' in row and isinstance(row['Passhöhe'], str):
            is_high_pass = 'hoch' in row['Passhöhe'].lower()
        
        # Wenn es ein hoher Pass ist, überschreibe die Farbe mit Gelb
        if is_high_pass:
            color = '#FFFF00'

        # Setze Transparenz
        alpha = 0.4
        
        # Responsive Größen für Punkte und Linien
        start_point_size = field_width * 0.067  # Etwa 7 Einheiten
        end_point_size = field_width * 0.105    # Etwa 11 Einheiten
        line_width = field_width * 0.019        # Etwa 2 Einheiten
        
        # Zeichne den Startpunkt (kleiner)
        ax.plot(start_x, start_y, 'o', color=color, markersize=start_point_size, alpha=alpha)
        
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
                ax.annotate("",
                           xy=(end_x, end_y), xycoords='data',
                           xytext=(start_x, start_y), textcoords='data',
                           arrowprops=dict(arrowstyle="-|>", color=color,
                                         linewidth=line_width,
                                         alpha=alpha,
                                         connectionstyle="arc3,rad=0.3",
                                         shrinkA=0, shrinkB=0,
                                         mutation_scale=field_width * 0.162),  # Responsive Pfeilspitze
                           )
            else:
                # Für normale Pässe: gerade Linie
                ax.plot([start_x, end_x], [start_y, end_y], color=color, linewidth=line_width, alpha=alpha)
                
                # Berechne die Position der Pfeilspitze
                arrow_pos = 0.5
                arrow_x = start_x + (end_x - start_x) * arrow_pos
                arrow_y = start_y + (end_y - start_y) * arrow_pos
                
                # Responsive Pfeilspitze
                arrow_length = field_width * 0.005
                arrow_dx = np.cos(angle) * arrow_length
                arrow_dy = np.sin(angle) * arrow_length
                
                ax.annotate("",
                           xy=(arrow_x + arrow_dx, arrow_y + arrow_dy), xycoords='data',
                           xytext=(arrow_x - arrow_dx, arrow_y - arrow_dy), textcoords='data',
                           arrowprops=dict(arrowstyle="->", color=color,
                                         linewidth=line_width,
                                         alpha=1,
                                         shrinkA=0, shrinkB=0),
                           )
            
            # Zeichne den Endpunkt (größer)
            ax.plot(end_x, end_y, 'o', color=color, markersize=end_point_size, alpha=alpha)
        else:
            # Wenn keine Endkoordinaten vorhanden sind
            ax.plot(start_x, start_y, 'o', color=color, markersize=end_point_size, alpha=alpha)
    
    # Setze Achsen-Limits und entferne Achsen
    ax.set_xlim(-field_width/2, field_width/2)
    ax.set_ylim(-field_height/2, field_height/2)
    ax.axis('off')
    
    # Mache das Diagramm responsiv
    fig.tight_layout()
    
    # Zeige das Diagramm
    st.pyplot(fig, use_container_width=True)
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