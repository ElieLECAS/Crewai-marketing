from typing import Dict, List, Optional
from dataclasses import dataclass
from src.tools import get_available_tools, DEFAULT_AGENT_TOOLS

@dataclass
class AgentConfig:
    """Configuration d'un agent"""
    name: str
    role: str
    goal: str
    backstory: str
    verbose: bool = True
    enabled_tools: List[str] = None
    max_iter: int = 3
    memory: bool = False  # Désactivé pour éviter les problèmes d'événements
    allow_delegation: bool = False

class AgentConfigManager:
    """Gestionnaire de configuration des agents"""
    
    def __init__(self):
        self.agents_config: Dict[str, AgentConfig] = {}
        self.available_tools = get_available_tools()
        self._init_default_configs()
    
    def _init_default_configs(self):
        """Initialise les configurations par défaut"""
        default_configs = {
            "meta_manager_agent": AgentConfig(
                name="meta agent manager",
                role="Meta Agent Manager",
                goal="Analyser les problématiques marketing, comprendre les besoins spécifiques et créer des tâches dynamiques adaptées pour déléguer aux agents spécialisés.",
                backstory="Manager stratégique avec une vision globale du marketing digital. Expert en analyse de problématiques complexes et en orchestration d'équipes spécialisées. Capable de décomposer une problématique en tâches concrètes et de les déléguer aux bons experts.",
                enabled_tools=["serper_search", "pdf_search", "rag_tool"],
                allow_delegation=True
            ),
            "clara_detective_digitale": AgentConfig(
                name="chercheuse web",
                role="Chercheuse Web",
                goal="Identifier les meilleures idées, repérer les hashtags tendance et collecter des exemples concrets d'actions menées par d'autres entreprises.",
                backstory="Clara est passionnée par la veille digitale. Depuis ses débuts dans une agence de communication, elle a développé une expertise pour trouver les tendances et bonnes pratiques en ligne. On l'appelle 'l'œil du web' car rien ne lui échappe : actualités, hashtags, campagnes inspirantes.",
                enabled_tools=["serper_search", "website_search", "scrape_website", "pdf_search", "rag_tool"]
            ),
            "julien_analyste_strategique": AgentConfig(
                name="analyste de contexte",
                role="Analyste de Contexte",
                goal="Filtrer les informations collectées et les contextualiser pour l'entreprise spécifique, en identifiant le ton juste et les actions crédibles.",
                backstory="Julien a travaillé plusieurs années en tant que consultant en RSE (Responsabilité Sociétale des Entreprises). Il adore donner du sens aux données brutes et les adapter au contexte spécifique d'une organisation. Avec un regard humain et pragmatique, il sait traduire une tendance générale en action réaliste et pertinente pour une entreprise donnée.",
                enabled_tools=["serper_search", "pdf_search", "rag_tool"]
            ),
            "sophie_plume_solidaire": AgentConfig(
                name="rédactrice linkedin",
                role="Rédactrice LinkedIn",
                goal="Rédiger du contenu engageant, fidèle aux valeurs de l'entreprise, et aligné avec la stratégie marketing définie.",
                backstory="Sophie est une communicante née. Ancienne journaliste spécialisée dans la communication interne, elle a une sensibilité particulière pour les sujets humains et solidaires. Sa plume est à la fois professionnelle et chaleureuse, capable d'émouvoir tout en valorisant l'entreprise.",
                enabled_tools=["serper_search", "pdf_search", "rag_tool"]
            )
        }
        
        self.agents_config = default_configs
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """Récupère la configuration d'un agent"""
        return self.agents_config.get(agent_name)
    
    def update_agent_config(self, agent_name: str, config: AgentConfig):
        """Met à jour la configuration d'un agent"""
        self.agents_config[agent_name] = config
    
    def get_all_agents(self) -> Dict[str, AgentConfig]:
        """Retourne toutes les configurations d'agents"""
        return self.agents_config
    
    def get_available_tools(self) -> Dict[str, Dict]:
        """Retourne les outils disponibles"""
        return self.available_tools
    
    def update_agent_tools(self, agent_name: str, enabled_tools: List[str]):
        """Met à jour les outils d'un agent"""
        if agent_name in self.agents_config:
            self.agents_config[agent_name].enabled_tools = enabled_tools
    
    def export_config(self) -> Dict:
        """Exporte la configuration complète"""
        return {
            "agents": {
                name: {
                    "role": config.role,
                    "goal": config.goal,
                    "backstory": config.backstory,
                    "verbose": config.verbose,
                    "enabled_tools": config.enabled_tools,
                    "max_iter": config.max_iter,
                    "memory": config.memory,
                    "allow_delegation": config.allow_delegation
                }
                for name, config in self.agents_config.items()
            },
            "tools": {
                name: {
                    "description": tool_info["description"],
                    "enabled": tool_info["enabled"]
                }
                for name, tool_info in self.available_tools.items()
            }
        }
    
    def import_config(self, config: Dict):
        """Importe une configuration"""
        if "agents" in config:
            for agent_name, agent_data in config["agents"].items():
                if agent_name in self.agents_config:
                    self.agents_config[agent_name].role = agent_data.get("role", self.agents_config[agent_name].role)
                    self.agents_config[agent_name].goal = agent_data.get("goal", self.agents_config[agent_name].goal)
                    self.agents_config[agent_name].backstory = agent_data.get("backstory", self.agents_config[agent_name].backstory)
                    self.agents_config[agent_name].verbose = agent_data.get("verbose", self.agents_config[agent_name].verbose)
                    self.agents_config[agent_name].enabled_tools = agent_data.get("enabled_tools", self.agents_config[agent_name].enabled_tools)
                    self.agents_config[agent_name].max_iter = agent_data.get("max_iter", self.agents_config[agent_name].max_iter)
                    self.agents_config[agent_name].memory = agent_data.get("memory", self.agents_config[agent_name].memory)
                    self.agents_config[agent_name].allow_delegation = agent_data.get("allow_delegation", self.agents_config[agent_name].allow_delegation)