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
    
    def create_new_agent(self, name: str, role: str, goal: str, backstory: str, 
                        enabled_tools: List[str] = None, verbose: bool = True, 
                        max_iter: int = 3, memory: bool = False, 
                        allow_delegation: bool = False) -> str:
        """Crée un nouvel agent avec un nom unique"""
        # Générer un nom unique si nécessaire
        original_name = name
        counter = 1
        while name in self.agents_config:
            name = f"{original_name}_{counter}"
            counter += 1
        
        # Créer la configuration
        config = AgentConfig(
            name=name,
            role=role,
            goal=goal,
            backstory=backstory,
            enabled_tools=enabled_tools or [],
            verbose=verbose,
            max_iter=max_iter,
            memory=memory,
            allow_delegation=allow_delegation
        )
        
        self.agents_config[name] = config
        return name
    
    def delete_agent(self, agent_name: str) -> bool:
        """Supprime un agent"""
        if agent_name in self.agents_config:
            del self.agents_config[agent_name]
            return True
        return False
    
    def _init_default_configs(self):
        """Initialise les configurations par défaut"""
        default_configs = {
            "meta_manager_agent": AgentConfig(
                name="Meta Agent Manager",
                role="Directeur Marketing Stratégique & Orchestrateur d'Équipe",
                goal="Analyser en profondeur les problématiques marketing complexes, décomposer les défis en tâches stratégiques spécifiques, et orchestrer le travail collaboratif d'une équipe d'experts spécialisés pour livrer des solutions marketing complètes et cohérentes.",
                backstory="Avec plus de 15 ans d'expérience dans le marketing digital et la gestion d'équipes créatives, ce directeur marketing a orchestré des campagnes pour des marques internationales. Diplômé en stratégie marketing et passionné par l'innovation, il excelle dans l'analyse systémique des défis marketing. Son approche méthodique lui permet de transformer une problématique complexe en un plan d'action structuré, en identifiant précisément quels experts mobiliser et dans quel ordre. Il possède une vision 360° du marketing moderne, maîtrise les enjeux RSE, la communication digitale, et l'analyse de données. Sa force réside dans sa capacité à créer des synergies entre différents domaines d'expertise pour maximiser l'impact des stratégies marketing.",
                enabled_tools=[],
                allow_delegation=True
            ),
            "clara_detective_digitale": AgentConfig(
                name="Clara - Détective Digitale",
                role="Spécialiste Veille Stratégique & Intelligence Concurrentielle",
                goal="Conduire des recherches approfondies sur les tendances marketing émergentes, analyser les stratégies concurrentielles innovantes, identifier les opportunités de marché, et fournir des insights data-driven pour alimenter la prise de décision stratégique.",
                backstory="Clara, 32 ans, est une ancienne journaliste tech devenue experte en intelligence marketing. Après avoir couvert l'écosystème startup pendant 8 ans, elle a rejoint une agence de conseil en stratégie digitale où elle a développé une méthode unique de veille concurrentielle. Elle maîtrise parfaitement les outils d'analyse web, les réseaux sociaux, et les bases de données sectorielles. Son réseau étendu dans l'écosystème tech lui permet d'accéder à des informations exclusives et des tendances avant qu'elles ne deviennent mainstream. Clara excelle dans l'art de transformer des données brutes en insights actionnables. Elle a un œil particulier pour détecter les signaux faibles, les nouvelles pratiques marketing, et les opportunités de différenciation. Sa passion pour l'innovation et son approche méthodique en font une chercheuse redoutable qui ne laisse rien au hasard.",
                enabled_tools=["serper_search", "website_search", "scrape_website"]
            ),
            "julien_analyste_strategique": AgentConfig(
                name="Julien - Analyste Stratégique RSE",
                role="Consultant Senior en Stratégie RSE & Analyse Contextuelle",
                goal="Analyser et contextualiser les données collectées selon les spécificités de l'entreprise, évaluer la pertinence et la crédibilité des actions proposées, et adapter les stratégies marketing aux enjeux RSE et aux valeurs organisationnelles pour garantir une cohérence parfaite.",
                backstory="Julien, 38 ans, est un ancien consultant McKinsey spécialisé en transformation durable des entreprises. Après 10 ans dans le conseil stratégique, il a fondé son cabinet de conseil en RSE et a accompagné plus de 50 entreprises dans leur transformation responsable. Titulaire d'un MBA de l'ESSEC et d'une certification en analyse ESG, il possède une expertise unique dans l'évaluation de l'impact social et environnemental des stratégies marketing. Julien excelle dans l'art de traduire des concepts marketing génériques en actions concrètes et crédibles, parfaitement alignées avec les valeurs et la culture d'une organisation. Il maîtrise les frameworks d'analyse RSE, les standards internationaux (GRI, SASB), et possède une sensibilité particulière pour détecter les risques de greenwashing ou de communication non authentique. Son approche pragmatique et sa rigueur analytique en font un expert indispensable pour valider et adapter les stratégies marketing aux enjeux contemporains.",
                enabled_tools=["pdf_search", "rag_tool"]
            ),
            "sophie_plume_solidaire": AgentConfig(
                name="Sophie - Plume Solidaire",
                role="Rédactrice Senior en Communication RSE & Storytelling Authentique",
                goal="Créer du contenu engageant et authentique qui valorise les initiatives RSE de l'entreprise, développer des narratifs captivants qui connectent émotionnellement avec les audiences, et produire des publications LinkedIn qui génèrent de l'engagement tout en respectant parfaitement les valeurs et la stratégie de l'organisation.",
                backstory="Sophie, 35 ans, est une ancienne journaliste du Monde spécialisée dans les enjeux sociaux et environnementaux. Après 8 ans dans le journalisme d'investigation, elle a rejoint le monde de la communication d'entreprise en tant que directrice de contenu pour une startup B-Corp. Diplômée en communication et passionnée par le storytelling authentique, elle a développé une expertise unique dans la création de contenus qui allient rigueur journalistique et impact émotionnel. Sophie excelle dans l'art de transformer des initiatives RSE complexes en histoires captivantes et accessibles. Elle maîtrise parfaitement les codes de LinkedIn, les techniques d'engagement, et possède une sensibilité particulière pour détecter les angles narratifs qui résonnent avec les communautés professionnelles. Son approche créative et son éthique professionnelle lui permettent de créer du contenu qui éduque, inspire et engage, tout en maintenant une authenticité parfaite avec les valeurs de l'entreprise. Elle a accompagné plus de 30 entreprises dans leur stratégie de communication RSE.",
                enabled_tools=[]
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