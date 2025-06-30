import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="Suivi Fermentation", layout="wide")

# ================================
# 🧾 En-tête
# ================================
st.title("🧪 Tableau de bord - Suivi des analyses physico-chimiques")
st.markdown("""
Ce tableau de bord présente l’évolution des paramètres de fermentation pendant les 20 premiers jours après remplissage.
Vous pouvez visualiser les courbes par cuve, lire un rapport automatique de conformité et consulter une prédiction du pH.
""")

# ================================
# 📂 Chargement du fichier CSV
# ================================
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, sep=";", encoding="latin1")
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("%", "")
        .str.replace("°Be", "DegreBe")
        .str.replace("°", "Degre")
        .str.replace("Na Cl", "_NaCl")
        .str.replace(" ", "_")
    )
    if "___NaCl" in df.columns:
        df = df.rename(columns={"___NaCl": "_NaCl"})
    if "N\u00b0Cuve" in df.columns:
        df = df.rename(columns={"N\u00b0Cuve": "NDegreCuve"})

    if "La_date" in df.columns and "Date_de_remplissage" in df.columns:
        df["La_date"] = pd.to_datetime(df["La_date"], dayfirst=True, errors="coerce")
        df["Date_de_remplissage"] = pd.to_datetime(df["Date_de_remplissage"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["La_date", "Date_de_remplissage"])
        df["Jours_apres_remplissage"] = (df["La_date"] - df["Date_de_remplissage"]).dt.days

    for col in ["DegreBe", "_NaCl", "PH", "AL", "AC", "TDegreC"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")

    top_5_cuves = df["NDegreCuve"].value_counts().head(5).index.tolist()
    df = df[df["NDegreCuve"].isin(top_5_cuves)]
    df = df[df["Jours_apres_remplissage"].between(0, 20)]
    return df

# ================================
# 📁 Barre latérale (menu)
# ================================
df = load_data("2025_Suivi des analyses physico-chimique.csv")
menu = st.sidebar.radio("Navigation", ["Accueil", "Graphiques", "Rapport", "Prédiction"])

# ================================
# 📊 Accueil
# ================================
if menu == "Accueil":
    st.subheader("📋 Aperçu des données")
    st.dataframe(df.head(20))
    st.markdown(f"""
    **Paramètres disponibles :** DegreBe, _NaCl, PH, AL, AC, TDegreC  
    **Nombre de cuves sélectionnées :** {df['NDegreCuve'].nunique()}  
    **Taille du jeu de données :** {df.shape[0]} lignes
    """)

# ================================
# 📈 Graphiques
# ================================
elif menu == "Graphiques":
    st.subheader("📈 Évolution des paramètres")
    param = st.selectbox("Choisir un paramètre à tracer", ["DegreBe", "_NaCl", "PH", "AL", "AC", "TDegreC"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=df, x="Jours_apres_remplissage", y=param, hue="NDegreCuve", marker="o", ax=ax)
    ax.set_title(f"Évolution de {param} pendant les 20 premiers jours")
    ax.grid(True)
    st.pyplot(fig)

# ================================
# 📄 Rapport
# ================================
elif menu == "Rapport":
    st.subheader("📝 Rapport automatique")

    df["PH"] = pd.to_numeric(df["PH"].astype(str).str.replace(",", "."), errors="coerce")
    df["AL"] = pd.to_numeric(df["AL"].astype(str).str.replace(",", "."), errors="coerce")

    rapport = []
    for _, row in df.iterrows():
        cuve = row["NDegreCuve"]
        date = row["La_date"].strftime("%d/%m/%Y")
        ph = row["PH"]
        al = row["AL"]
        ac = row["AC"]
        sel = row["_NaCl"]

        bloc = [f"**🧪 Cuve {cuve} | Date : {date}**"]

        if pd.isna(ph):
            bloc.append("⚠️ pH manquant")
            frequence = "Inconnue"
        elif ph <= 4.2:
            bloc.append("✔️ pH conforme (≤ 4.2)")
            frequence = "Analyse chaque 20 jours"
        elif ph < 4.5:
            bloc.append("⚠️ pH > 4.2 (Contrôle chaque 2 jours)")
            frequence = "Analyse chaque 2 jours"
        else:
            bloc.append("❌ pH ≥ 4.5 (Risque élevé – Contrôle chaque semaine)")
            frequence = "Analyse chaque semaine"

        bloc.append(f"📌 Fréquence recommandée : {frequence}")

        if not pd.isna(ph) and ph < 7:
            if not pd.isna(al):
                bloc.append("✔️ Acidité libre > 0.8 %" if al > 0.8 else "❌ Acidité libre insuffisante (≤ 0.8 %)")
            else:
                bloc.append("⚠️ AL manquant")
        else:
            bloc.append("ℹ️ pH ≥ 7 : contrôle AL non requis.")

        if not pd.isna(ac):
            if 0.11 <= ac <= 0.13:
                bloc.append("✔️ Acidité combinée dans la norme (0.11 - 0.13 N)")
            else:
                bloc.append(f"❌ Acidité combinée hors norme ({ac:.3f} N)")
        else:
            bloc.append("⚠️ Acidité combinée manquante")

        bloc.append("ℹ️ NaCl mesuré. Contrôle : mise en saumure + 5-7 jours après")
        bloc.append("---")
        rapport.append("\n".join(bloc))

    st.markdown("\n\n".join(rapport))

# ================================
# 🔮 Prédiction
# ================================
elif menu == "Prédiction":
    st.subheader("🔮 Prédiction du pH par cuve")

    cuves = df["NDegreCuve"].unique().tolist()
    selected_cuve = st.selectbox("Sélectionner une cuve", cuves)

    df_cuve = df[df["NDegreCuve"] == selected_cuve].dropna(subset=["PH", "Jours_apres_remplissage"])

    if len(df_cuve) >= 5:
        X = df_cuve[["Jours_apres_remplissage"]]
        y = df_cuve["PH"]
        model = LinearRegression()
        model.fit(X, y)

        dernier_jour = df_cuve["Jours_apres_remplissage"].max()
        jours_futurs = np.array([dernier_jour + i for i in range(1, 4)]).reshape(-1, 1)
        ph_predits = model.predict(jours_futurs)

        jours_tous = np.append(X["Jours_apres_remplissage"], jours_futurs.flatten()).reshape(-1, 1)
        predictions_tous = model.predict(jours_tous)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x=X["Jours_apres_remplissage"], y=y, label="Valeurs réelles", ax=ax)
        ax.plot(jours_tous, predictions_tous, color="red", label="Tendance prédite")
        ax.set_title(f"Évolution et prédiction du pH – Cuve {selected_cuve}")
        ax.set_xlabel("Jours après remplissage")
        ax.set_ylabel("pH")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

        st.markdown("### 📈 Prédictions à venir :")
        for i, jour in enumerate(jours_futurs.flatten(), 1):
            st.write(f"➡️ Jour {jour} : **pH prédit = {ph_predits[i - 1]:.2f}**")
            if ph_predits[i - 1] >= 4.5:
                st.error("🚨 Attention : Risque de dépassement critique du pH !")
            elif ph_predits[i - 1] > 4.2:
                st.warning("⚠️ pH élevé, surveillance conseillée.")
    else:
        st.warning("Pas assez de données pour cette cuve (minimum 5 valeurs).")
