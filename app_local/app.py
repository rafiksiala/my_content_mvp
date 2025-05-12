import streamlit as st
import requests

st.set_page_config(page_title="Recommandation My Content")

st.title("Recommandation d'articles - My Content")

# Simule une liste d'utilisateurs
users = ["user_001", "user_002", "user_003"]
selected_user = st.selectbox("Choisissez un utilisateur :", users)

if st.button("Afficher les recommandations"):
    # Remplace ci-dessous par ton URL réelle après déploiement
    base_url = "https://my-content-func.azurewebsites.net/api/recommend_function"
    url = f"{base_url}?user_id={selected_user}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()
            st.success("Voici les articles recommandés :")
            for article in articles:
                st.markdown(f"**{article['title']}** (ID: `{article['id']}`)")
        else:
            st.error(f"Erreur {response.status_code} : {response.text}")
    except Exception as e:
        st.error(f"Erreur lors de la requête : {e}")
