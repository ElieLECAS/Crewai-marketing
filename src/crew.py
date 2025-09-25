from crewai import Crew, Process
from .agents import create_all_agents
from .sequential_tasks import create_sequential_tasks_from_problem
from .agent_config import AgentConfigManager
from typing import List, Optional


def build_dynamic_marketing_crew(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None, selected_agents: List[str] = None):
    """Construit l'équipe marketing dynamique basée sur une problématique spécifique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    # Utiliser les agents par défaut si aucun n'est fourni
    if selected_agents is None:
        selected_agents = ["meta_manager_agent", "clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
    
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
        # Supprimer les paramètres memory et planning pour éviter les erreurs d'événements
    )

