import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Recommandation My Content", layout="centered")
st.markdown("""
    <style>
        .block-container {
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 1rem;
            max-width: 60%;
        }
        header, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)
st.title("Recommandation d'articles - My Content")

# Charger dynamiquement les user_id depuis clicks_sample.csv
try:
    df = pd.read_csv("data/clicks_sample.csv")
    user_ids = sorted(df["user_id"].unique().tolist())
    user_ids = [str(user_id) for user_id in user_ids]
except Exception:
    st.error("Impossible de charger la liste des utilisateurs depuis clicks_sample.csv.")
    user_ids = []

if user_ids:
    selected_user = st.selectbox("Choisissez un utilisateur :", user_ids)

    if st.button("Afficher les recommandations"):
        base_url = "https://my-content-func.azurewebsites.net/api/recommend_articles"
        url = f"{base_url}?user_id={selected_user}"

        try:
            response = requests.get(url)

            if response.status_code == 404:
                st.warning(response.json().get("error", "Utilisateur inconnu."))

            elif response.status_code == 200:
                articles = response.json()
                if not articles:
                    st.info("Aucun article recommandé pour cet utilisateur.")
                else:
                    st.success("Voici les articles recommandés :")
                    for article in articles:
                        st.markdown(
                            f"""
                            - 📰 **Article ID**: `{article['article_id']}`
                                - 📚 Catégorie : `{article.get('category_id', 'N/A')}`
                                - 🏢 Publisher : `{article.get('publisher_id', 'N/A')}`
                                - 🔢 Score de popularité : `{article.get('score', 'N/A')}`
                            """
                        )

            else:
                st.error(f"Erreur {response.status_code} : {response.text}")

        except Exception as e:
            st.error(f"Erreur lors de la requête : {e}")
else:
    st.warning("Aucun utilisateur disponible.")
