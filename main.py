from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uvicorn
from datetime import datetime

from src.database import get_db, init_db
from src.schemas import (
    AgentCreate, AgentUpdate, AgentResponse,
    CrewCreate, CrewUpdate, CrewResponse,
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CampaignExecutionRequest, CampaignExecutionResponse,
    FileUploadResponse, FileListResponse,
    APIResponse, PaginatedResponse, DashboardStats,
    ToolsResponse, ToolInfo
)
from src.services import AgentService, CrewService, CampaignService, FileService
from src.tools import get_available_tools

# Créer l'application FastAPI
app = FastAPI(
    title="CrewAI Marketing API",
    description="API pour la gestion des campagnes marketing avec CrewAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialiser la base de données au démarrage
@app.on_event("startup")
async def startup_event():
    init_db()

# Endpoints pour les agents
@app.post("/agents/", response_model=AgentResponse)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Créer un nouvel agent"""
    try:
        service = AgentService(db)
        agent = service.create_agent(agent_data)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'agent: {str(e)}")

@app.get("/agents/", response_model=List[AgentResponse])
async def get_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer tous les agents"""
    service = AgentService(db)
    return service.get_all_agents(skip=skip, limit=limit)

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Récupérer un agent par ID"""
    service = AgentService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agent

@app.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent_data: AgentUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un agent"""
    try:
        service = AgentService(db)
        agent = service.update_agent(agent_id, agent_data)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        return agent
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.delete("/agents/{agent_id}", response_model=APIResponse)
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Supprimer un agent"""
    try:
        service = AgentService(db)
        success = service.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent non trouvé")
        return APIResponse(success=True, message="Agent supprimé avec succès")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# Endpoints pour les crews
@app.post("/crews/", response_model=CrewResponse)
async def create_crew(crew_data: CrewCreate, db: Session = Depends(get_db)):
    """Créer un nouveau crew"""
    try:
        service = CrewService(db)
        crew = service.create_crew(crew_data)
        return crew
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du crew: {str(e)}")

@app.get("/crews/", response_model=List[CrewResponse])
async def get_crews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer tous les crews"""
    service = CrewService(db)
    return service.get_all_crews(skip=skip, limit=limit)

@app.get("/crews/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: int, db: Session = Depends(get_db)):
    """Récupérer un crew par ID"""
    service = CrewService(db)
    crew = service.get_crew(crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew non trouvé")
    return crew

@app.put("/crews/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: int, crew_data: CrewUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un crew"""
    try:
        service = CrewService(db)
        crew = service.update_crew(crew_id, crew_data)
        if not crew:
            raise HTTPException(status_code=404, detail="Crew non trouvé")
        return crew
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.delete("/crews/{crew_id}", response_model=APIResponse)
async def delete_crew(crew_id: int, db: Session = Depends(get_db)):
    """Supprimer un crew"""
    try:
        service = CrewService(db)
        success = service.delete_crew(crew_id)
        if not success:
            raise HTTPException(status_code=404, detail="Crew non trouvé")
        return APIResponse(success=True, message="Crew supprimé avec succès")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# Endpoints pour les campagnes
@app.post("/campaigns/", response_model=CampaignResponse)
async def create_campaign(campaign_data: CampaignCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle campagne"""
    try:
        service = CampaignService(db)
        campaign = service.create_campaign(campaign_data)
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la campagne: {str(e)}")

@app.get("/campaigns/", response_model=List[CampaignResponse])
async def get_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les campagnes"""
    service = CampaignService(db)
    return service.get_all_campaigns(skip=skip, limit=limit)

@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Récupérer une campagne par ID"""
    service = CampaignService(db)
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campagne non trouvée")
    return campaign

@app.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(campaign_id: int, campaign_data: CampaignUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une campagne"""
    try:
        service = CampaignService(db)
        campaign = service.update_campaign(campaign_id, campaign_data)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@app.delete("/campaigns/{campaign_id}", response_model=APIResponse)
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Supprimer une campagne"""
    try:
        service = CampaignService(db)
        success = service.delete_campaign(campaign_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        return APIResponse(success=True, message="Campagne supprimée avec succès")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# Endpoint pour exécuter une campagne
@app.post("/campaigns/{campaign_id}/execute", response_model=CampaignExecutionResponse)
async def execute_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    openai_api_key: str = Form(...),
    serper_api_key: Optional[str] = Form(None),
    openai_model: str = Form("gpt-4o-mini"),
    db: Session = Depends(get_db)
):
    """Exécuter une campagne marketing"""
    try:
        service = CampaignService(db)
        result = service.execute_campaign(
            campaign_id=campaign_id,
            openai_api_key=openai_api_key,
            serper_api_key=serper_api_key,
            openai_model=openai_model
        )
        
        return CampaignExecutionResponse(
            campaign_id=campaign_id,
            status=result["status"],
            message="Campagne exécutée avec succès" if result["success"] else "Erreur lors de l'exécution",
            result=result.get("result")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution: {str(e)}")

# Endpoints pour les fichiers
@app.post("/campaigns/{campaign_id}/files", response_model=FileUploadResponse)
async def upload_file(
    campaign_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploader un fichier pour une campagne"""
    try:
        # Vérifier que la campagne existe
        campaign_service = CampaignService(db)
        campaign = campaign_service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campagne non trouvée")
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Uploader le fichier
        file_service = FileService(db)
        campaign_file = file_service.upload_file(campaign_id, file_content, file.filename)
        
        return FileUploadResponse(
            filename=campaign_file.filename,
            file_path=campaign_file.file_path,
            file_size=campaign_file.file_size,
            message="Fichier uploadé avec succès"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

@app.get("/campaigns/{campaign_id}/files", response_model=FileListResponse)
async def get_campaign_files(campaign_id: int, db: Session = Depends(get_db)):
    """Récupérer les fichiers d'une campagne"""
    try:
        file_service = FileService(db)
        files = file_service.get_campaign_files(campaign_id)
        
        return FileListResponse(
            files=files,
            total_count=len(files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

@app.delete("/files/{file_id}", response_model=APIResponse)
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """Supprimer un fichier"""
    try:
        file_service = FileService(db)
        success = file_service.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=404, detail="Fichier non trouvé")
        return APIResponse(success=True, message="Fichier supprimé avec succès")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

# Endpoints utilitaires
@app.get("/tools", response_model=ToolsResponse)
async def get_available_tools_info():
    """Récupérer les outils disponibles"""
    tools = get_available_tools()
    tool_infos = {}
    
    for tool_name, tool_info in tools.items():
        tool_infos[tool_name] = ToolInfo(
            name=tool_info["name"],
            description=tool_info["description"],
            enabled=tool_info["enabled"]
        )
    
    return ToolsResponse(tools=tool_infos)

@app.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Récupérer les statistiques du dashboard"""
    try:
        agent_service = AgentService(db)
        crew_service = CrewService(db)
        campaign_service = CampaignService(db)
        file_service = FileService(db)
        
        # Compter les agents
        total_agents = len(agent_service.get_all_agents())
        
        # Compter les crews
        total_crews = len(crew_service.get_all_crews())
        
        # Compter les campagnes
        all_campaigns = campaign_service.get_all_campaigns()
        total_campaigns = len(all_campaigns)
        completed_campaigns = len([c for c in all_campaigns if c.status == "completed"])
        pending_campaigns = len([c for c in all_campaigns if c.status == "pending"])
        failed_campaigns = len([c for c in all_campaigns if c.status == "failed"])
        
        # Compter les fichiers (approximation)
        total_files = 0
        for campaign in all_campaigns:
            files = file_service.get_campaign_files(campaign.id)
            total_files += len(files)
        
        return DashboardStats(
            total_agents=total_agents,
            total_crews=total_crews,
            total_campaigns=total_campaigns,
            completed_campaigns=completed_campaigns,
            pending_campaigns=pending_campaigns,
            failed_campaigns=failed_campaigns,
            total_files=total_files
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")

# Endpoint de santé
@app.get("/health")
async def health_check():
    """Vérifier la santé de l'API"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Endpoint racine
@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "CrewAI Marketing API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
