# demano-bank-api

API bancaire réalisée avec Python, Django et Django REST Framework.

## Langage et technologies

- Langage : Python
- Framework : Django
- API : Django REST Framework
- Documentation : Swagger avec drf-spectacular
- Déploiement : Render

## Fonctions principales

- Créer un compte bancaire.
- Lister les comptes bancaires actifs.
- Consulter un compte bancaire.
- Effectuer un dépôt.
- Effectuer un retrait.
- Consulter l'historique des transactions.
- Consulter les cas de test manuels.

## Lancement local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Swagger

- Accueil : `http://127.0.0.1:8000/`
- Swagger : `http://127.0.0.1:8000/docs/`
- OpenAPI schema : `http://127.0.0.1:8000/api/schema/`
- Cas de test manuels : `http://127.0.0.1:8000/api/tests-manuels/`

## Documents

- Tableau des cas de test manuels : [`docs/cas_tests_manuels.pdf`](docs/cas_tests_manuels.pdf)
- Analyse C1 et C2, graphes de flot et chemins : [`docs/analyse_c1_c2_api_bancaire.pdf`](docs/analyse_c1_c2_api_bancaire.pdf)

## Déploiement Render

Paramètres du Web Service :

- Runtime : `Python 3`
- Branch : `main`
- Build Command : `bash build.sh`
- Start Command : `gunicorn banque_api.wsgi:application`

Variables d'environnement :

- `DEBUG=False`
- `ALLOWED_HOSTS=.onrender.com,demano-bank-api.vercel.app,localhost,127.0.0.1`
- `SECRET_KEY=<valeur-secrete>`

Le fichier `app.py` permet aussi de supporter l'ancienne commande Render `gunicorn app:app`, mais la commande recommandée reste `gunicorn banque_api.wsgi:application`.
