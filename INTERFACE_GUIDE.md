# 🚀 Guide d'utilisation de l'Interface CrewAI Marketing

## Vue d'ensemble

L'interface CrewAI Marketing a été complètement repensée pour offrir une expérience de configuration flexible et intuitive. Vous pouvez maintenant créer une infinité d'agents, les organiser en crews personnalisés, et définir des tâches séquentielles selon vos besoins.

## 🎯 Fonctionnalités principales

### 1. Gestion des Agents (Onglet "🤖 Gestion Agents")

-   **Création illimitée d'agents** avec le bouton "➕ Créer un nouvel agent"
-   **Configuration complète** : nom, rôle, objectif, backstory, outils, paramètres
-   **Suppression d'agents** avec confirmation
-   **Affichage organisé** de tous les agents existants

### 2. Gestion des Crews (Onglet "👥 Gestion Crews")

-   **Création de crews personnalisés** avec le bouton "➕ Créer un nouveau crew"
-   **Sélection d'agents** parmi ceux disponibles
-   **Configuration flexible** : nom, description, agents sélectionnés
-   **Gestion des crews** : visualisation, suppression

### 3. Configuration des Tâches (Onglet "📋 Configuration Tâches")

-   **Création de tâches personnalisées** pour chaque crew
-   **Assignation d'agents** à des tâches spécifiques
-   **Ordre séquentiel** : définissez l'ordre d'exécution des tâches
-   **Gestion complète** : ajout, suppression, modification de l'ordre

### 4. Campagne Marketing (Onglet "🎯 Campagne")

-   **Sélection du crew** à utiliser pour la campagne
-   **Interface simplifiée** : problématique + contexte entreprise
-   **Exécution personnalisée** selon la configuration du crew sélectionné

## 🔄 Workflow recommandé

### Étape 1 : Créer vos agents

1. Allez dans l'onglet "🤖 Gestion Agents"
2. Cliquez sur "➕ Créer un nouvel agent"
3. Remplissez les informations :
    - **Nom** : identifiant unique
    - **Rôle** : fonction de l'agent
    - **Objectif** : ce qu'il doit accomplir
    - **Backstory** : son histoire et compétences
    - **Outils** : sélectionnez les outils disponibles
    - **Paramètres** : max iterations, verbose, etc.

### Étape 2 : Créer vos crews

1. Allez dans l'onglet "👥 Gestion Crews"
2. Cliquez sur "➕ Créer un nouveau crew"
3. Remplissez les informations :
    - **Nom** : identifiant du crew
    - **Description** : rôle du crew
    - **Agents** : sélectionnez les agents à inclure

### Étape 3 : Configurer les tâches

1. Allez dans l'onglet "📋 Configuration Tâches"
2. Sélectionnez le crew à configurer
3. Cliquez sur "➕ Ajouter une nouvelle tâche"
4. Pour chaque tâche :
    - **Nom** : identifiant de la tâche
    - **Description** : ce que la tâche doit faire
    - **Agent assigné** : qui exécute la tâche
    - **Résultat attendu** : format du livrable
    - **Ordre** : position dans la séquence

### Étape 4 : Lancer une campagne

1. Allez dans l'onglet "🎯 Campagne"
2. Sélectionnez le crew à utiliser
3. Décrivez votre problématique marketing
4. Ajoutez le contexte de votre entreprise (optionnel)
5. Cliquez sur "🚀 Lancer la campagne avec le crew sélectionné"

## 💾 Sauvegarde et Chargement

### Export de configuration

-   Allez dans l'onglet "🔧 Outils"
-   Cliquez sur "📥 Exporter configuration complète"
-   Téléchargez le fichier JSON avec toutes vos configurations

### Import de configuration

-   Allez dans l'onglet "🔧 Outils"
-   Utilisez "📤 Importer configuration"
-   Sélectionnez un fichier JSON de configuration
-   Toutes vos configurations seront restaurées

## 🎨 Exemples d'utilisation

### Exemple 1 : Crew Marketing Standard

-   **Agent 1** : Meta Manager (analyse et délégation)
-   **Agent 2** : Chercheur Web (recherche d'informations)
-   **Agent 3** : Analyste Stratégique (analyse contextuelle)
-   **Agent 4** : Rédacteur (création de contenu)

### Exemple 2 : Crew Spécialisé E-commerce

-   **Agent 1** : Analyste Produit
-   **Agent 2** : Expert SEO
-   **Agent 3** : Spécialiste Publicité
-   **Agent 4** : Rédacteur E-commerce

### Exemple 3 : Crew Créatif

-   **Agent 1** : Directeur Créatif
-   **Agent 2** : Concepteur Graphique
-   **Agent 3** : Copywriter
-   **Agent 4** : Stratège Social Media

## 🔧 Configuration avancée

### Outils disponibles

-   **serper_search** : Recherche web avec Serper API
-   **website_search** : Recherche sur sites web
-   **scrape_website** : Extraction de contenu web
-   **pdf_search** : Recherche dans documents PDF
-   **rag_tool** : Recherche augmentée par génération

### Types de processus

-   **Sequential** : Exécution séquentielle des tâches
-   **Hierarchical** : Exécution hiérarchique (à venir)

## 🚨 Bonnes pratiques

1. **Nommage cohérent** : Utilisez des noms clairs et descriptifs
2. **Objectifs précis** : Définissez des objectifs spécifiques et mesurables
3. **Ordre logique** : Organisez les tâches dans un ordre logique
4. **Tests réguliers** : Testez vos configurations avec des problématiques simples
5. **Sauvegarde fréquente** : Exportez régulièrement vos configurations

## 🆘 Dépannage

### Problèmes courants

-   **Aucun crew disponible** : Créez d'abord des agents et des crews
-   **Erreur d'API** : Vérifiez vos clés API dans la sidebar
-   **Tâches non exécutées** : Vérifiez l'ordre des tâches et les agents assignés

### Support

-   Vérifiez les logs dans la console
-   Utilisez le bouton "🔄 Réinitialiser tout" en cas de problème
-   Exportez votre configuration avant de faire des modifications importantes
