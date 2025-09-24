from crewai import Agent
from src.tools import get_tools_for_agent, create_pdf_knowledge_sources
from src.agent_config import AgentConfigManager
from typing import List

def create_agent_from_config(agent_name: str, config_manager: AgentConfigManager, pdf_paths: List[str] = None) -> Agent:
    """Crée un agent CrewAI à partir de sa configuration"""
    config = config_manager.get_agent_config(agent_name)
    if not config:
        raise ValueError(f"Configuration non trouvée pour l'agent: {agent_name}")
    
    # Récupérer les outils configurés
    tools = get_tools_for_agent(agent_name, config.enabled_tools)
    
    # Créer les sources de connaissances PDF si des chemins sont fournis
    knowledge_sources = []
    if pdf_paths:
        knowledge_sources = create_pdf_knowledge_sources(pdf_paths)
    
    return Agent(
        role=config.role,
        goal=config.goal,
        backstory=config.backstory,
        verbose=config.verbose,
        tools=tools,
        knowledge_sources=knowledge_sources,
        max_iter=config.max_iter,
        # Supprimer memory et allow_delegation pour éviter les erreurs d'événements
    )

def create_all_agents(config_manager: AgentConfigManager, pdf_paths: List[str] = None) -> dict:
    """Crée tous les agents à partir de leur configuration"""
    agents = {}
    agent_names = ["meta_manager_agent", "clara_detective_digitale", "julien_analyste_strategique", "sophie_plume_solidaire"]
    
    for agent_name in agent_names:
        agents[agent_name] = create_agent_from_config(agent_name, config_manager, pdf_paths)
    
    return agents

# Fonction de compatibilité pour l'ancien code
def get_legacy_agents():
    """Retourne les agents avec la configuration par défaut (pour compatibilité)"""
    config_manager = AgentConfigManager()
    return create_all_agents(config_manager)

__all__ = [
    "create_agent_from_config",
    "create_all_agents", 
    "get_legacy_agents"
]