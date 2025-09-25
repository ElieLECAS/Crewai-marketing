# 🚀 CrewAI Marketing - Interface Avancée

## Description

Application CrewAI pour la génération de contenu marketing dynamique avec une interface de configuration flexible et intuitive. Créez une infinité d'agents, organisez-les en crews personnalisés, et définissez des tâches séquentielles selon vos besoins.

## ✨ Nouvelles Fonctionnalités

### 🤖 Gestion des Agents

-   **Création illimitée d'agents** avec le bouton "➕ Créer un nouvel agent"
-   **Configuration complète** : nom, rôle, objectif, backstory, outils, paramètres
-   **Interface intuitive** pour gérer tous vos agents
-   **Suppression et modification** des agents existants

### 👥 Gestion des Crews

-   **Crews personnalisés** : sélectionnez les agents de votre choix
-   **Configuration flexible** : nom, description, agents sélectionnés
-   **Gestion complète** : création, modification, suppression

### 🤖 Meta Manager Automatique

-   **Analyse automatique** de votre problématique marketing
-   **Création dynamique** des tâches selon le contexte
-   **Répartition intelligente** des tâches aux agents appropriés
-   **Exécution séquentielle** optimisée

### 🎯 Campagne Marketing

-   **Sélection du crew** à utiliser pour la campagne
-   **Interface simplifiée** : problématique + contexte entreprise
-   **Exécution personnalisée** selon la configuration du crew

### 💾 Sauvegarde et Chargement

-   **Export/Import** de configurations complètes
-   **Sauvegarde** de vos agents, crews et tâches
-   **Partage** de configurations entre équipes

## 🚀 Démarrage Rapide

### Démarrage

```bash
# Installation des dépendances
pip install -r requirements.txt

# Démarrage de l'application
streamlit run streamlit_app.py
```

## ⚙️ Configuration

### Fichier .env

Créez un fichier `.env` avec vos clés API :

```env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
CREWAI_TELEMETRY=False
```

### Configuration par défaut

L'application démarre avec 4 agents pré-configurés :

-   Meta Manager (analyse et délégation)
-   Clara (recherche web et veille)
-   Julien (analyse stratégique)
-   Sophie (rédaction de contenu)

## 📖 Guide d'utilisation

### 1. Créer vos agents

1. Allez dans l'onglet "🤖 Gestion Agents"
2. Cliquez sur "➕ Créer un nouvel agent"
3. Remplissez les informations (nom, rôle, objectif, backstory, outils)
4. Sauvegardez l'agent

### 2. Créer vos crews

1. Allez dans l'onglet "👥 Gestion Crews"
2. Cliquez sur "➕ Créer un nouveau crew"
3. Sélectionnez les agents à inclure
4. Définissez le nom et la description du crew

### 3. Lancer une campagne

1. Allez dans l'onglet "🎯 Campagne"
2. Sélectionnez le crew à utiliser
3. Décrivez votre problématique marketing
4. Ajoutez le contexte de votre entreprise
5. Cliquez sur "🚀 Lancer la campagne"
6. **Le Meta Manager analysera automatiquement votre problématique et créera/répartira les tâches aux agents**

## 🎨 Exemples d'utilisation

### Crew Marketing Standard

-   **Meta Manager** : Analyse et délégation
-   **Clara** : Recherche web et veille
-   **Julien** : Analyse stratégique
-   **Sophie** : Rédaction de contenu

### Crew E-commerce

-   **Analyste Produit** : Analyse des produits
-   **Expert SEO** : Optimisation SEO
-   **Spécialiste Publicité** : Campagnes publicitaires
-   **Rédacteur E-commerce** : Contenu commercial

### Crew Créatif

-   **Directeur Créatif** : Direction artistique
-   **Concepteur Graphique** : Design visuel
-   **Copywriter** : Rédaction créative
-   **Stratège Social Media** : Stratégies réseaux sociaux

## 🔧 Outils disponibles

-   **serper_search** : Recherche web avec Serper API
-   **website_search** : Recherche sur sites web
-   **scrape_website** : Extraction de contenu web
-   **pdf_search** : Recherche dans documents PDF
-   **rag_tool** : Recherche augmentée par génération

## 📁 Structure du projet

```
Crewai-marketing/
├── src/
│   ├── agent_config.py      # Gestion des agents
│   ├── crew_config.py       # Gestion des crews
│   ├── sequential_tasks.py  # Gestion des tâches
│   ├── agents.py           # Création des agents
│   ├── crew.py             # Construction des crews
│   └── tools.py            # Outils disponibles
├── streamlit_app.py        # Interface principale
├── DEMO_INTERFACE.py      # Démonstration
├── test_interface.py      # Tests
└── INTERFACE_GUIDE.md     # Guide détaillé
```

## 🧪 Tests et Démonstration

### Tests automatiques

```bash
python test_interface.py
```

### Démonstration interactive

```bash
python DEMO_INTERFACE.py
```

## 📚 Documentation

-   **INTERFACE_GUIDE.md** : Guide détaillé de l'interface
-   **DEMO_INTERFACE.py** : Script de démonstration
-   **test_interface.py** : Tests de validation

## 🆘 Dépannage

### Problèmes courants

-   **Aucun crew disponible** : Créez d'abord des agents et des crews
-   **Erreur d'API** : Vérifiez vos clés API dans la sidebar
-   **Tâches non exécutées** : Vérifiez l'ordre des tâches et les agents assignés

### Support

-   Vérifiez les logs dans la console
-   Utilisez le bouton "🔄 Réinitialiser tout" en cas de problème
-   Exportez votre configuration avant de faire des modifications importantes

## 🐳 Docker (Optionnel)

### Construction et exécution

```bash
docker build -t crewai-marketing:latest .
docker run --rm -it -p 8501:8501 \
  -e OPENAI_API_KEY=$Env:OPENAI_API_KEY \
  crewai-marketing:latest
```

### Avec docker-compose

```bash
docker compose up --build
```

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

-   Signaler des bugs
-   Proposer des améliorations
-   Ajouter de nouveaux agents ou outils
-   Améliorer la documentation

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
