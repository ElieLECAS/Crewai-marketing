from crewai import Task
from textwrap import dedent
from typing import Dict, List, Optional
from .agents import create_agent_from_config
from .agent_config import AgentConfigManager


class SequentialTaskManager:
    """Gestionnaire de tâches séquentielles avec transmission des résultats"""
    
    def __init__(self, config_manager: AgentConfigManager):
        self.config_manager = config_manager
    
    def create_meta_manager_task(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None) -> Task:
        """Crée la tâche principale du Meta Agent Manager"""
        meta_agent = create_agent_from_config("meta_manager_agent", self.config_manager)
        
        # Construire la liste des agents disponibles dynamiquement
        if available_agents is None:
            available_agents = ["clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
        
        # Récupérer les informations complètes des agents
        agents_info = []
        for agent_name in available_agents:
            agent_config = self.config_manager.get_agent_config(agent_name)
            if agent_config:
                # Récupérer les outils disponibles
                available_tools = self.config_manager.get_available_tools()
                agent_tools = []
                for tool_name in agent_config.enabled_tools:
                    if tool_name in available_tools:
                        agent_tools.append(available_tools[tool_name]["name"])
                
                tools_text = ", ".join(agent_tools) if agent_tools else "Aucun outil"
                
                agent_info = f"""- **{agent_config.name} ({agent_config.role})**
  - **Objectif** : {agent_config.goal}
  - **Backstory** : {agent_config.backstory}
  - **Outils disponibles** : {tools_text}
  - **Max Iterations** : {agent_config.max_iter}
  - **Verbose** : {'Oui' if agent_config.verbose else 'Non'}"""
                
                agents_info.append(agent_info)
        
        agents_list = "\n\n            ".join(agents_info) if agents_info else "Aucun agent disponible"
        
        return Task(
            description=dedent(f"""
            Tu es le Meta Agent Manager. Tu reçois une problématique marketing et tu dois l'analyser pour créer des tâches spécifiques et les déléguer.
            
            PROBLÉMATIQUE REÇUE :
            {problem_statement}
            
            CONTEXTE ENTREPRISE :
            {company_context if company_context else "Aucun contexte spécifique fourni"}
            
            MISSION IMPORTANTE :
            1. **Analyser la problématique** : Comprendre les enjeux, objectifs et contraintes
            2. **Évaluer les compétences** : Analyser les capacités, outils et spécialisations de chaque agent
            3. **Déterminer l'ordre optimal** : Choisir l'ordre d'exécution selon la logique de la problématique et les compétences
            4. **Créer des tâches spécifiques** : Générer des tâches concrètes adaptées aux capacités de chaque agent
            5. **Déléguer intelligemment** : Assigner chaque tâche à l'agent le plus compétent avec les bons outils
            6. **Structurer pour transmission** : Préparer les informations pour transmission via le système de context
            
            AGENTS DISPONIBLES DANS TON CREW :
            {agents_list}
            
            FORMAT DE DÉLÉGATION REQUIS :
            Tu dois créer un plan d'action structuré avec :
            
            ## ORDRE D'EXÉCUTION RECOMMANDÉ :
            [Liste les agents dans l'ordre optimal d'exécution avec justification basée sur :
            - Les compétences spécifiques de chaque agent
            - Les outils disponibles pour chaque agent
            - La logique de la problématique
            - Les dépendances entre les tâches]
            
            ## TÂCHES PAR AGENT (dans l'ordre recommandé) :
            [Pour chaque agent, crée une section avec :]
            - **Agent assigné** : [Nom et rôle de l'agent]
            - **Compétences utilisées** : [Quelles compétences spécifiques de l'agent seront utilisées]
            - **Outils recommandés** : [Quels outils l'agent devrait utiliser]
            - **Objectif** : [Objectif précis pour cet agent]
            - **Instructions** : [Instructions détaillées adaptées aux capacités de l'agent]
            - **Livrables** : [Format et contenu attendus]
            - **Justification** : [Pourquoi cet agent est le plus approprié pour cette tâche]
            - **Dépendances** : [Quels résultats des agents précédents sont nécessaires]
            - **Ordre d'exécution** : [Position dans la séquence et pourquoi]
            
            IMPORTANT : 
            - Chaque agent recevra le contexte de tous les agents précédents
            - Utilise les compétences et outils spécifiques de chaque agent
            - L'ordre que tu recommandes sera respecté
            
            LIVRABLE :
            Plan d'action structuré avec l'ordre d'exécution recommandé et les tâches déléguées pour tous les agents de ton crew.
            """).strip(),
            agent=meta_agent,
            expected_output="Plan d'action structuré avec l'ordre d'exécution choisi et les tâches déléguées pour tous les agents de ton crew.",
        )
    
    def create_agent_task(self, agent_name: str, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche dynamique pour un agent spécifique"""
        agent = create_agent_from_config(agent_name, self.config_manager)
        agent_config = self.config_manager.get_agent_config(agent_name)
        
        if not agent_config:
            raise ValueError(f"Configuration non trouvée pour l'agent: {agent_name}")
        
        return Task(
            description=dedent(f"""
            Tu es {agent_config.name}, {agent_config.role}.
            
            CONTEXTE :
            Tu vas recevoir via le système de context les instructions du Meta Agent Manager qui a analysé cette problématique :
            {problem_statement}
            
            {f"Contexte entreprise : {company_context}" if company_context else ""}
            
            MISSION :
            1. **Récupère ta tâche** : Dans le context, trouve la section "## TÂCHE POUR {agent_config.name.upper()}"
            2. **Comprends l'ordre** : Le Meta Manager a défini un ordre d'exécution optimal - respecte-le
            3. **Utilise les dépendances** : Si des agents ont travaillé avant toi, utilise leurs résultats
            4. **Exécute précisément** : Accomplis exactement l'objectif défini avec les instructions données
            5. **Utilise tes outils** : Emploie tes outils selon tes besoins
            6. **Respecte le format** : Livre le résultat selon le format demandé
            
            IMPORTANT : 
            - Exécute uniquement ce qui t'est demandé dans ta section du context
            - Respecte l'ordre d'exécution défini par le Meta Manager
            - Utilise les résultats des agents précédents si disponibles
            
            LIVRABLE :
            Résultat conforme aux spécifications reçues via le context du Meta Manager.
            """).strip(),
            agent=agent,
            expected_output="Résultat conforme aux spécifications reçues via le context du Meta Manager.",
        )
    
    
    def create_sequential_tasks(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None) -> List[Task]:
        """Crée un ensemble de tâches séquentielles avec transmission des résultats via le système de context"""
        tasks = []
        
        # Utiliser les agents par défaut si aucun n'est fourni
        if available_agents is None:
            available_agents = ["clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
        
        # Tâche 1: Meta Manager - Analyse et délégation (avec choix de l'ordre)
        meta_task = self.create_meta_manager_task(problem_statement, company_context, available_agents)
        tasks.append(meta_task)
        
        # Tâches pour chaque agent du crew dans l'ordre choisi par le Meta Manager
        # Le Meta Manager décidera de l'ordre optimal dans sa tâche
        previous_tasks = [meta_task]  # Tous les agents reçoivent le contexte du Meta Manager
        
        for agent_name in available_agents:
            # Vérifier que l'agent existe
            if self.config_manager.get_agent_config(agent_name):
                agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                agent_task.context = previous_tasks.copy()  # L'agent reçoit le contexte de tous les agents précédents
                tasks.append(agent_task)
                previous_tasks.append(agent_task)  # Ajouter cette tâche au contexte pour les suivantes
        
        return tasks


def create_sequential_tasks_from_problem(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, available_agents: List[str] = None) -> List[Task]:
    """Fonction utilitaire pour créer des tâches séquentielles à partir d'une problématique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    task_manager = SequentialTaskManager(config_manager)
    return task_manager.create_sequential_tasks(problem_statement, company_context, available_agents)

