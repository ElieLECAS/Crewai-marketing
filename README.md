# CrewAI Marketing Crew

Ce projet met en place une équipe marketing basée sur CrewAI avec un agent Manager (meta-agent) qui collecte la demande et répartit les tâches à des sous-agents spécialisés (SEO, Contenu, Réseaux sociaux, Emailing, Analytics). L'application est exécutable en local (CLI et Streamlit) ou via Docker et docker-compose.

## Prérequis

-   Python 3.10+
-   Compte OpenAI (ou fournisseur compatible OpenAI)
-   Clé API `OPENAI_API_KEY`

## Option A — Interface Streamlit (recommandé)

### Local

```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Ensuite, ouvre l’URL affichée (par défaut `http://localhost:8501`) et saisis tes exigences + checklist.

### Docker

```bash
docker build -t crewai-marketing:latest .
docker run --rm -it -p 8501:8501 \
  -e OPENAI_API_KEY=$Env:OPENAI_API_KEY \
  crewai-marketing:latest
```

### docker-compose

```bash
docker compose up --build
```

Puis ouvre `http://localhost:8501`.

## Configuration

Créez un fichier `.env` à la racine (ou utilisez des variables d'environnement) :

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
CREWAI_TELEMETRY=False

# Optionnel: Serper pour recherche web
SERPER_API_KEY=...
```

Variables optionnelles:

-   `OPENAI_BASE_URL` pour un fournisseur compatible OpenAI
-   `OPENAI_MODEL` pour choisir le modèle (ex: `gpt-4o-mini`, `gpt-4o`)
-   `SERPER_API_KEY` pour activer la recherche web via Serper

## Structure

```
.
├─ streamlit_app.py     # UI Streamlit (interface principale)
├─ src/
│  ├─ agents.py         # Définition des agents CrewAI
│  ├─ agent_config.py   # Configuration des agents
│  ├─ sequential_tasks.py # Gestionnaire de tâches séquentielles
│  ├─ tools.py          # Outils disponibles pour les agents
│  └─ crew.py           # Orchestrateur Crew
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
└─ .env.example
```

## Fonctionnalités

-   **Interface Streamlit** avec 3 onglets :
    -   🎯 **Campagne** : Saisie des exigences et checklist pré-kickoff
    -   ⚙️ **Configuration Agents** : Personnalisation des agents, rôles, objectifs et outils
    -   🔧 **Outils** : Gestion des outils disponibles (Serper, recherche web, scraping)
-   **Outils intégrés** : Recherche web (Serper), recherche sur site, scraping
-   **Configuration flexible** : Export/import des configurations d'agents
-   **Docker ready** : Déploiement facile avec docker-compose

## Notes

-   Le Manager consolide la demande et coordonne les sous-agents via des tâches dédiées.
-   Chaque agent peut être configuré individuellement avec ses propres outils.
-   Les outils de recherche web nécessitent une clé API Serper (optionnelle).
