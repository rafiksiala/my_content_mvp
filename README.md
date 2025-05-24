# MyContent MVP – Système de recommandation d’articles (Content-Based)

Ce projet met en œuvre un système de recommandation d’articles basé sur la **similarité de contenu** entre les articles, en utilisant des **embeddings vectoriels stockés sur Azure Blob Storage**.

---

## Fonctionnalités

- Recommandation de 5 articles personnalisés via similarité d'embeddings
- Approche content-based avec vecteurs d’articles pré-calculés
- Embeddings stockés sur Azure Blob Storage et chargés dynamiquement
- Interface utilisateur locale en Streamlit
- Données utilisateurs et articles issues de jeux de données publics

---

## Structure du dépôt

```
my_content_mvp/
│
├── azure_function/                  # Code de la fonction Azure (backend)
│   ├── function_app.py              # Script principal avec la logique de recommandation
│   ├── requirements.txt             # Dépendances nécessaires à l'exécution sur Azure
│   ├── host.json                    # Fichier de configuration pour Azure Functions
│   ├── .funcignore                  # Fichiers à ignorer lors du déploiement sur Azure
│   └── data/
│       ├── clicks_sample.csv        # Données d’interactions utilisateur/article
│       └── articles_metadata.csv    # Métadonnées des articles
│
├── streamlit_app/                   # Application Streamlit pour tester l'API
│   ├── app.py                       # Interface utilisateur avec appel à l'API Azure
│   └── data/
│       ├── clicks_sample.csv        # Données d’interactions utilisateur/article
│       └── articles_metadata.csv    # Métadonnées des articles
│
├── deploy_function.sh               # Script CLI pour déploiement rapide via terminal
├── .gitignore                       # Fichiers/dossiers exclus du versioning
└── README.md                        # Documentation du projet
```

---

## 🔧 Installation & exécution

### 1. Cloner le projet

```bash
git clone https://github.com/rafiksiala/my_content_mvp.git
cd my_content_mvp
```

---

### 2. Lancer l’interface Streamlit

```bash
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py
```

---

### 3. Déployer la fonction Azure

L’Azure Function est déclenchée par une requête HTTP. Elle :

- télécharge dynamiquement les embeddings depuis Azure Blob Storage,
- calcule la similarité entre les articles lus par un utilisateur,
- retourne les 5 articles les plus pertinents.

#### Méthode 1 — Déploiement via Visual Studio Code (recommandée si vous travaillez seul)

1. Ouvrir le projet dans VSCode
2. Clic droit sur le dossier `azure_function`
3. Sélectionner **"Deploy to Function App"**
4. Choisir l'application `my-content-func`

> Cette méthode rapide et visuelle est idéale pour un usage local sans configuration complexe.

#### Méthode 2 — Déploiement automatisé via terminal

Exécuter le script suivant depuis la racine du projet :

```bash
./deploy_function.sh
```

Ce script :

- vérifie si vous êtes connecté à Azure (`az account show`)
- lance `az login --use-device-code` si nécessaire
- publie la fonction avec `func azure functionapp publish my-content-func`

> Parfait pour les automatisations ou intégrations CI/CD.

---

### 4. Tester l’API

```http
GET https://my-content-func.azurewebsites.net/api/recommend_articles?user_id=0
```

---

## Architecture technique

- **Backend** : Azure Functions en Python
- **Frontend** : Streamlit (Python)
- **Stockage** : Azure Blob Storage pour les embeddings
- **Modèle** : Approche content-based avec similarité cosinus

---

## Évolutions possibles

- API REST complète (POST, logs, ajout d’utilisateur)
- Mise à jour dynamique des embeddings
- Base de données temps réel
- Recombinaison content + collaborative filtering
- Interface mobile ou progressive web app (PWA)
