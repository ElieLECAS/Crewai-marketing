from crewai import Crew, Process
from .agents import create_all_agents
from .sequential_tasks import create_sequential_tasks_from_problem
from .agent_config import AgentConfigManager
from typing import List, Optional


def build_dynamic_marketing_crew(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, pdf_paths: List[str] = None):
    """Construit l'équipe marketing dynamique basée sur une problématique spécifique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    # Créer les agents avec leur configuration et les PDFs
    agents = create_all_agents(config_manager, pdf_paths)
    
    # Créer les tâches séquentielles avec transmission des résultats
    tasks = create_sequential_tasks_from_problem(problem_statement, company_context, config_manager)

    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        # Supprimer les paramètres memory et planning pour éviter les erreurs d'événements
    )

