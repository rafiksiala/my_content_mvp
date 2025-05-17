import azure.functions as func
import pandas as pd
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# === CHARGEMENT DES DONNÉES AU DÉMARRAGE DE L'APPLICATION ===

base_path = os.path.dirname(__file__)
clicks_path = os.path.join(base_path, "data/clicks_sample.csv")
meta_path = os.path.join(base_path, "data/articles_metadata.csv")

try:
    # Chargement des clics utilisateur
    df_clicks = pd.read_csv(clicks_path)
    df_clicks["user_id"] = df_clicks["user_id"].astype(str)
    df_clicks["click_article_id"] = df_clicks["click_article_id"].astype(str)

    # Chargement des métadonnées des articles
    df_meta = pd.read_csv(meta_path)
    df_meta["article_id"] = df_meta["article_id"].astype(str)

    # Liste des articles valides (présents dans les métadonnées)
    available_articles = set(df_meta["article_id"])

    # Calcul de la popularité : nombre de clics par article
    popularity_df = (
        df_clicks.groupby("click_article_id")
        .size()
        .reset_index(name="click_count")
        .sort_values("click_count", ascending=False)
    )

except Exception as e:
    # Gestion des erreurs de chargement
    print(f"Error loading assets: {e}")
    df_clicks, df_meta, popularity_df, available_articles = None, None, None, set()

# === ROUTE PRINCIPALE DE L'API ===

@app.route(route="recommend_articles")
def recommend_articles(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.params.get("user_id")

    # Vérifie que l'ID utilisateur a bien été fourni
    if not user_id:
        return func.HttpResponse("Missing user_id", status_code=400)

    try:
        user_id = str(user_id)

        # Vérifie que l'utilisateur est connu dans les données
        if user_id not in df_clicks["user_id"].values:
            return func.HttpResponse(
                json.dumps({"error": f"user_id '{user_id}' non trouvé dans les interactions."}),
                mimetype="application/json",
                status_code=404
            )

        # Récupère les articles déjà vus par l'utilisateur
        seen_articles = set(df_clicks[df_clicks["user_id"] == user_id]["click_article_id"])

        # Filtrage des articles non vus et présents dans les métadonnées
        candidate_df = popularity_df[~popularity_df["click_article_id"].isin(seen_articles)]
        candidate_df = candidate_df[candidate_df["click_article_id"].isin(available_articles)]

        # Sélection des 5 articles les plus populaires parmi les candidats
        top_df = candidate_df.head(5)

        # Construction de la réponse JSON avec des métadonnées associées
        results = []
        for _, row in top_df.iterrows():
            article_id = row["click_article_id"]
            article_info = df_meta[df_meta["article_id"] == article_id].iloc[0]
            results.append({
                "article_id": str(article_id),  # ou int(article_id) si tu préfères
                "score": int(row["click_count"]),
                "category_id": str(article_info.get("category_id", "")),
                "publisher_id": str(article_info.get("publisher_id", ""))
            })


        # Envoi de la réponse HTTP
        return func.HttpResponse(
            json.dumps(results),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        # Gestion des erreurs inattendues
        return func.HttpResponse(
            f"Error generating recommendations: {str(e)}",
            status_code=500
        )
