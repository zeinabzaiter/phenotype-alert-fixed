import streamlit as st
import pandas as pd
import altair as alt

# Fonction pour charger les données depuis GitHub
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/zeinabzaiter/phenotype-alert-fixed/main/weekly_staph_phenotypes.csv"
    df = pd.read_csv(url)
    df['Week'] = pd.to_datetime(df['Week'])  # Conversion de la colonne Week en datetime
    return df

# Charger les données
df = load_data()

# Sélectionner les colonnes importantes
phenotypes = [col for col in df.columns if col.lower() != 'week' and 'total' not in col.lower()]

# Choisir un phénotype à afficher
phenotype_choisi = st.selectbox("Select a phenotype to display:", phenotypes)

# Fonction pour calculer le seuil d'alerte selon la règle de Tukey
def seuil_tukey(values):
    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    return q3 + 1.5 * iqr

# Calcul du seuil pour le phénotype choisi
seuil = seuil_tukey(df[phenotype_choisi])

# Ajouter une colonne pour indiquer les alertes
df['Alerte'] = df[phenotype_choisi] > seuil

# Créer le graphique
base = alt.Chart(df).encode(
    x=alt.X('Week:T', title='Week'),
    y=alt.Y(f'{phenotype_choisi}:Q', title='Number of isolates'),
    tooltip=[
        alt.Tooltip('Week:T', title='Week'),
        alt.Tooltip(f'{phenotype_choisi}:Q', title='Resistance %'),
        alt.Tooltip('Alerte:N', title='Alert')
    ]
)

line = base.mark_line(color='blue')
points = base.mark_circle(size=60).encode(
    color=alt.condition(
        alt.datum.Alerte,
        alt.value('red'),  # Rouge si alerte
        alt.value('blue')  # Bleu sinon
    )
)

graphique = (line + points).properties(
    title=f'Evolution of {phenotype_choisi} with Alerts Highlighted',
    width=800,
    height=400
).interactive()

# Affichage du graphique
st.title("Phenotypic Resistance Alert Dashboard")
st.altair_chart(graphique, use_container_width=True)
