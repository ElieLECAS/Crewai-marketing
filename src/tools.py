from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool, PDFSearchTool, RagTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from typing import List, Dict, Any
import os

def get_available_tools() -> Dict[str, Any]:
    """Retourne la liste des outils disponibles avec leurs configurations"""
    tools = {}
    
    # Serper pour recherche web
    if os.getenv("SERPER_API_KEY"):
        tools["serper_search"] = {
            "name": "Recherche Web (Serper)",
            "description": "Recherche d'informations sur le web via Serper",
            "tool": SerperDevTool(),
            "enabled": True
        }
    
    # Recherche sur site web
    tools["website_search"] = {
        "name": "Recherche sur Site Web",
        "description": "Recherche dans le contenu d'un site web spécifique",
        "tool": WebsiteSearchTool(),
        "enabled": True
    }
    
    # Scraping de site web
    tools["scrape_website"] = {
        "name": "Scraping de Site Web",
        "description": "Extraction du contenu d'une page web",
        "tool": ScrapeWebsiteTool(),
        "enabled": True
    }
    
    # Outils PDF et RAG (CrewAI natifs)
    tools["pdf_search"] = {
        "name": "Recherche PDF (CrewAI)",
        "description": "Recherche sémantique dans les fichiers PDF via CrewAI. Les PDFs doivent être dans le dossier knowledge/ ou spécifiés par chemin complet.",
        "tool": PDFSearchTool(),
        "enabled": True
    }
    
    tools["rag_tool"] = {
        "name": "RAG Tool (CrewAI)",
        "description": "Recherche dans base de connaissances via CrewAI. Utilise automatiquement les PDFs disponibles.",
        "tool": RagTool(),
        "enabled": True
    }
    
    return tools

def create_pdf_knowledge_sources(pdf_paths: List[str]) -> List:
    """Crée des sources de connaissances PDF pour les agents"""
    knowledge_sources = []
    
    if not pdf_paths:
        print("Aucun PDF fourni pour les sources de connaissances")
        return knowledge_sources
    
    print(f"📚 Création des sources de connaissances pour {len(pdf_paths)} PDF(s)")
    
    # Pour l'instant, on retourne une liste vide pour éviter les erreurs de compatibilité
    # Les agents utiliseront directement les outils PDFSearchTool et RagTool
    print("💡 Les agents utiliseront les outils PDF natifs de CrewAI (PDFSearchTool, RagTool)")
    print("📄 PDFs disponibles pour les outils :")
    
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            abs_path = os.path.abspath(pdf_path)
            print(f"   ✅ {abs_path}")
        else:
            print(f"   ⚠️ Fichier non trouvé: {pdf_path}")
    
    print("🎯 Les outils PDF sont prêts à être utilisés par les agents")
    return knowledge_sources

def get_tools_for_agent(agent_name: str, enabled_tools: List[str]) -> List[Any]:
    """Retourne les outils activés pour un agent spécifique"""
    available_tools = get_available_tools()
    agent_tools = []
    
    for tool_name in enabled_tools:
        if tool_name in available_tools and available_tools[tool_name]["enabled"]:
            agent_tools.append(available_tools[tool_name]["tool"])
    
    return agent_tools

# Configuration par défaut des outils par agent
DEFAULT_AGENT_TOOLS = {
    "manager_agent": ["serper_search", "rag_tool"],
    "web_research_agent": ["serper_search", "website_search", "scrape_website"],
    "pdf_analysis_agent": ["pdf_search", "rag_tool"],
    "content_writer_agent": ["serper_search", "rag_tool"]
}