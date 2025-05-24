#!/bin/bash

# Nom de la Function App sur Azure
FUNCTION_APP_NAME="my-content-func"

# Étape 1 : Vérification de session Azure
echo "Vérification de la session Azure..."

if az account show > /dev/null 2>&1; then
    echo "Déjà connecté à Azure."
else
    echo "Connexion à Azure via device code..."
    az login --use-device-code
fi

# Étape 2 (optionnelle) : Sélection de l’abonnement si nécessaire
# az account set --subscription "Nom de votre abonnement"

# Étape 3 : Déploiement de la Function App
echo "Déploiement de la Function App : $FUNCTION_APP_NAME"
func azure functionapp publish $FUNCTION_APP_NAME

echo "Déploiement terminé."
