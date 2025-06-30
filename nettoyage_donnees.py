import pandas as pd

def load_data(path):
    df = pd.read_csv(path, sep=";", encoding="latin1")

    # Nettoyage des colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("%", "")
        .str.replace("°Be", "DegreBe")
        .str.replace("°", "Degre")
        .str.replace("Na Cl", "_NaCl")
        .str.replace("NaCl", "_NaCl")  # Ajout pour sécurité
        .str.replace(" ", "_")
    )

    # Sécurité : forcer l'existence de la colonne "_NaCl"
    if "_NaCl" not in df.columns:
        for col in df.columns:
            if "NaCl" in col:
                df = df.rename(columns={col: "_NaCl"})

    # Correction des noms de colonnes liés à NaCl
    for col in df.columns:
        if "NaCl" in col and col != "_NaCl":
            df = df.rename(columns={col: "_NaCl"})

    if "___NaCl" in df.columns:
        df = df.rename(columns={"___NaCl": "_NaCl"})

    # Renommage des colonnes si besoin
    if "N°Cuve" in df.columns:
        df = df.rename(columns={"N°Cuve": "NDegreCuve"})
    if "N\u00b0Cuve" in df.columns:
        df = df.rename(columns={"N\u00b0Cuve": "NDegreCuve"})

    # Conversion des dates
    if "La_date" in df.columns and "Date_de_remplissage" in df.columns:
        df["La_date"] = pd.to_datetime(df["La_date"], dayfirst=True, errors="coerce")
        df["Date_de_remplissage"] = pd.to_datetime(df["Date_de_remplissage"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["La_date", "Date_de_remplissage"])
        df["Jours_apres_remplissage"] = (df["La_date"] - df["Date_de_remplissage"]).dt.days

    # Conversion des colonnes numériques
    for col in ["DegreBe", "_NaCl", "PH", "AL", "AC", "TDegreC"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

    # ✅ Filtrer les cuves contenant uniquement des chiffres
    if "NDegreCuve" in df.columns:
        df = df[df["NDegreCuve"].astype(str).str.isnumeric()]
       

    # Garder uniquement les jours 0 à 20
    df = df[df["Jours_apres_remplissage"].between(0, 20)]

    return df
