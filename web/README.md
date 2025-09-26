# Interface Web CrewAI Marketing

Interface utilisateur moderne pour la plateforme CrewAI Marketing, développée avec HTML, CSS et JavaScript vanilla.

## 🎯 Fonctionnalités

### ✅ **Dashboard**

-   Vue d'ensemble des statistiques
-   Campagnes récentes
-   Métriques en temps réel

### ✅ **Gestion des Agents**

-   Création, modification, suppression d'agents
-   Configuration des outils et paramètres
-   Interface intuitive avec cartes

### ✅ **Gestion des Crews**

-   Création et gestion des équipes d'agents
-   Sélection multiple d'agents
-   Configuration des processus

### ✅ **Campagnes Marketing**

-   Création de campagnes avec problématique
-   Exécution avec clés API
-   Visualisation des résultats
-   Parsing intelligent des outputs

### ✅ **Gestion des Fichiers**

-   Upload de fichiers PDF
-   Drag & Drop
-   Association aux campagnes

## 🚀 Démarrage rapide

### Option 1 : Script automatique (Recommandé)

```bash
python start_ui.py
```

### Option 2 : Démarrage manuel

```bash
# 1. Démarrer l'API
docker-compose up -d

# 2. Démarrer le serveur web
python web_server.py
```

### Option 3 : Serveur web simple

```bash
# Depuis le dossier web
cd web
python -m http.server 3000
```

## 🌐 Accès

-   **Interface Web** : http://localhost:3000
-   **API Documentation** : http://localhost:8000/docs
-   **API** : http://localhost:8000

## 📁 Structure des fichiers

```
web/
├── index.html              # Page principale
├── static/
│   ├── css/
│   │   └── style.css       # Styles CSS
│   ├── js/
│   │   ├── api.js          # Client API
│   │   ├── ui.js           # Gestionnaire UI
│   │   └── app.js          # Application principale
│   └── images/             # Images et icônes
└── README.md               # Documentation
```

## 🎨 Design

### Caractéristiques

-   **Design moderne** avec CSS Grid et Flexbox
-   **Responsive** pour mobile, tablette et desktop
-   **Thème sombre/clair** (préparé)
-   **Animations fluides** avec CSS transitions
-   **Icônes Font Awesome** pour une meilleure UX

### Couleurs

-   **Primaire** : Bleu (#3b82f6)
-   **Secondaire** : Gris (#64748b)
-   **Accent** : Orange (#f59e0b)
-   **Succès** : Vert (#10b981)
-   **Erreur** : Rouge (#ef4444)

## 🔧 Configuration

### Variables d'environnement

L'interface se connecte automatiquement à l'API sur `http://localhost:8000`.

Pour changer l'URL de l'API, modifiez dans `static/js/api.js` :

```javascript
class CrewAIApi {
    constructor(baseUrl = "http://votre-api:8000") {
        // ...
    }
}
```

### Personnalisation

-   **Couleurs** : Modifiez les variables CSS dans `static/css/style.css`
-   **Layout** : Ajustez les grilles et flexbox
-   **Fonctionnalités** : Étendez les classes JavaScript

## 📱 Responsive Design

### Breakpoints

-   **Mobile** : < 768px
-   **Tablette** : 768px - 1024px
-   **Desktop** : > 1024px

### Adaptations

-   Navigation en menu hamburger sur mobile
-   Grilles adaptatives
-   Modales en plein écran sur mobile
-   Boutons tactiles optimisés

## 🔌 Intégration API

### Endpoints utilisés

-   `GET /health` - Santé de l'API
-   `GET /dashboard/stats` - Statistiques
-   `GET /agents/` - Liste des agents
-   `POST /agents/` - Créer un agent
-   `GET /crews/` - Liste des crews
-   `POST /crews/` - Créer un crew
-   `GET /campaigns/` - Liste des campagnes
-   `POST /campaigns/` - Créer une campagne
-   `POST /campaigns/{id}/execute` - Exécuter une campagne

### Gestion des erreurs

-   Notifications toast pour les erreurs
-   Retry automatique pour les requêtes
-   Fallback gracieux en cas d'échec

## 🧪 Tests

### Test manuel

1. Ouvrir http://localhost:3000
2. Vérifier que l'API est accessible
3. Tester la création d'un agent
4. Tester la création d'un crew
5. Tester la création d'une campagne
6. Tester l'exécution d'une campagne

### Test automatisé

```bash
# Tester l'API
python test_simple.py

# Tester l'interface (à développer)
# python test_ui.py
```

## 🚀 Déploiement

### Production

1. **Minifier** les fichiers CSS/JS
2. **Optimiser** les images
3. **Configurer** un serveur web (Nginx, Apache)
4. **Sécuriser** avec HTTPS
5. **Configurer** CORS pour l'API

### Docker

```dockerfile
FROM nginx:alpine
COPY web/ /usr/share/nginx/html/
EXPOSE 80
```

## 🔧 Développement

### Structure du code

-   **api.js** : Communication avec l'API REST
-   **ui.js** : Gestion de l'interface utilisateur
-   **app.js** : Logique métier et orchestration

### Bonnes pratiques

-   Code modulaire et réutilisable
-   Gestion d'erreurs robuste
-   Performance optimisée
-   Accessibilité (WCAG)

## 📈 Améliorations futures

### Fonctionnalités

-   [ ] Édition d'agents et crews
-   [ ] Historique des campagnes
-   [ ] Export des résultats
-   [ ] Templates de campagnes
-   [ ] Collaboration en temps réel

### Technique

-   [ ] Tests automatisés
-   [ ] PWA (Progressive Web App)
-   [ ] Cache intelligent
-   [ ] Offline support
-   [ ] Internationalisation

## 🐛 Dépannage

### Problèmes courants

**L'interface ne se charge pas**

-   Vérifiez que le serveur web est démarré
-   Vérifiez l'URL dans le navigateur
-   Vérifiez la console du navigateur

**L'API n'est pas accessible**

-   Vérifiez que Docker est démarré
-   Vérifiez les logs : `docker-compose logs app`
-   Vérifiez l'URL de l'API dans `api.js`

**Erreurs CORS**

-   L'API doit autoriser les requêtes depuis l'interface
-   Vérifiez la configuration CORS dans `main.py`

### Logs

```bash
# Logs de l'API
docker-compose logs app

# Logs de PostgreSQL
docker-compose logs postgres

# Console du navigateur
F12 > Console
```

## 📞 Support

-   **Documentation API** : http://localhost:8000/docs
-   **Issues** : Créer une issue sur le repository
-   **Logs** : Vérifier les logs Docker et navigateur

---

**Interface développée avec ❤️ pour CrewAI Marketing**
