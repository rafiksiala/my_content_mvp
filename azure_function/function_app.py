import azure.functions as func
import logging
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="recommend_function")
def recommend_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function "recommend_function" triggered.')

    user_id = req.params.get('user_id')
    if not user_id:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None
        if req_body:
            user_id = req_body.get('user_id')

    if not user_id:
        return func.HttpResponse(
            "Missing 'user_id' parameter in query string or body.",
            status_code=400
        )

    # Charger les articles
    articles_path = os.path.join(os.path.dirname(__file__), "articles.json")
    try:
        with open(articles_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except Exception as e:
        logging.error(f"Error loading articles: {e}")
        return func.HttpResponse(
            "Error loading article data.",
            status_code=500
        )

    recommended = articles[:5]

    return func.HttpResponse(
        json.dumps(recommended),
        mimetype="application/json",
        status_code=200
    )
