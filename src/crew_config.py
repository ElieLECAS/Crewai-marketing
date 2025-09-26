from typing import Dict, List, Optional
from dataclasses import dataclass
from .agent_config import AgentConfigManager, AgentConfig

@dataclass
class CrewConfig:
    """Configuration d'un crew"""
    name: str
    description: str
    selected_agents: List[str]  # Noms des agents sélectionnés
    process_type: str = "sequential"  # sequential, hierarchical, etc.
    # Optionnel: tâches préconfigurées (souvent gérées dynamiquement ailleurs)
    tasks: List[str] = None

class CrewConfigManager:
    """Gestionnaire de configuration des crews"""
    
    def __init__(self, agent_config_manager: AgentConfigManager):
        self.agent_config_manager = agent_config_manager
        self.crews_config: Dict[str, CrewConfig] = {}
        self._init_default_crews()
    
    def _init_default_crews(self):
        """Initialise les crews par défaut"""
        # Crew marketing par défaut
        default_marketing_crew = CrewConfig(
            name="Crew Marketing Standard",
            description="Crew marketing avec Meta Manager, Clara, Julien et Sophie. Le Meta Manager analysera automatiquement votre problématique et créera/répartira les tâches aux agents.",
            selected_agents=["meta_manager_agent", "clara_detective_digitale", 
                           "julien_analyste_strategique", "sophie_plume_solidaire"]
        )
        
        self.crews_config["marketing_standard"] = default_marketing_crew
    
    def create_new_crew(self, name: str, description: str, selected_agents: List[str]) -> str:
        """Crée un nouveau crew"""
        # Générer un nom unique si nécessaire
        original_name = name
        counter = 1
        while name in self.crews_config:
            name = f"{original_name}_{counter}"
            counter += 1
        
        crew_config = CrewConfig(
            name=name,
            description=description,
            selected_agents=selected_agents,
            tasks=[]
        )
        
        self.crews_config[name] = crew_config
        return name
    
    def delete_crew(self, crew_name: str) -> bool:
        """Supprime un crew"""
        if crew_name in self.crews_config:
            del self.crews_config[crew_name]
            return True
        return False
    
    def update_crew_config(self, crew_name: str, crew_config: CrewConfig) -> bool:
        """Met à jour la configuration d'un crew"""
        if crew_name in self.crews_config:
            self.crews_config[crew_name] = crew_config
            return True
        return False
    
    
    def get_crew_config(self, crew_name: str) -> Optional[CrewConfig]:
        """Récupère la configuration d'un crew"""
        return self.crews_config.get(crew_name)
    
    def get_all_crews(self) -> Dict[str, CrewConfig]:
        """Retourne toutes les configurations de crews"""
        return self.crews_config
    
    def get_available_agents(self) -> Dict[str, AgentConfig]:
        """Retourne les agents disponibles"""
        return self.agent_config_manager.get_all_agents()
    
    def export_config(self) -> Dict:
        """Exporte la configuration complète des crews"""
        return {
            "crews": {
                name: {
                    "description": crew.description,
                    "selected_agents": crew.selected_agents,
                    "process_type": crew.process_type
                }
                for name, crew in self.crews_config.items()
            }
        }
    
    def import_config(self, config: Dict):
        """Importe une configuration de crews"""
        if "crews" in config:
            for crew_name, crew_data in config["crews"].items():
                crew_config = CrewConfig(
                    name=crew_name,
                    description=crew_data.get("description", ""),
                    selected_agents=crew_data.get("selected_agents", []),
                    process_type=crew_data.get("process_type", "sequential")
                )
                
                self.crews_config[crew_name] = crew_config
