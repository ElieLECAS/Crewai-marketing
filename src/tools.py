from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool, PDFSearchTool, RagTool
from typing import List, Dict, Any
import os
from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field

def get_available_pdfs() -> List[str]:
    """Retourne la liste des PDFs disponibles dans le dossier knowledge/"""
    knowledge_dir = "knowledge"
    pdf_files = []
    
    # Utiliser le chemin absolu du dossier knowledge
    knowledge_abs_dir = os.path.abspath(knowledge_dir)
    
    if os.path.exists(knowledge_abs_dir):
        for file in os.listdir(knowledge_abs_dir):
            if file.lower().endswith('.pdf'):
                # Utiliser des chemins absolus pour éviter les problèmes de répertoire de travail
                pdf_files.append(os.path.join(knowledge_abs_dir, file))
    
    return pdf_files


def create_pdf_search_tools(pdf_files: List[str]) -> List[PDFSearchTool]:
    """Crée une liste d'outils PDFSearchTool pour chaque fichier PDF"""
    tools = []
    
    for pdf_path in pdf_files:
        try:
            tool = PDFSearchTool(pdf=pdf_path)
            tools.append(tool)
            print(f"✅ Outil PDF créé pour: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"❌ Erreur création outil pour {os.path.basename(pdf_path)}: {e}")
    
    return tools

def create_smart_pdf_tools():
    """Crée des outils PDF intelligents qui utilisent automatiquement les PDFs disponibles"""
    pdf_files = get_available_pdfs()
    
    if pdf_files:
        # Affichage debug des chemins PDF
        print(f"🔍 Création des outils PDF avec {len(pdf_files)} fichier(s):")
        for pdf_path in pdf_files:
            print(f"   📄 Chemin PDF: {pdf_path}")
            print(f"   📄 Fichier existe: {os.path.exists(pdf_path)}")
        
        # Créer les outils PDF pour chaque fichier
        tools = create_pdf_search_tools(pdf_files)
        print(f"✅ {len(tools)} outil(s) PDF créé(s) avec succès")
        return tools
    else:
        # Retourner une liste vide si aucun PDF n'est disponible
        print("⚠️ Aucun PDF disponible pour créer les outils PDFSearchTool")
        return []


def create_rag_tools(pdf_files: List[str]) -> List[RagTool]:
    """Crée une liste d'outils RagTool pour chaque fichier PDF"""
    tools = []
    
    for pdf_path in pdf_files:
        try:
            tool = RagTool(pdf=pdf_path)
            tools.append(tool)
            print(f"✅ Outil RAG créé pour: {os.path.basename(pdf_path)}")
        except Exception as e:
            print(f"❌ Erreur création RAG pour {os.path.basename(pdf_path)}: {e}")
    
    return tools

def create_smart_rag_tools():
    """Crée des outils RAG intelligents qui utilisent automatiquement les PDFs disponibles"""
    pdf_files = get_available_pdfs()
    
    if pdf_files:
        # Affichage debug des chemins PDF
        print(f"🔍 Création des outils RAG avec {len(pdf_files)} fichier(s):")
        for pdf_path in pdf_files:
            print(f"   📄 Chemin PDF: {pdf_path}")
            print(f"   📄 Fichier existe: {os.path.exists(pdf_path)}")
        
        # Créer les outils RAG pour chaque fichier
        tools = create_rag_tools(pdf_files)
        print(f"✅ {len(tools)} outil(s) RAG créé(s) avec succès")
        return tools
    else:
        # Retourner une liste vide si aucun PDF n'est disponible
        print("⚠️ Aucun PDF disponible pour créer les outils RagTool")
        return []

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
    
    # Outils PDF intelligents - détectent automatiquement les PDFs disponibles
    pdf_files = get_available_pdfs()
    if pdf_files:
        pdf_tools = create_smart_pdf_tools()
        rag_tools = create_smart_rag_tools()
        
        tools["pdf_search"] = {
            "name": "Recherche PDF (CrewAI)",
            "description": f"Recherche sémantique dans {len(pdf_files)} fichier(s) PDF disponible(s) dans le dossier knowledge/",
            "tools": pdf_tools,
            "enabled": True
        }
        
        tools["rag_tool"] = {
            "name": "RAG Tool (CrewAI)",
            "description": f"Recherche dans base de connaissances via CrewAI. Utilise automatiquement {len(pdf_files)} fichier(s) PDF disponible(s).",
            "tools": rag_tools,
            "enabled": True
        }
    else:
        # Désactiver les outils PDF si aucun PDF n'est disponible
        tools["pdf_search"] = {
            "name": "Recherche PDF (CrewAI)",
            "description": "Recherche sémantique dans les fichiers PDF via CrewAI. Aucun PDF disponible actuellement.",
            "tools": [],
            "enabled": False
        }
        
        tools["rag_tool"] = {
            "name": "RAG Tool (CrewAI)",
            "description": "Recherche dans base de connaissances via CrewAI. Aucun PDF disponible actuellement.",
            "tools": [],
            "enabled": False
        }
    
    return tools

def create_pdf_knowledge_sources(pdf_paths: List[str]) -> List:
    """Prépare les PDFs pour les outils CrewAI"""
    from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
    
    knowledge_sources = []
    
    if not pdf_paths:
        print("Aucun PDF fourni pour les sources de connaissances")
        return knowledge_sources
    
    print(f"📚 Préparation des PDFs pour les outils CrewAI ({len(pdf_paths)} fichier(s))")
    
    # Créer le dossier knowledge s'il n'existe pas (avec chemin absolu)
    knowledge_dir = os.path.abspath("knowledge")
    if not os.path.exists(knowledge_dir):
        os.makedirs(knowledge_dir)
        print(f"📁 Dossier {knowledge_dir} créé")
    
    # Copier les PDFs dans le dossier knowledge et créer les sources de connaissances
    for pdf_path in pdf_paths:
        # Convertir le chemin en absolu si nécessaire
        abs_pdf_path = os.path.abspath(pdf_path)
        
        if os.path.exists(abs_pdf_path):
            import shutil
            filename = os.path.basename(abs_pdf_path)
            dest_path = os.path.join(knowledge_dir, filename)
            
            # Vérifier si le fichier est déjà dans le dossier knowledge
            if os.path.abspath(abs_pdf_path) == os.path.abspath(dest_path):
                print(f"   ✅ PDF déjà dans knowledge/: {filename}")
                source_path = dest_path
            else:
                # Copier le fichier dans le dossier knowledge
                try:
                    shutil.copy2(abs_pdf_path, dest_path)
                    print(f"   ✅ PDF copié: {filename}")
                    source_path = dest_path
                except Exception as e:
                    print(f"   ❌ Erreur lors de la copie de {filename}: {e}")
                    continue
            
            # Créer une source de connaissance pour ce PDF avec le chemin absolu
            try:
                # Essayer différentes méthodes de construction
                pdf_source = PDFKnowledgeSource(file_path=os.path.abspath(source_path))
                knowledge_sources.append(pdf_source)
                print(f"   📖 Source de connaissance créée pour: {filename}")
            except Exception as e:
                print(f"   ⚠️ Erreur avec file_path, essai avec file_paths: {e}")
                try:
                    # Essayer avec file_paths (au pluriel)
                    pdf_source = PDFKnowledgeSource(file_paths=[os.path.abspath(source_path)])
                    knowledge_sources.append(pdf_source)
                    print(f"   📖 Source de connaissance créée pour: {filename} (avec file_paths)")
                except Exception as e2:
                    print(f"   ⚠️ Erreur avec file_paths, essai avec constructeur par défaut: {e2}")
                    try:
                        # Essayer avec le constructeur par défaut
                        pdf_source = PDFKnowledgeSource(os.path.abspath(source_path))
                        knowledge_sources.append(pdf_source)
                        print(f"   📖 Source de connaissance créée pour: {filename} (constructeur par défaut)")
                    except Exception as e3:
                        print(f"   ❌ Toutes les méthodes ont échoué pour {filename}: {e3}")
                    
        else:
            print(f"   ⚠️ Fichier non trouvé: {abs_pdf_path}")
    
    print(f"💡 {len(knowledge_sources)} source(s) de connaissance PDF créée(s)")
    print("🎯 Les PDFs sont prêts dans le dossier knowledge/")
    return knowledge_sources

def get_tools_for_agent(agent_name: str, enabled_tools: List[str]) -> List[Any]:
    """Retourne les outils activés pour un agent spécifique"""
    available_tools = get_available_tools()
    agent_tools = []
    
    # Vérifier si des PDFs sont disponibles
    pdf_files = get_available_pdfs()
    has_pdfs = len(pdf_files) > 0
    
    for tool_name in enabled_tools:
        if tool_name in available_tools and available_tools[tool_name]["enabled"]:
            tool_config = available_tools[tool_name]
            
            # Gestion intelligente des outils PDF
            if tool_name in ["pdf_search", "rag_tool"]:
                tools_list = tool_config.get("tools", [])
                if has_pdfs and tools_list:
                    agent_tools.extend(tools_list)
                    print(f"✅ Agent {agent_name}: {len(tools_list)} outil(s) {tool_name} activé(s) avec {len(pdf_files)} PDF(s)")
                    # Affichage debug des chemins PDF utilisés
                    for pdf_path in pdf_files:
                        print(f"   📄 PDF: {pdf_path}")
                else:
                    print(f"⚠️ Agent {agent_name}: Outil {tool_name} désactivé (aucun PDF disponible)")
            else:
                # Pour les autres outils, ajouter normalement
                tool = tool_config.get("tool")
                if tool is not None:
                    agent_tools.append(tool)
    
    return agent_tools

# Configuration par défaut des outils par agent
DEFAULT_AGENT_TOOLS = {
    "meta_manager_agent": ["serper_search", "rag_tool"],
    "clara_detective_digitale": ["serper_search", "website_search", "scrape_website"],
    "julien_analyste_strategique": ["pdf_search", "rag_tool"],
    "sophie_plume_solidaire": ["serper_search", "rag_tool"]
}