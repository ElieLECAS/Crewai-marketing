-- Script d'initialisation de la base de données PostgreSQL
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur PostgreSQL

-- Créer la base de données si elle n'existe pas déjà
-- (PostgreSQL crée automatiquement la base spécifiée dans POSTGRES_DB)

-- Créer un utilisateur avec des privilèges étendus si nécessaire
-- (L'utilisateur par défaut a déjà tous les privilèges)

-- Activer les extensions nécessaires
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Créer un index pour améliorer les performances
-- (Les tables seront créées par SQLAlchemy, mais on peut prévoir des index)

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données crewai_marketing initialisée avec succès';
END $$;
