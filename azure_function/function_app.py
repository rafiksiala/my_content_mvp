import azure.functions as func
import pandas as pd
import numpy as np
import json
import os
import requests
import pickle

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# === CHARGEMENT DES DONNÉES ET EMBEDDINGS ===

base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, "data")
clicks_path = os.path.join(data_path, "clicks_sample.csv")
meta_path = os.path.join(data_path, "articles_metadata.csv")
blob_url = "https://articlesembeddings.blob.core.windows.net/articles-embeddings/articles_embeddings_pca.pickle"

try:
    # Chargement CSV
    df_clicks = pd.read_csv(clicks_path)
    df_meta = pd.read_csv(meta_path)

    # Encodage natif, sans cast en string
    article_ids = df_clicks["click_article_id"].unique()
    available_articles = set(article_ids)

    # Chargement des embeddings depuis Azure Blob
    response = requests.get(blob_url)
    response.raise_for_status()
    article_embeddings = pickle.loads(response.content)

    # Définition du modèle content-based
    class ContentBasedRecommender:
        def __init__(self, article_ids, article_embeddings, interactions_df):
            self.article_ids = np.array(article_ids)
            self.article_embeddings = article_embeddings
            self.interactions_df = interactions_df
            self.article_index = {article_id: idx for idx, article_id in enumerate(article_ids)}

        def get_name(self):
            return 'Content-Based'

        def recommend_top_articles(self, user_id, topn=5):
            # Articles vus par l'utilisateur
            seen_articles = set(self.interactions_df[self.interactions_df["user_id"] == user_id]["click_article_id"])
            seen_idxs = [self.article_index[a] for a in seen_articles if a in self.article_index]
            
            # Si l'utilisateur n'a vu aucun article valide
            if not seen_idxs:
                return []

            # Construction du profil utilisateur
            user_profile = self.article_embeddings[seen_idxs].mean(axis=0)
            user_profile /= np.linalg.norm(user_profile)

            # Articles candidats (non vus)
            candidates = [aid for aid in self.article_ids if aid not in seen_articles and aid in self.article_index]

            # Scorer les articles candidats
            scored = []
            for article_id in candidates:
                idx = self.article_index[article_id]
                article_vec = self.article_embeddings[idx]
                article_vec /= np.linalg.norm(article_vec)
                score = np.dot(user_profile, article_vec)
                scored.append((article_id, score))

            # Retourner les top articles triés
            scored_sorted = sorted(scored, key=lambda x: -x[1])[:topn]
            return scored_sorted

    # Initialisation unique du modèle
    cb_recommender = ContentBasedRecommender(
        article_ids=article_ids,
        article_embeddings=article_embeddings,
        interactions_df=df_clicks
    )

except Exception as e:
    print(f"Error during startup: {e}")
    df_clicks, df_meta, cb_recommender = None, None, None

# === ROUTE AZURE FUNCTION ===

@app.route(route="recommend_articles")
def recommend_articles(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.params.get("user_id")

    if not user_id:
        return func.HttpResponse("Missing user_id", status_code=400)

    try:
        user_id = int(user_id)

        if user_id not in df_clicks["user_id"].values:
            return func.HttpResponse(
                json.dumps({"error": f"user_id {user_id} non trouvé."}),
                mimetype="application/json",
                status_code=404
            )

        top_recs = cb_recommender.recommend_top_articles(user_id=user_id, topn=5)

        results = []
        for article_id, score in top_recs:
            meta = df_meta[df_meta["article_id"] == article_id]
            if meta.empty:
                continue
            article_info = meta.iloc[0]
            results.append({
                "article_id": int(article_id),
                "score": float(score),
                "category_id": int(article_info.get("category_id", 0)),
                "publisher_id": int(article_info.get("publisher_id", 0))
            })

        return func.HttpResponse(json.dumps(results), mimetype="application/json", status_code=200)

    except Exception as e:
        return func.HttpResponse(f"Error generating recommendations: {str(e)}", status_code=500)
