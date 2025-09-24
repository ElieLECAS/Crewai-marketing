from crewai import Task
from textwrap import dedent
from typing import Dict, List, Optional
from .agents import create_agent_from_config
from .agent_config import AgentConfigManager


class SequentialTaskManager:
    """Gestionnaire de tâches séquentielles avec transmission des résultats"""
    
    def __init__(self, config_manager: AgentConfigManager):
        self.config_manager = config_manager
    
    def create_meta_manager_task(self, problem_statement: str, company_context: str = "") -> Task:
        """Crée la tâche principale du Meta Agent Manager"""
        meta_agent = create_agent_from_config("meta_manager_agent", self.config_manager)
        
        return Task(
            description=dedent(f"""
            Tu es le Meta Agent Manager. Tu reçois une problématique marketing et tu dois l'analyser pour créer des tâches spécifiques et les déléguer.
            
            PROBLÉMATIQUE REÇUE :
            {problem_statement}
            
            CONTEXTE ENTREPRISE :
            {company_context if company_context else "Aucun contexte spécifique fourni"}
            
            MISSION IMPORTANTE :
            1. **Analyser la problématique** : Comprendre les enjeux, objectifs et contraintes
            2. **Créer des tâches spécifiques** : Générer des tâches concrètes et détaillées pour chaque agent
            3. **Déléguer intelligemment** : Assigner chaque tâche à l'agent le plus approprié
            4. **Structurer pour transmission** : Préparer les informations pour transmission via le système de context
            
            AGENTS DISPONIBLES :
            - **Clara (Détective Digitale)** : Recherche web, veille, hashtags, exemples concrets
            - **Julien (Analyste Stratégique)** : Analyse contextuelle, filtrage, adaptation au secteur
            - **Sophie (Plume Solidaire)** : Rédaction LinkedIn, contenu engageant
            
            FORMAT DE DÉLÉGATION REQUIS :
            Tu dois créer un plan d'action structuré avec :
            
            ## TÂCHE POUR CLARA :
            - **Objectif** : [Objectif précis pour Clara]
            - **Instructions** : [Instructions détaillées]
            - **Livrables** : [Format et contenu attendus]
            - **Justification** : [Pourquoi cette tâche]
            
            ## TÂCHE POUR JULIEN :
            - **Objectif** : [Objectif précis pour Julien]
            - **Instructions** : [Instructions détaillées, basées sur les données de Clara]
            - **Livrables** : [Format et contenu attendus]
            - **Justification** : [Pourquoi cette tâche]
            
            ## TÂCHE POUR SOPHIE :
            - **Objectif** : [Objectif précis pour Sophie]
            - **Instructions** : [Instructions détaillées, basées sur les analyses précédentes]
            - **Livrables** : [Format et contenu attendus]
            - **Justification** : [Pourquoi cette tâche]
            
            LIVRABLE :
            Plan d'action structuré avec les tâches déléguées pour Clara, Julien et Sophie.
            """).strip(),
            agent=meta_agent,
            expected_output="Plan d'action structuré avec les tâches déléguées pour Clara, Julien et Sophie.",
        )
    
    def create_clara_task(self, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche pour Clara qui utilise le context du Meta Manager"""
        clara_agent = create_agent_from_config("clara_detective_digitale", self.config_manager)
        
        return Task(
            description=dedent(f"""
            Tu es Clara, la Détective Digitale.
            
            CONTEXTE :
            Tu vas recevoir via le système de context les instructions du Meta Agent Manager qui a analysé cette problématique :
            {problem_statement}
            
            {f"Contexte entreprise : {company_context}" if company_context else ""}
            
            MISSION :
            1. **Récupère ta tâche** : Dans le context, trouve la section "## TÂCHE POUR CLARA"
            2. **Exécute précisément** : Accomplis exactement l'objectif défini avec les instructions données
            3. **Utilise tes outils** : Emploie serper_search, website_search, scrape_website selon tes besoins
            4. **Respecte le format** : Livre le résultat selon le format demandé
            
            IMPORTANT : Exécute uniquement ce qui t'est demandé dans ta section du context, ni plus ni moins.
            
            LIVRABLE :
            Résultat conforme aux spécifications reçues via le context du Meta Manager.
            """).strip(),
            agent=clara_agent,
            expected_output="Résultat conforme aux spécifications reçues via le context du Meta Manager.",
        )
    
    def create_julien_task(self, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche pour Julien qui utilise le context du Meta Manager et les résultats de Clara"""
        julien_agent = create_agent_from_config("julien_analyste_strategique", self.config_manager)
        
        return Task(
            description=dedent(f"""
            Tu es Julien, l'Analyste Stratégique.
            
            CONTEXTE :
            Tu vas recevoir via le système de context :
            1. **Instructions du Meta Manager** : Section "## TÂCHE POUR JULIEN" avec tes objectifs
            2. **Données de Clara** : Les résultats de ses recherches pour cette problématique : {problem_statement}
            
            {f"Contexte entreprise : {company_context}" if company_context else ""}
            
            MISSION :
            1. **Récupère ta tâche** : Dans le context, trouve la section "## TÂCHE POUR JULIEN"
            2. **Analyse les données de Clara** : Utilise ses résultats comme base de travail
            3. **Exécute ton analyse** : Accomplis précisément l'objectif défini
            4. **Respecte le format** : Livre le résultat selon le format demandé
            
            IMPORTANT : Combine les données de Clara avec ta propre analyse selon les instructions du Meta Manager.
            
            LIVRABLE :
            Résultat d'analyse conforme aux spécifications reçues via le context, enrichi des données de Clara.
            """).strip(),
            agent=julien_agent,
            expected_output="Résultat d'analyse conforme aux spécifications reçues via le context, enrichi des données de Clara.",
        )
    
    def create_sophie_task(self, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche pour Sophie qui utilise le context de tous les agents précédents"""
        sophie_agent = create_agent_from_config("sophie_plume_solidaire", self.config_manager)
        
        return Task(
            description=dedent(f"""
            Tu es Sophie, la Plume Solidaire.
            
            CONTEXTE :
            Tu vas recevoir via le système de context :
            1. **Instructions du Meta Manager** : Section "## TÂCHE POUR SOPHIE" avec tes objectifs
            2. **Données de Clara** : Les recherches et informations qu'elle a collectées
            3. **Analyse de Julien** : Son analyse stratégique et contextualisée
            
            Tout ceci pour cette problématique : {problem_statement}
            {f"Contexte entreprise : {company_context}" if company_context else ""}
            
            MISSION :
            1. **Récupère ta tâche** : Dans le context, trouve la section "## TÂCHE POUR SOPHIE"
            2. **Synthétise les inputs** : Utilise les données de Clara et l'analyse de Julien
            3. **Exécute ta rédaction** : Accomplis précisément l'objectif défini
            4. **Respecte le format** : Livre le résultat selon le format demandé
            
            IMPORTANT : Crée un contenu final qui combine intelligemment tous les éléments transmis via le context.
            
            LIVRABLE :
            Contenu final conforme aux spécifications reçues via le context, synthétisant le travail de toute l'équipe.
            """).strip(),
            agent=sophie_agent,
            expected_output="Contenu final conforme aux spécifications reçues via le context, synthétisant le travail de toute l'équipe.",
        )
    
    def create_sequential_tasks(self, problem_statement: str, company_context: str = "") -> List[Task]:
        """Crée un ensemble de tâches séquentielles avec transmission des résultats via le système de context"""
        tasks = []
        
        # Tâche 1: Meta Manager - Analyse et délégation
        meta_task = self.create_meta_manager_task(problem_statement, company_context)
        tasks.append(meta_task)
        
        # Tâche 2: Clara - Reçoit le context du Meta Manager
        clara_task = self.create_clara_task(problem_statement, company_context)
        clara_task.context = [meta_task]  # Clara reçoit le résultat du Meta Manager
        tasks.append(clara_task)
        
        # Tâche 3: Julien - Reçoit le context du Meta Manager ET de Clara
        julien_task = self.create_julien_task(problem_statement, company_context)
        julien_task.context = [meta_task, clara_task]  # Julien reçoit les résultats du Meta Manager et de Clara
        tasks.append(julien_task)
        
        # Tâche 4: Sophie - Reçoit le context de TOUS les agents précédents
        sophie_task = self.create_sophie_task(problem_statement, company_context)
        sophie_task.context = [meta_task, clara_task, julien_task]  # Sophie reçoit tous les résultats précédents
        tasks.append(sophie_task)
        
        return tasks


def create_sequential_tasks_from_problem(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None) -> List[Task]:
    """Fonction utilitaire pour créer des tâches séquentielles à partir d'une problématique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    task_manager = SequentialTaskManager(config_manager)
    return task_manager.create_sequential_tasks(problem_statement, company_context)
