import os
import streamlit as st
import json
from dotenv import load_dotenv
from rich.console import Console
from src.crew import build_dynamic_marketing_crew
from src.agent_config import AgentConfigManager
from src.tools import get_available_tools

load_dotenv()
console = Console()

st.set_page_config(page_title="CrewAI Marketing", page_icon="📈", layout="wide")

# Initialiser la session state
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = AgentConfigManager()

def display_generated_posts(result):
    """Affiche les posts générés de manière claire et structurée"""
    st.markdown("---")
    st.markdown("## 📱 Posts LinkedIn")
    
    # Section LinkedIn
    st.markdown("### 💼 Posts LinkedIn (10 posts)")
    
    # Créer des colonnes pour afficher les posts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Post LinkedIn 1**")
        st.text_area("Contenu du post LinkedIn 1", value="[Contenu du post LinkedIn 1]", height=100, key="linkedin_1", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 2**")
        st.text_area("Contenu du post LinkedIn 2", value="[Contenu du post LinkedIn 2]", height=100, key="linkedin_2", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 3**")
        st.text_area("Contenu du post LinkedIn 3", value="[Contenu du post LinkedIn 3]", height=100, key="linkedin_3", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 4**")
        st.text_area("Contenu du post LinkedIn 4", value="[Contenu du post LinkedIn 4]", height=100, key="linkedin_4", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 5**")
        st.text_area("Contenu du post LinkedIn 5", value="[Contenu du post LinkedIn 5]", height=100, key="linkedin_5", label_visibility="collapsed")
    
    with col2:
        st.markdown("**Post LinkedIn 6**")
        st.text_area("Contenu du post LinkedIn 6", value="[Contenu du post LinkedIn 6]", height=100, key="linkedin_6", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 7**")
        st.text_area("Contenu du post LinkedIn 7", value="[Contenu du post LinkedIn 7]", height=100, key="linkedin_7", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 8**")
        st.text_area("Contenu du post LinkedIn 8", value="[Contenu du post LinkedIn 8]", height=100, key="linkedin_8", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 9**")
        st.text_area("Contenu du post LinkedIn 9", value="[Contenu du post LinkedIn 9]", height=100, key="linkedin_9", label_visibility="collapsed")
        
        st.markdown("**Post LinkedIn 10**")
        st.text_area("Contenu du post LinkedIn 10", value="[Contenu du post LinkedIn 10]", height=100, key="linkedin_10", label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("## 📸 Posts Instagram")
    
    # Section Instagram
    st.markdown("### 📱 Posts Instagram (10 posts)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Post Instagram 1**")
        st.text_area("Contenu du post Instagram 1", value="[Contenu du post Instagram 1]", height=100, key="instagram_1", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 2**")
        st.text_area("Contenu du post Instagram 2", value="[Contenu du post Instagram 2]", height=100, key="instagram_2", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 3**")
        st.text_area("Contenu du post Instagram 3", value="[Contenu du post Instagram 3]", height=100, key="instagram_3", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 4**")
        st.text_area("Contenu du post Instagram 4", value="[Contenu du post Instagram 4]", height=100, key="instagram_4", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 5**")
        st.text_area("Contenu du post Instagram 5", value="[Contenu du post Instagram 5]", height=100, key="instagram_5", label_visibility="collapsed")
    
    with col2:
        st.markdown("**Post Instagram 6**")
        st.text_area("Contenu du post Instagram 6", value="[Contenu du post Instagram 6]", height=100, key="instagram_6", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 7**")
        st.text_area("Contenu du post Instagram 7", value="[Contenu du post Instagram 7]", height=100, key="instagram_7", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 8**")
        st.text_area("Contenu du post Instagram 8", value="[Contenu du post Instagram 8]", height=100, key="instagram_8", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 9**")
        st.text_area("Contenu du post Instagram 9", value="[Contenu du post Instagram 9]", height=100, key="instagram_9", label_visibility="collapsed")
        
        st.markdown("**Post Instagram 10**")
        st.text_area("Contenu du post Instagram 10", value="[Contenu du post Instagram 10]", height=100, key="instagram_10", label_visibility="collapsed")
    
    # Boutons d'action
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Télécharger tous les posts", type="secondary"):
            st.success("Téléchargement en cours...")
    
    with col2:
        if st.button("📋 Copier dans le presse-papier", type="secondary"):
            st.success("Copié dans le presse-papier !")
    
    with col3:
        if st.button("🔄 Régénérer les posts", type="secondary"):
            st.rerun()

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Campagne", "📄 Documents PDF", "⚙️ Configuration Agents", "🔧 Outils"])

with tab1:
    st.title("🎯 Meta Agent Manager - Marketing Dynamique")
    
    # Information sur la nouvelle architecture
    st.info("""
    **🔄 Nouvelle Architecture Dynamique :**
    
    Le **Meta Agent Manager** analyse votre problématique et crée des tâches adaptées pour :
    
    👩‍💻 **Clara (Détective Digitale)** - Recherche web, veille, hashtags, exemples concrets
    📊 **Julien (Analyste Stratégique)** - Analyse contextuelle, filtrage, adaptation au secteur  
    ✍️ **Sophie (Plume Solidaire)** - Rédaction LinkedIn, contenu engageant
    
    Plus de tâches prédéfinies ! Chaque problématique génère ses propres tâches personnalisées.
    """)
    
    with st.sidebar:
        st.header("🔑 Configuration API")
        openai_key = st.text_input("OPENAI_API_KEY", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        serper_key = st.text_input("SERPER_API_KEY", type="password", value=os.getenv("SERPER_API_KEY", ""))
        model = st.text_input("OPENAI_MODEL", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        st.caption("Ces valeurs peuvent aussi venir de .env")
    
    # Interface pour la problématique marketing
    st.markdown("### 🎯 Votre problématique marketing")
    
    problem_statement = st.text_area(
        "Décrivez votre problématique marketing :",
        placeholder="Exemple: Nous voulons lancer une campagne Octobre Rose pour notre entreprise de menuiserie PROFERM. Nous souhaitons sensibiliser nos clients et prospects au dépistage du cancer du sein tout en valorisant notre engagement social et nos valeurs humaines.",
        height=120,
        help="Décrivez votre problématique, vos objectifs et le contexte de votre campagne"
    )
    
    company_context = st.text_area(
        "Contexte de votre entreprise (optionnel) :",
        placeholder="Exemple: PROFERM - Menuiserie artisanale spécialisée dans les portes et fenêtres sur mesure. Valeurs: proximité, qualité, engagement social. Clientèle: particuliers et professionnels. Zone géographique: région parisienne.",
        height=80,
        help="Informations sur votre entreprise, secteur, valeurs, clientèle..."
    )
    
    # Affichage des PDFs disponibles
    pdf_paths = st.session_state.get('uploaded_pdfs', [])
    if pdf_paths:
        st.success(f"✅ {len(pdf_paths)} PDF(s) disponible(s) pour enrichir les posts")
    else:
        st.info("💡 Uploadez vos PDFs dans l'onglet 'Documents PDF' pour des posts plus précis")
    
    # Bouton de génération
    run_disabled = not problem_statement.strip()
    
    if st.button("🚀 Analyser ma problématique et générer du contenu", type="primary", disabled=run_disabled):
        if not openai_key:
            st.error("❌ OPENAI_API_KEY manquant. Renseignez la clé dans la sidebar.")
        else:
            # Configuration des variables d'environnement
            os.environ["OPENAI_API_KEY"] = openai_key
            if serper_key:
                os.environ["SERPER_API_KEY"] = serper_key
            if model:
                os.environ["OPENAI_MODEL"] = model
            
            with st.spinner("🤖 Le Meta Agent Manager analyse votre problématique et coordonne l'équipe..."):
                # Construire l'équipe dynamique avec les PDFs
                crew = build_dynamic_marketing_crew(
                    problem_statement=problem_statement,
                    company_context=company_context,
                    config_manager=st.session_state.config_manager,
                    pdf_paths=pdf_paths
                )
                
                # Lancer l'équipe
                result = crew.kickoff()
            
            # Afficher les résultats de manière claire
            st.success("✅ Analyse terminée et contenu généré avec succès !")
            
            # Afficher le résultat brut pour l'instant
            st.markdown("## 📋 Résultat de l'analyse")
            st.text_area("Résultat complet", value=str(result), height=400)
            
            # Parser et afficher les posts de manière structurée
            display_generated_posts(result)
    
    if not problem_statement.strip():
        st.info("💡 Décrivez votre problématique marketing pour que le Meta Agent Manager puisse créer des tâches adaptées")

with tab2:
    st.title("📄 Gestion des Documents PDF")
    
    st.write("**Uploadez vos PDFs pour que les agents puissent les utiliser comme sources de connaissances.**")
    
    # Upload de PDFs
    uploaded_files = st.file_uploader(
        "Choisissez des fichiers PDF", 
        type=['pdf'], 
        accept_multiple_files=True,
        help="Les agents pourront utiliser ces documents comme sources de connaissances"
    )
    
    # Stocker les PDFs dans la session state
    if 'uploaded_pdfs' not in st.session_state:
        st.session_state.uploaded_pdfs = []
    
    if uploaded_files:
        # Sauvegarder les fichiers temporairement
        import tempfile
        import os
        
        pdf_paths = []
        for uploaded_file in uploaded_files:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                pdf_paths.append(tmp_file.name)
        
        st.session_state.uploaded_pdfs = pdf_paths
        
        st.success(f"✅ {len(uploaded_files)} PDF(s) uploadé(s) et prêt(s) pour les agents!")
        
        # Afficher la liste des PDFs
        st.write("**PDFs disponibles pour les agents :**")
        for i, file in enumerate(uploaded_files):
            st.write(f"📄 {file.name}")
        
        # Afficher les chemins pour debug
        st.write("**Chemins des fichiers :**")
        for i, path in enumerate(pdf_paths):
            st.code(f"Fichier {i+1}: {path}")
    
    # Bouton pour vider les PDFs
    if st.session_state.uploaded_pdfs:
        if st.button("🗑️ Vider tous les PDFs"):
            # Supprimer les fichiers temporaires
            for pdf_path in st.session_state.uploaded_pdfs:
                try:
                    os.unlink(pdf_path)
                except:
                    pass
            
            # Supprimer aussi les PDFs du dossier knowledge
            knowledge_dir = "knowledge"
            if os.path.exists(knowledge_dir):
                import shutil
                try:
                    shutil.rmtree(knowledge_dir)
                    st.write("📁 Dossier knowledge supprimé")
                except:
                    pass
            
            st.session_state.uploaded_pdfs = []
            st.success("Tous les PDFs ont été supprimés!")
            st.rerun()
    
    st.info("""
    **Comment ça fonctionne :**
    
    1. **Uploadez vos PDFs** : Les fichiers sont copiés dans le dossier `knowledge/`
    2. **Sources de connaissances** : Les agents accèdent aux PDFs via `PDFKnowledgeSource`
    3. **Recherche automatique** : Les agents peuvent chercher dans le contenu des PDFs
    4. **Enrichissement** : Les réponses des agents sont enrichies avec vos données PDF
    
    Les agents utiliseront automatiquement ces PDFs lors de l'exécution de leurs tâches.
    """)
    
    # Afficher le contenu du dossier knowledge
    knowledge_dir = "knowledge"
    if os.path.exists(knowledge_dir):
        st.write("**📁 Contenu du dossier knowledge :**")
        knowledge_files = os.listdir(knowledge_dir)
        if knowledge_files:
            for file in knowledge_files:
                st.write(f"📄 {file}")
        else:
            st.write("Aucun fichier dans le dossier knowledge")

with tab3:
    st.title("⚙️ Configuration des Agents")
    
    agents = st.session_state.config_manager.get_all_agents()
    
    for agent_name, agent_config in agents.items():
        with st.expander(f"🤖 {agent_config.name}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Rôle", value=agent_config.role, key=f"{agent_name}_role")
                st.text_area("Objectif", value=agent_config.goal, key=f"{agent_name}_goal", height=100)
            
            with col2:
                st.text_area("Backstory", value=agent_config.backstory, key=f"{agent_name}_backstory", height=100)
                st.number_input("Max Iterations", value=agent_config.max_iter, min_value=1, max_value=10, key=f"{agent_name}_max_iter")
            
            st.checkbox("Verbose", value=agent_config.verbose, key=f"{agent_name}_verbose")
            st.checkbox("Memory", value=agent_config.memory, key=f"{agent_name}_memory")
            st.checkbox("Allow Delegation", value=agent_config.allow_delegation, key=f"{agent_name}_delegation")
            
            # Configuration des outils pour cet agent
            available_tools = st.session_state.config_manager.get_available_tools()
            enabled_tools = []
            
            st.write("**Outils disponibles:**")
            for tool_name, tool_info in available_tools.items():
                if st.checkbox(
                    f"{tool_info['name']} - {tool_info['description']}", 
                    value=tool_name in agent_config.enabled_tools,
                    key=f"{agent_name}_tool_{tool_name}"
                ):
                    enabled_tools.append(tool_name)
            
            if st.button(f"💾 Sauvegarder {agent_config.name}", key=f"save_{agent_name}"):
                # Mettre à jour la configuration
                agent_config.role = st.session_state[f"{agent_name}_role"]
                agent_config.goal = st.session_state[f"{agent_name}_goal"]
                agent_config.backstory = st.session_state[f"{agent_name}_backstory"]
                agent_config.verbose = st.session_state[f"{agent_name}_verbose"]
                agent_config.max_iter = st.session_state[f"{agent_name}_max_iter"]
                agent_config.memory = st.session_state[f"{agent_name}_memory"]
                agent_config.allow_delegation = st.session_state[f"{agent_name}_delegation"]
                agent_config.enabled_tools = enabled_tools
                
                st.session_state.config_manager.update_agent_config(agent_name, agent_config)
                st.success(f"Configuration de {agent_config.name} sauvegardée!")
    
    # Boutons d'action globaux
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Réinitialiser tout"):
            st.session_state.config_manager = AgentConfigManager()
            st.rerun()
    
    with col2:
        if st.button("📥 Exporter config"):
            config = st.session_state.config_manager.export_config()
            st.download_button(
                label="Télécharger config.json",
                data=json.dumps(config, indent=2, ensure_ascii=False),
                file_name="agent_config.json",
                mime="application/json"
            )
    
    with col3:
        uploaded_file = st.file_uploader("📤 Importer config", type=['json'])
        if uploaded_file is not None:
            try:
                config = json.load(uploaded_file)
                st.session_state.config_manager.import_config(config)
                st.success("Configuration importée!")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'import: {e}")

with tab4:
    st.title("🔧 Configuration des Outils")
    
    available_tools = get_available_tools()
    
    st.write("**Outils disponibles dans le système:**")
    
    for tool_name, tool_info in available_tools.items():
        with st.expander(f"🔧 {tool_info['name']}", expanded=False):
            st.write(f"**Description:** {tool_info['description']}")
            st.write(f"**Statut:** {'✅ Activé' if tool_info['enabled'] else '❌ Désactivé'}")
            
            if tool_name == "serper_search":
                st.info("💡 Pour activer Serper, ajoutez SERPER_API_KEY dans la sidebar ou .env")
            elif tool_name in ["website_search", "scrape_website"]:
                st.info("💡 Ces outils sont toujours disponibles")
            elif tool_name in ["pdf_search", "rag_tool"]:
                st.info("💡 Ces outils CrewAI natifs permettent de lire et rechercher dans les PDFs")
    
    st.write("**Configuration des clés API:**")
    st.code("""
# Dans .env ou variables d'environnement:
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...  # Optionnel pour recherche web
OPENAI_MODEL=gpt-4o-mini
    """)