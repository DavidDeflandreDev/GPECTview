import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import io
import pandas as pd
from matplotlib.ticker import FuncFormatter
import matplotlib.container
import streamlit as st
from constants import get_mepag_palette
import matplotlib.colors as mcolors

# Palette dynamique à adapter selon l'organisation future
PALETTE = px.colors.qualitative.Plotly

def create_centered_bar_chart(label_df, graph_title, x_axis_label, y_axis_label, display_as_percent, invert_axes, palette, show_legend=True):
    # ... (copier la fonction depuis app.py)
    # Palette dynamique pour MEPAG
    if palette is None:
        couleurs = get_mepag_palette(len(label_df))
    else:
        couleurs = palette[:len(label_df)]
    max_val = label_df["Valeur"].max()
    label_df["Espace_vide"] = (max_val - label_df["Valeur"]) / 2
    use_type = 'Type' in label_df.columns
    fig = go.Figure()
    if invert_axes:
        fig.add_trace(go.Bar(
            y=label_df["Label"],
            x=label_df["Espace_vide"],
            marker_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip',
            orientation='h'
        ))
        if use_type:
            for i, row in label_df.iterrows():
                text_val = f"{row['Valeur']:.2f}%" if display_as_percent else f"{row['Valeur']:.2f}"
                fig.add_trace(go.Bar(
                    y=[row["Label"]],
                    x=[row["Valeur"]],
                    text=[text_val],
                    textposition='outside',
                    marker_color=couleurs[i],
                    name=row["Type"],
                    orientation='h',
                    showlegend=show_legend
                ))
        else:
            for i, row in label_df.iterrows():
                text_val = f"{row['Valeur']:.2f}%" if display_as_percent else f"{row['Valeur']:.2f}"
                fig.add_trace(go.Bar(
                    y=[row["Label"]],
                    x=[row["Valeur"]],
                    text=[text_val],
                    textposition='outside',
                    marker_color=couleurs[i],
                    name=row["Label"],
                    orientation='h',
                    showlegend=show_legend
                ))
        fig.update_layout(
            xaxis_title=y_axis_label,
            yaxis_title=x_axis_label,
            showlegend=show_legend,
            legend_title_text="Réponse" if use_type else None
        )
    else:
        fig.add_trace(go.Bar(
            x=label_df["Label"],
            y=label_df["Espace_vide"],
            marker_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip'
        ))
        if use_type:
            for i, row in label_df.iterrows():
                text_val = f"{row['Valeur']:.2f}%" if display_as_percent else f"{row['Valeur']:.2f}"
                fig.add_trace(go.Bar(
                    x=[row["Label"]],
                    y=[row["Valeur"]],
                    text=[text_val],
                    textposition='outside',
                    marker_color=couleurs[i],
                    name=row["Type"],
                    showlegend=show_legend
                ))
        else:
            for i, row in label_df.iterrows():
                text_val = f"{row['Valeur']:.2f}%" if display_as_percent else f"{row['Valeur']:.2f}"
                fig.add_trace(go.Bar(
                    x=[row["Label"]],
                    y=[row["Valeur"]],
                    text=[text_val],
                    textposition='outside',
                    marker_color=couleurs[i],
                    name=row["Label"],
                    showlegend=show_legend
                ))
        fig.update_layout(
            yaxis_title=y_axis_label,
            xaxis_title=x_axis_label,
            showlegend=show_legend,
            legend_title_text="Réponse" if use_type else None
        )
    fig.update_layout(
        barmode='stack',
        title=graph_title,
        showlegend=show_legend
    )
    return fig

def create_stacked_bar_chart(label_df, graph_title, x_axis_label, y_axis_label, display_as_percent, invert_axes, palette):
    # ... (copier la fonction depuis app.py)
    if palette is None:
        couleurs = get_mepag_palette(len(label_df["Type"].unique()) if "Type" in label_df else len(label_df))
    else:
        couleurs = palette[:len(label_df["Type"].unique())] if "Type" in label_df else palette[:len(label_df)]
    if invert_axes:
        fig = px.bar(
            label_df,
            x="Valeur",
            y="Label",
            color="Type",
            text="Valeur",
            color_discrete_sequence=couleurs,
            title=graph_title,
            orientation='h'
        )
        fig.update_layout(
            xaxis_title=y_axis_label,
            yaxis_title=x_axis_label
        )
    else:
        fig = px.bar(
            label_df,
            x="Label",
            y="Valeur",
            color="Type",
            text="Valeur",
            color_discrete_sequence=couleurs,
            title=graph_title
        )
        fig.update_layout(
            xaxis_title=x_axis_label,
            yaxis_title=y_axis_label
        )
    fig.update_layout(barmode="stack")
    fig.update_traces(
        texttemplate='%{text:.2f}%' if display_as_percent else '%{text:.2f}',
        textposition="inside",
        insidetextanchor="middle"
    )
    return fig

def create_bar_chart(label_df, graph_title, x_axis_label, y_axis_label, display_as_percent, invert_axes, palette, show_legend=True):
    if palette is None:
        couleurs = get_mepag_palette(len(label_df))
    else:
        couleurs = palette[:len(label_df)]
    use_type = 'Type' in label_df.columns
    if use_type:
        # Cas classique : on laisse Plotly Express gérer la légende par type
        if invert_axes:
            valeurs = label_df["Valeur"].values
            labels = label_df["Label"].values
            if display_as_percent:
                text_vals = [f"{v:.2f}%" for v in valeurs]
            else:
                text_vals = [f"{v:.2f}" for v in valeurs]
            fig = go.Figure(go.Bar(
                x=valeurs,
                y=labels,
                orientation='h',
                marker_color=couleurs,
                text=text_vals,
                textposition='inside',
                insidetextanchor='middle',
                hovertemplate='%{y}: %{x}<extra></extra>',
                name='Valeur',
                showlegend=show_legend
            ))
            fig.update_traces(
                textfont_size=14,
                textangle=0,
                cliponaxis=False
            )
            fig.update_layout(
                title=graph_title,
                xaxis_title=x_axis_label,
                yaxis_title=y_axis_label,
                barmode='group',
                legend_title_text="Type",
                showlegend=show_legend
            )
        else:
            fig = px.bar(
                label_df,
                x="Label",
                y="Valeur",
                color="Type",
                text=label_df["Valeur"].round(2),
                color_discrete_sequence=couleurs,
                title=graph_title
            )
            fig.update_layout(
                xaxis_title=x_axis_label,
                yaxis_title=y_axis_label,
                showlegend=show_legend
            )
            if display_as_percent:
                fig.update_traces(textposition='inside', texttemplate='%{y:.2f}%')
            else:
                fig.update_traces(textposition='inside', texttemplate='%{y:.2f}')
    else:
        # Cas réponses multiples : pas de légende
        fig = go.Figure()
        if invert_axes:
            for i, row in label_df.iterrows():
                val = row["Valeur"]
                text_val = f"{val:.2f}%" if display_as_percent else f"{val:.2f}"
                fig.add_trace(go.Bar(
                    x=[val],
                    y=[row["Label"]],
                    orientation='h',
                    marker_color=couleurs[i],
                    text=[text_val],
                    textposition='inside',
                    insidetextanchor='middle',
                    name=row["Label"],
                    showlegend=show_legend
                ))
            fig.update_layout(
                title=graph_title,
                xaxis_title=x_axis_label,
                yaxis_title=y_axis_label,
                barmode='group',
                showlegend=show_legend
            )
        else:
            for i, row in label_df.iterrows():
                val = row["Valeur"]
                text_val = f"{val:.2f}%" if display_as_percent else f"{val:.2f}"
                fig.add_trace(go.Bar(
                    x=[row["Label"]],
                    y=[val],
                    marker_color=couleurs[i],
                    text=[text_val],
                    textposition='inside',
                    insidetextanchor='middle',
                    name=row["Label"],
                    showlegend=show_legend
                ))
            fig.update_layout(
                title=graph_title,
                xaxis_title=x_axis_label,
                yaxis_title=y_axis_label,
                barmode='group',
                showlegend=show_legend
            )
    return fig

def create_pie_chart(label_df, graph_title, palette):
    # ... (copier la fonction depuis app.py)
    if palette is None:
        couleurs = get_mepag_palette(len(label_df))
    else:
        couleurs = palette[:len(label_df)]
    fig = px.pie(
        label_df,
        names="Label",
        values="Valeur",
        color="Label",
        color_discrete_sequence=couleurs,
        title=graph_title
    )
    return fig

# --- FONCTION UTILE : détection couleur claire/foncée ---
def is_light_color(hex_color):
    rgb = mcolors.hex2color(hex_color)
    # Perception humaine de la luminosité (formule standard)
    luminance = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return luminance > 0.7
# --- FIN FONCTION UTILE ---

def export_chart_as_image(label_df, graph_type, graph_title, x_axis_label, y_axis_label, display_as_percent, invert_axes, palette, palette_name=None):
    # ... (copier la fonction depuis app.py)
    try:
        st.write("Début de la génération de l'image...")  # Debug log
        label_df = label_df.copy()
        # --- MODIF : ne pas trier pour Barres centre ---
        if graph_type != "Barres empilées" and graph_type != "Barres centre":
            label_df = label_df.sort_values("Valeur", ascending=True)
        # --- FIN MODIF ---
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        plt.subplots_adjust(right=0.75)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(False)
        ax.tick_params(axis='both', which='both', length=0)
        # --- MODIF : fond sombre ---
        ax.set_facecolor('#0E1117')
        fig.patch.set_facecolor('#0E1117')
        # --- FIN MODIF ---
        # Palette dynamique pour MEPAG (même logique que l'affichage)
        if palette_name == "MEPAG":
            if graph_type == "Barres empilées" and "Type" in label_df:
                couleurs = get_mepag_palette(len(label_df["Type"].unique()))
            else:
                couleurs = get_mepag_palette(len(label_df))
        else:
            if graph_type == "Barres empilées" and "Type" in label_df:
                couleurs = palette[:len(label_df["Type"].unique())]
            else:
                couleurs = palette[:len(label_df)]
        if graph_type == "Barres":
            if invert_axes:
                bars = ax.barh(label_df["Label"], label_df["Valeur"], color=couleurs)
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    if width > 0:
                        text_color = 'black' if is_light_color(couleurs[i]) else 'white'
                        ax.text(width/2, bar.get_y() + bar.get_height()/2,
                               f'{width:.1f}%' if display_as_percent else f'{width:.1f}',
                               ha='center', va='center', fontsize=10, color=text_color)
            else:
                bars = ax.bar(label_df["Label"], label_df["Valeur"], color=couleurs)
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:
                        text_color = 'black' if is_light_color(couleurs[i]) else 'white'
                        ax.text(bar.get_x() + bar.get_width()/2, height/2,
                               f'{height:.1f}%' if display_as_percent else f'{height:.1f}',
                               ha='center', va='center', fontsize=10, color=text_color)
        elif graph_type == "Camembert":
            non_zero_mask = label_df["Valeur"] > 0
            pie_data = ax.pie(label_df[non_zero_mask]["Valeur"], 
                              labels=label_df[non_zero_mask]["Label"], 
                              colors=couleurs,
                              autopct=lambda pct: f'{pct:.1f}%' if display_as_percent else f'{pct*sum(label_df["Valeur"])/100:.1f}',
                              pctdistance=0.85,
                              textprops={'color':'white'})
            if len(pie_data) == 3:
                wedges, texts, autotexts = pie_data
                for i, autotext in enumerate(autotexts):
                    color = couleurs[i % len(couleurs)]
                    text_color = 'black' if is_light_color(color) else 'white'
                    autotext.set_color(text_color)
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
            else:
                wedges, texts = pie_data
            for i, text in enumerate(texts):
                color = couleurs[i % len(couleurs)]
                text_color = 'black' if is_light_color(color) else 'white'
                text.set_color(text_color)
                text.set_fontsize(9)
        elif graph_type == "Barres empilées":
            df_pivot = label_df.pivot(index="Label", columns="Type", values="Valeur")
            if invert_axes:
                bar_containers = df_pivot.plot(kind='barh', stacked=True, color=couleurs, ax=ax).containers
                for c in bar_containers:
                    if isinstance(c, matplotlib.container.BarContainer):
                        for i, bar in enumerate(c):
                            val = bar.get_width()
                            if val > 0:
                                color = bar.get_facecolor()
                                # Convertir RGBA [0,1] en hex
                                hex_color = mcolors.to_hex(color)
                                text_color = 'black' if is_light_color(hex_color) else 'white'
                                ax.text(bar.get_x() + val/2, bar.get_y() + bar.get_height()/2,
                                        f'{val:.1f}%' if display_as_percent else f'{val:.1f}',
                                        ha='center', va='center', fontsize=10, color=text_color)
            else:
                bar_containers = df_pivot.plot(kind='bar', stacked=True, color=couleurs, ax=ax).containers
                for c in bar_containers:
                    if isinstance(c, matplotlib.container.BarContainer):
                        for i, bar in enumerate(c):
                            val = bar.get_height()
                            if val > 0:
                                color = bar.get_facecolor()
                                hex_color = mcolors.to_hex(color)
                                text_color = 'black' if is_light_color(hex_color) else 'white'
                                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + val/2,
                                        f'{val:.1f}%' if display_as_percent else f'{val:.1f}',
                                        ha='center', va='center', fontsize=10, color=text_color)
        elif graph_type == "Barres centre":
            max_val = label_df["Valeur"].max()
            if invert_axes:
                center = max_val / 2
                bars = ax.barh(label_df["Label"], label_df["Valeur"], 
                             left=[center - val/2 for val in label_df["Valeur"]], 
                             color=couleurs)
                for i, bar in enumerate(bars):
                    width = bar.get_width()
                    if width > 0:
                        text_color = 'black' if is_light_color(couleurs[i]) else 'white'
                        ax.text(bar.get_x() + width/2, bar.get_y() + bar.get_height()/2,
                               f'{width:.1f}%' if display_as_percent else f'{width:.1f}',
                               ha='center', va='center', fontsize=10, color=text_color)
            else:
                center = max_val / 2
                bars = ax.bar(label_df["Label"], label_df["Valeur"], 
                            bottom=[center - val/2 for val in label_df["Valeur"]], 
                            color=couleurs)
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:
                        text_color = 'black' if is_light_color(couleurs[i]) else 'white'
                        ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2,
                               f'{height:.1f}%' if display_as_percent else f'{height:.1f}',
                               ha='center', va='center', fontsize=10, color=text_color)
        # --- MODIF : titre en gras et texte blanc ---
        ax.set_title(graph_title, pad=20, color='white', fontweight='bold')
        ax.set_xlabel(x_axis_label, color='white')
        ax.set_ylabel(y_axis_label, color='white')
        # --- FIN MODIF ---
        # Couleur des axes
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        if display_as_percent and graph_type != "Camembert":
            if invert_axes:
                ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.1f}%'))
            else:
                ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{y:.1f}%'))
        if not invert_axes:
            plt.xticks(rotation=45, ha='right', color='white')
        if graph_type != "Camembert":
            bbox = ax.get_position()
            y_center = bbox.y0 + bbox.height/2
            legend = ax.legend(bbox_to_anchor=(1.02, y_center), loc='center left', fontsize=8, facecolor='#0E1117', edgecolor='white', labelcolor='white')
            # Pour matplotlib >=3.4, labelcolor fonctionne, sinon :
            for text in legend.get_texts():
                text.set_color('white')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        img_bytes = buf.getvalue()
        buf.close()
        plt.close()
        st.write("Image générée avec succès!")
        return img_bytes
    except Exception as e:
        st.error(f"Erreur lors de la création du graphique : {str(e)}")
        return None 