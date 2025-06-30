import pandas as pd

# Lecture du fichier Excel
df = pd.read_csv("C:/Users/admin/Documents/2025_Suivi des analyses physico-chimique.csv", sep=";")




# Afficher les premières lignes
print(df.head())
import pandas as pd
df = pd.read_excel("C:/Users/admin/Downloads/2025_Suivi des analyses physico-chimique.csv.xlsx")
print(df.columns)      # Voir les noms exacts des colonnes
print(df.info())       # Voir les types (float, object, etc.)
print(df.describe())   # Statistiques des colonnes numériques
df = df.dropna(how="any")  # Supprime toutes les lignes avec au moins une valeur manquante
colonnes_numeriques = ["PH", "NaCl", "DegreBe", "AL", "AC"]
for col in colonnes_numeriques:
    df[col] = pd.to_numeric(df[col], errors="coerce")
print(df.head())
print(df.dtype) 