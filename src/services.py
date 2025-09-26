from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import shutil
import uuid
from pathlib import Path

from .database import Agent, Crew, CrewAgent, Campaign, CampaignFile, AgentOutput
from .schemas import (
    AgentCreate, AgentUpdate, CrewCreate, CrewUpdate, 
    CampaignCreate, CampaignUpdate, CampaignStatus
)
from .agent_config import AgentConfigManager
from .crew_config import CrewConfigManager
from .crew import build_two_phase_marketing_crew, build_ordered_crew_from_meta_result

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.config_manager = AgentConfigManager()
    
    def create_agent(self, agent_data: AgentCreate) -> Agent:
        """Créer un nouvel agent"""
        # Vérifier si l'agent existe déjà
        existing_agent = self.db.query(Agent).filter(Agent.name == agent_data.name).first()
        if existing_agent:
            raise ValueError(f"Un agent avec le nom '{agent_data.name}' existe déjà")
        
        # Créer l'agent en base
        db_agent = Agent(**agent_data.dict())
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        
        # Créer la configuration dans le config manager
        self.config_manager.create_new_agent(
            name=agent_data.name,
            role=agent_data.role,
            goal=agent_data.goal,
            backstory=agent_data.backstory,
            enabled_tools=agent_data.enabled_tools,
            max_iter=agent_data.max_iter,
            verbose=agent_data.verbose
        )
        
        return db_agent
    
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Récupérer un agent par ID"""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Récupérer un agent par nom"""
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def get_all_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Récupérer tous les agents avec pagination"""
        return self.db.query(Agent).offset(skip).limit(limit).all()
    
    def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Optional[Agent]:
        """Mettre à jour un agent"""
        db_agent = self.get_agent(agent_id)
        if not db_agent:
            return None
        
        # Mettre à jour les champs fournis
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_agent, field, value)
        
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        
        # Mettre à jour la configuration
        if update_data:
            self.config_manager.update_agent_config(db_agent.name, db_agent)
        
        return db_agent
    
    def delete_agent(self, agent_id: int) -> bool:
        """Supprimer un agent"""
        db_agent = self.get_agent(agent_id)
        if not db_agent:
            return False
        
        # Vérifier si l'agent est utilisé dans des crews
        crew_usage = self.db.query(CrewAgent).filter(CrewAgent.agent_id == agent_id).first()
        if crew_usage:
            raise ValueError("Impossible de supprimer un agent utilisé dans des crews")
        
        # Supprimer de la base
        self.db.delete(db_agent)
        self.db.commit()
        
        # Supprimer de la configuration
        self.config_manager.delete_agent(db_agent.name)
        
        return True

class CrewService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_service = AgentService(db)
        self.config_manager = CrewConfigManager(AgentConfigManager())
    
    def create_crew(self, crew_data: CrewCreate) -> Crew:
        """Créer un nouveau crew"""
        # Vérifier si le crew existe déjà
        existing_crew = self.db.query(Crew).filter(Crew.name == crew_data.name).first()
        if existing_crew:
            raise ValueError(f"Un crew avec le nom '{crew_data.name}' existe déjà")
        
        # Vérifier que tous les agents existent
        for agent_name in crew_data.selected_agents:
            agent = self.agent_service.get_agent_by_name(agent_name)
            if not agent:
                raise ValueError(f"Agent '{agent_name}' non trouvé")
        
        # Créer le crew
        crew_dict = crew_data.dict(exclude={'selected_agents'})
        db_crew = Crew(**crew_dict)
        self.db.add(db_crew)
        self.db.flush()  # Pour obtenir l'ID
        
        # Ajouter les agents au crew
        for order, agent_name in enumerate(crew_data.selected_agents):
            agent = self.agent_service.get_agent_by_name(agent_name)
            crew_agent = CrewAgent(
                crew_id=db_crew.id,
                agent_id=agent.id,
                order=order
            )
            self.db.add(crew_agent)
        
        self.db.commit()
        self.db.refresh(db_crew)
        
        # Créer la configuration
        self.config_manager.create_new_crew(
            name=crew_data.name,
            description=crew_data.description,
            selected_agents=crew_data.selected_agents
        )
        
        return db_crew
    
    def get_crew(self, crew_id: int) -> Optional[Crew]:
        """Récupérer un crew par ID"""
        return self.db.query(Crew).filter(Crew.id == crew_id).first()
    
    def get_all_crews(self, skip: int = 0, limit: int = 100) -> List[Crew]:
        """Récupérer tous les crews avec pagination"""
        return self.db.query(Crew).offset(skip).limit(limit).all()
    
    def update_crew(self, crew_id: int, crew_data: CrewUpdate) -> Optional[Crew]:
        """Mettre à jour un crew"""
        db_crew = self.get_crew(crew_id)
        if not db_crew:
            return None
        
        # Mettre à jour les champs fournis
        update_data = crew_data.dict(exclude_unset=True, exclude={'selected_agents'})
        for field, value in update_data.items():
            setattr(db_crew, field, value)
        
        # Mettre à jour les agents si fournis
        if crew_data.selected_agents is not None:
            # Supprimer les anciens agents
            self.db.query(CrewAgent).filter(CrewAgent.crew_id == crew_id).delete()
            
            # Ajouter les nouveaux agents
            for order, agent_name in enumerate(crew_data.selected_agents):
                agent = self.agent_service.get_agent_by_name(agent_name)
                if not agent:
                    raise ValueError(f"Agent '{agent_name}' non trouvé")
                
                crew_agent = CrewAgent(
                    crew_id=crew_id,
                    agent_id=agent.id,
                    order=order
                )
                self.db.add(crew_agent)
        
        db_crew.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_crew)
        
        return db_crew
    
    def delete_crew(self, crew_id: int) -> bool:
        """Supprimer un crew"""
        db_crew = self.get_crew(crew_id)
        if not db_crew:
            return False
        
        # Vérifier si le crew est utilisé dans des campagnes
        campaign_usage = self.db.query(Campaign).filter(Campaign.crew_id == crew_id).first()
        if campaign_usage:
            raise ValueError("Impossible de supprimer un crew utilisé dans des campagnes")
        
        # Supprimer les relations crew_agents
        self.db.query(CrewAgent).filter(CrewAgent.crew_id == crew_id).delete()
        
        # Supprimer le crew
        self.db.delete(db_crew)
        self.db.commit()
        
        return True

class CampaignService:
    def __init__(self, db: Session):
        self.db = db
        self.crew_service = CrewService(db)
        self.agent_service = AgentService(db)
    
    def create_campaign(self, campaign_data: CampaignCreate) -> Campaign:
        """Créer une nouvelle campagne"""
        # Vérifier que le crew existe
        crew = self.crew_service.get_crew(campaign_data.crew_id)
        if not crew:
            raise ValueError("Crew non trouvé")
        
        # Créer la campagne
        db_campaign = Campaign(**campaign_data.dict())
        self.db.add(db_campaign)
        self.db.commit()
        self.db.refresh(db_campaign)
        
        return db_campaign
    
    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Récupérer une campagne par ID"""
        return self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    def get_all_campaigns(self, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """Récupérer toutes les campagnes avec pagination"""
        return self.db.query(Campaign).offset(skip).limit(limit).all()
    
    def update_campaign(self, campaign_id: int, campaign_data: CampaignUpdate) -> Optional[Campaign]:
        """Mettre à jour une campagne"""
        db_campaign = self.get_campaign(campaign_id)
        if not db_campaign:
            return None
        
        # Mettre à jour les champs fournis
        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_campaign, field, value)
        
        self.db.commit()
        self.db.refresh(db_campaign)
        
        return db_campaign
    
    def delete_campaign(self, campaign_id: int) -> bool:
        """Supprimer une campagne"""
        db_campaign = self.get_campaign(campaign_id)
        if not db_campaign:
            return False
        
        # Supprimer les fichiers associés
        self.db.query(CampaignFile).filter(CampaignFile.campaign_id == campaign_id).delete()
        
        # Supprimer les outputs des agents
        self.db.query(AgentOutput).filter(AgentOutput.campaign_id == campaign_id).delete()
        
        # Supprimer la campagne
        self.db.delete(db_campaign)
        self.db.commit()
        
        return True
    
    def execute_campaign(self, campaign_id: int, openai_api_key: str, 
                        serper_api_key: Optional[str] = None, 
                        openai_model: str = "gpt-4o-mini") -> Dict[str, Any]:
        """Exécuter une campagne marketing"""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            raise ValueError("Campagne non trouvée")
        
        if campaign.status == CampaignStatus.RUNNING:
            raise ValueError("La campagne est déjà en cours d'exécution")
        
        # Mettre à jour le statut
        campaign.status = CampaignStatus.RUNNING
        self.db.commit()
        
        try:
            # Configuration des variables d'environnement
            os.environ["OPENAI_API_KEY"] = openai_api_key
            if serper_api_key:
                os.environ["SERPER_API_KEY"] = serper_api_key
            os.environ["OPENAI_MODEL"] = openai_model
            os.environ["CREWAI_TELEMETRY"] = "False"
            
            # Récupérer les fichiers PDF de la campagne
            pdf_files = self.db.query(CampaignFile).filter(
                CampaignFile.campaign_id == campaign_id,
                CampaignFile.file_type == "pdf"
            ).all()
            pdf_paths = [f.file_path for f in pdf_files]
            
            # Récupérer les agents du crew
            crew_agents = self.db.query(CrewAgent).filter(
                CrewAgent.crew_id == campaign.crew_id
            ).order_by(CrewAgent.order).all()
            
            agent_names = []
            for crew_agent in crew_agents:
                agent = self.agent_service.get_agent(crew_agent.agent_id)
                if agent:
                    agent_names.append(agent.name)
            
            # Créer le config manager
            config_manager = AgentConfigManager()
            
            # Phase 1: Meta Manager
            meta_crew, task_manager, available_agents = build_two_phase_marketing_crew(
                problem_statement=campaign.problem_statement,
                company_context=campaign.company_context or "",
                config_manager=config_manager,
                pdf_paths=pdf_paths,
                selected_agents=agent_names
            )
            
            # Exécuter le Meta Manager
            meta_result = meta_crew.kickoff()
            
            # Phase 2: Exécution des agents
            ordered_crew = build_ordered_crew_from_meta_result(
                meta_result=str(meta_result),
                problem_statement=campaign.problem_statement,
                company_context=campaign.company_context or "",
                config_manager=config_manager,
                pdf_paths=pdf_paths,
                available_agents=available_agents
            )
            
            # Exécuter les agents
            agents_result = ordered_crew.kickoff()
            
            # Combiner les résultats
            final_result = f"{meta_result}\n\n---\n\nRÉSULTATS DES AGENTS:\n\n{agents_result}"
            
            # Sauvegarder le résultat
            campaign.result = final_result
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.utcnow()
            
            # Sauvegarder les outputs des agents
            self._save_agent_outputs(campaign_id, final_result)
            
            self.db.commit()
            
            return {
                "success": True,
                "result": final_result,
                "status": CampaignStatus.COMPLETED
            }
            
        except Exception as e:
            # Marquer la campagne comme échouée
            campaign.status = CampaignStatus.FAILED
            campaign.result = f"Erreur: {str(e)}"
            self.db.commit()
            
            return {
                "success": False,
                "error": str(e),
                "status": CampaignStatus.FAILED
            }
    
    def _save_agent_outputs(self, campaign_id: int, result: str):
        """Sauvegarder les outputs des agents"""
        # Parser le résultat pour extraire les outputs par agent
        lines = result.split('\n')
        current_agent = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            # Détecter les sections d'agents
            if any(agent_name in line.lower() for agent_name in ['clara', 'julien', 'sophie', 'meta manager', 'meta agent']):
                # Sauvegarder le contenu précédent
                if current_agent and current_content:
                    self._save_agent_output(campaign_id, current_agent, '\n'.join(current_content))
                
                # Nouvelle section d'agent
                current_agent = line
                current_content = [line]
            elif current_agent and line:
                current_content.append(line)
        
        # Sauvegarder la dernière section
        if current_agent and current_content:
            self._save_agent_output(campaign_id, current_agent, '\n'.join(current_content))
    
    def _save_agent_output(self, campaign_id: int, agent_name: str, content: str):
        """Sauvegarder un output d'agent"""
        agent_output = AgentOutput(
            campaign_id=campaign_id,
            agent_name=agent_name,
            output_content=content,
            output_type="text"
        )
        self.db.add(agent_output)

class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    def upload_file(self, campaign_id: int, file_content: bytes, filename: str) -> CampaignFile:
        """Uploader un fichier pour une campagne"""
        # Générer un nom de fichier unique
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Sauvegarder le fichier
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Créer l'entrée en base
        campaign_file = CampaignFile(
            campaign_id=campaign_id,
            filename=filename,
            file_path=str(file_path),
            file_type=file_extension[1:] if file_extension else "unknown",
            file_size=len(file_content)
        )
        
        self.db.add(campaign_file)
        self.db.commit()
        self.db.refresh(campaign_file)
        
        return campaign_file
    
    def get_campaign_files(self, campaign_id: int) -> List[CampaignFile]:
        """Récupérer les fichiers d'une campagne"""
        return self.db.query(CampaignFile).filter(CampaignFile.campaign_id == campaign_id).all()
    
    def delete_file(self, file_id: int) -> bool:
        """Supprimer un fichier"""
        campaign_file = self.db.query(CampaignFile).filter(CampaignFile.id == file_id).first()
        if not campaign_file:
            return False
        
        # Supprimer le fichier physique
        if os.path.exists(campaign_file.file_path):
            os.remove(campaign_file.file_path)
        
        # Supprimer l'entrée en base
        self.db.delete(campaign_file)
        self.db.commit()
        
        return True
