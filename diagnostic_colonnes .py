import pandas as pd
print("Début du script")
import os

fichier = "C:/Users/admin/Documents/projet fermentation/2025_Suivi des analyses physico-chimique.csv"
print("Existe ?", os.path.exists(fichier))
# Lire le fichier
fichier = "c:/Users/admin/Documents/projet fermentation/2025_Suivi des analyses physico-chimique.csv"
df = pd.read_csv(fichier)


# Nettoyer les noms de colonnes
df.columns = [
    col.strip()
       .replace(" ", "_")
       .replace("°", "Degre")
       .replace("%", "Pct")
       .replace("/", "_")
       .replace("(", "")
       .replace(")", "")
    for col in df.columns
]

# Afficher les colonnes après nettoyage
print("🧪 Colonnes après nettoyage :\n")
for col in df.columns:
    print("-", col)
