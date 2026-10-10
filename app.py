import pandas as pd #manipulation fichiers CSV
import streamlit as st #Création interface web
import glob  #pour créer un CSV à partir de chaque CSV de chaque salle
from datetime import datetime # Pour le fuseau horaire inital
from zoneinfo import ZoneInfo #Pareil

# Charger les données
fichiers_csv = glob.glob("SallesCSV/*.csv")    #Liste chaque fichiers csv du dossier SallesCSV, et les rassemble dans "fichiers_csv".

df = pd.concat( #Rassemble tous les CSV en 11
    [pd.read_csv(fichier) for fichier in fichiers_csv],  #Lit chaque fichier csv.
    ignore_index=True
)



#Configuration de l'onglet
st.set_page_config(
    page_title="Salles disponibles",
    page_icon="🏫",
    layout="centered"
)

st.title("Recherche de salles disponibles")   #Titre
st.write("Lycée Saint-Louis — Prototype")   #Texte




# Choisir le jour
jours = [
    "Lundi", "Mardi", "Mercredi",
    "Jeudi", "Vendredi", "Samedi" #Liste jours
]

jour = st.selectbox("Jour", jours) #Création Menu déroulant pour laisser choisir l'utilisateur.



        
# Choisir l'heure.
heure_actuelle = datetime.now(ZoneInfo("Europe/Paris")).time()

heure = st.time_input(
    "Heure de référence",
    value=heure_actuelle.replace(second=0, microsecond=0),
    key="heure_reference"
)





# Choisir la durée
duree = st.selectbox( #Menu déroulant pour choisir le temps prévu d'occupation de la salle
    "Durée souhaitée",
    [1,30, 60, 90, 120],
    format_func=lambda x: f"{x} minutes"
)





# Conversion HH:MM vers minutes après minuit
def en_minutes(horaire):
    h, m = map(int, str(horaire).strip()[:5].split(":"))
    return 60 * h + m

debut = heure.hour * 60 + heure.minute
fin = debut + duree







# Recherche des occupations qui chevauchent le créneau
salles = sorted(df["salle"].dropna().unique())

salles_libres = []
salles_occupees = []

for salle in salles:
    occupations_jour = df[
        (df["salle"] == salle) & (df["jour"] == jour)
    ]

    conflits = []

    for _, ligne in occupations_jour.iterrows():
        debut_occ = en_minutes(ligne["debut"])
        fin_occ = en_minutes(ligne["fin"])

        if debut_occ < fin and fin_occ > debut:
            conflits.append(ligne)

    if conflits:
        salles_occupees.append((salle, conflits))
    else:
        salles_libres.append(salle)

st.subheader(f"Salles libres : {len(salles_libres)}")

if salles_libres:
    for salle in salles_libres:
        st.success(f"Salle {salle}")
else:
    st.warning("Aucune salle libre.")

with st.expander("Voir les salles occupées"):
    for salle, conflits in salles_occupees:
        st.markdown(f"**Salle {salle}**")
        for ligne in conflits:
            st.write(
                f"{ligne['debut']}–{ligne['fin']} : "
                f"{ligne['activite']}"
            )
