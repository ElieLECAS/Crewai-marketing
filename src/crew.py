from crewai import Crew, Process
from .agents import create_all_agents, create_agent_from_config
from .sequential_tasks import create_sequential_tasks_from_problem, SequentialTaskManager
from .agent_config import AgentConfigManager
from typing import List, Optional


def build_dynamic_marketing_crew(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None, selected_agents: List[str] = None):
    """Construit l'équipe marketing dynamique basée sur une problématique spécifique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    # Si aucun ensemble fourni, utiliser tous les agents disponibles
    if selected_agents is None:
        selected_agents = list(config_manager.get_all_agents().keys())
    
    # Créer les agents sélectionnés avec leur configuration et les PDFs
    agents = {}
    for agent_name in selected_agents:
        try:
            agents[agent_name] = create_agent_from_config(agent_name, config_manager, pdf_paths)
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de l'agent {agent_name}: {e}")
    
    # Créer les tâches séquentielles avec transmission des résultats
    # Exclure le meta_manager_agent des tâches car il est géré séparément
    task_agents = [agent for agent in selected_agents if agent != "meta_manager_agent"]
    tasks = create_sequential_tasks_from_problem(problem_statement, company_context, config_manager, task_agents)

    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

def build_two_phase_marketing_crew(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None, selected_agents: List[str] = None):
    """Construit une équipe marketing en deux phases : Meta Manager puis agents dans l'ordre recommandé"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    # Utiliser les agents par défaut si aucun n'est fourni
    if selected_agents is None:
        selected_agents = ["meta_manager_agent", "clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
    
    # Phase 1: Créer et exécuter le Meta Manager seul
    meta_agent = create_agent_from_config("meta_manager_agent", config_manager, pdf_paths)
    task_manager = SequentialTaskManager(config_manager)
    
    # Agents disponibles pour le Meta Manager (sans lui-même)
    available_agents = [agent for agent in selected_agents if agent != "meta_manager_agent"]
    
    # Créer la tâche du Meta Manager qui génère un plan JSON
    meta_task = task_manager.create_meta_manager_task(problem_statement, company_context, available_agents)
    
    # Créer un crew temporaire pour le Meta Manager
    meta_crew = Crew(
        agents=[meta_agent],
        tasks=[meta_task],
        process=Process.sequential,
        verbose=True,
    )
    
    return meta_crew, task_manager, available_agents

def build_crew_with_json_plan(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None, selected_agents: List[str] = None) -> Crew:
    """Construit un crew où le Meta Manager génère un plan JSON pour créer les vraies Task CrewAI
    
    Args:
        problem_statement: La problématique marketing à résoudre
        company_context: Contexte spécifique de l'entreprise
        config_manager: Gestionnaire de configuration des agents
        pdf_paths: Chemins vers les fichiers PDF à utiliser comme sources de connaissances
        selected_agents: Liste des agents à utiliser (par défaut tous sauf meta_manager)
    
    Returns:
        Crew: Un crew CrewAI avec des tâches générées dynamiquement par le Meta Manager
        
    Example:
        crew = build_crew_with_json_plan(
            problem_statement="Créer une stratégie RSE pour lancer la gamme Lumeal",
            company_context="Entreprise cosmétique française, valeurs éthiques",
            selected_agents=["clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
        )
        result = crew.kickoff()
    """
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    task_manager = SequentialTaskManager(config_manager)
    return task_manager.create_dynamic_crew_with_json_plan(
        problem_statement, company_context, pdf_paths, selected_agents
    )

def build_ordered_crew_from_meta_result(meta_result: str, problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None, available_agents: List[str] = None):
    """Crée un crew avec les agents dans l'ordre recommandé par le Meta Manager"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    if available_agents is None:
        available_agents = ["clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
    
    # Créer le gestionnaire de tâches
    task_manager = SequentialTaskManager(config_manager)
    
    # Créer les tâches dans l'ordre recommandé avec le contexte du Meta Manager
    tasks = task_manager.create_ordered_sequential_tasks(
        problem_statement, 
        company_context, 
        available_agents, 
        meta_result
    )
    
    # Extraire les agents des tâches créées
    agents = [task.agent for task in tasks]
    
    return Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

