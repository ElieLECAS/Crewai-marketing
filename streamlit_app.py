import os
import streamlit as st
import json
import pandas as pd
import re
from dotenv import load_dotenv
from rich.console import Console
from src.crew import build_dynamic_marketing_crew, build_two_phase_marketing_crew, build_ordered_crew_from_meta_result
from src.agent_config import AgentConfigManager
from src.crew_config import CrewConfigManager
from src.tools import get_available_tools

load_dotenv()
console = Console()

# Désactiver la télémetrie CrewAI pour éviter les erreurs
import os
os.environ["CREWAI_TELEMETRY"] = "False"

st.set_page_config(page_title="CrewAI Marketing", page_icon="📈", layout="wide")

# Initialiser la session state
if 'config_manager' not in st.session_state:
    st.session_state.config_manager = AgentConfigManager()

if 'crew_config_manager' not in st.session_state:
    st.session_state.crew_config_manager = CrewConfigManager(st.session_state.config_manager)

def parse_markdown_result(result):
    """Parse le résultat Markdown et extrait les sections structurées"""
    result_str = str(result)
    
    # Dictionnaire pour stocker les sections parsées
    parsed_sections = {
        'meta_manager': '',
        'linkedin_posts': [],
        'instagram_posts': [],
        'other_content': []
    }
    
    # Diviser le résultat en lignes
    lines = result_str.split('\n')
    current_section = 'other_content'
    current_post = ''
    post_counter = 0
    
    for line in lines:
        line = line.strip()
        
        # Détecter les sections principales
        if 'meta manager' in line.lower() or 'meta agent' in line.lower() or 'plan d\'action' in line.lower():
            current_section = 'meta_manager'
            continue
        elif 'linkedin' in line.lower() and ('post' in line.lower() or 'contenu' in line.lower()):
            current_section = 'linkedin_posts'
            continue
        elif 'instagram' in line.lower() and ('post' in line.lower() or 'contenu' in line.lower()):
            current_section = 'instagram_posts'
            continue
        
        # Traiter les posts
        if current_section in ['linkedin_posts', 'instagram_posts']:
            if line.startswith('**') and 'post' in line.lower():
                # Nouveau post détecté
                if current_post:
                    parsed_sections[current_section].append(current_post.strip())
                current_post = line + '\n'
                post_counter += 1
            elif line and not line.startswith('---'):
                current_post += line + '\n'
        else:
            # Contenu général
            if current_section == 'meta_manager':
                parsed_sections['meta_manager'] += line + '\n'
            else:
                parsed_sections['other_content'].append(line)
    
    # Ajouter le dernier post s'il existe
    if current_post:
        parsed_sections[current_section].append(current_post.strip())
    
    return parsed_sections

def extract_posts_from_text(text, platform):
    """Extrait les posts d'une plateforme spécifique du texte"""
    posts = []
    lines = text.split('\n')
    current_post = ''
    in_post = False
    
    for line in lines:
        line = line.strip()
        
        # Détecter le début d'un post
        if platform.lower() in line.lower() and ('post' in line.lower() or 'contenu' in line.lower()):
            if current_post:
                posts.append(current_post.strip())
            current_post = line + '\n'
            in_post = True
        elif in_post and line and not line.startswith('---'):
            current_post += line + '\n'
        elif in_post and line.startswith('---'):
            in_post = False
            if current_post:
                posts.append(current_post.strip())
                current_post = ''
    
    # Ajouter le dernier post s'il existe
    if current_post:
        posts.append(current_post.strip())
    
    return posts

def smart_parse_result(result):
    """Parse intelligent du résultat avec détection automatique des sections"""
    result_str = str(result)
    
    # Dictionnaire pour stocker les sections parsées
    parsed_sections = {
        'meta_manager': '',
        'linkedin_posts': [],
        'instagram_posts': [],
        'other_content': []
    }
    
    # Extraire les posts LinkedIn
    linkedin_posts = extract_posts_from_text(result_str, 'linkedin')
    parsed_sections['linkedin_posts'] = linkedin_posts
    
    # Extraire les posts Instagram
    instagram_posts = extract_posts_from_text(result_str, 'instagram')
    parsed_sections['instagram_posts'] = instagram_posts
    
    # Extraire le plan du Meta Manager
    lines = result_str.split('\n')
    meta_manager_content = []
    in_meta_section = False
    
    for line in lines:
        line = line.strip()
        
        if 'meta manager' in line.lower() or 'meta agent' in line.lower() or 'plan d\'action' in line.lower():
            in_meta_section = True
            meta_manager_content.append(line)
        elif in_meta_section and ('linkedin' in line.lower() or 'instagram' in line.lower()):
            in_meta_section = False
            break
        elif in_meta_section:
            meta_manager_content.append(line)
    
    parsed_sections['meta_manager'] = '\n'.join(meta_manager_content)
    
    # Le reste du contenu
    other_content = []
    for line in lines:
        line = line.strip()
        if line and not any(keyword in line.lower() for keyword in ['meta manager', 'meta agent', 'linkedin', 'instagram', 'post']):
            other_content.append(line)
    
    parsed_sections['other_content'] = other_content
    
    return parsed_sections

def format_markdown_text(text):
    """Formate le texte Markdown pour un meilleur affichage"""
    if not text:
        return text
    
    # Remplacer les éléments Markdown par du HTML pour un meilleur rendu
    formatted = text
    
    # Gras
    formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
    
    # Italique
    formatted = formatted.replace('*', '<em>').replace('*', '</em>')
    
    # Listes à puces
    lines = formatted.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                formatted_lines.append('<ul>')
                in_list = True
            formatted_lines.append(f'<li>{line.strip()[2:]}</li>')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(line)
    
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

def display_parsed_result(result):
    """Affiche le résultat parsé avec un formatage Markdown amélioré"""
    parsed = smart_parse_result(result)
    
    # Section Meta Manager
    if parsed['meta_manager']:
        st.markdown("---")
        st.markdown("## 🧠 Plan du Meta Manager")
        
        # Afficher le plan du Meta Manager avec formatage Markdown
        st.markdown(parsed['meta_manager'])
        
        # Boutons d'action pour le plan du Meta Manager
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Copier le plan", key="copy_meta_plan", type="secondary"):
                st.code(parsed['meta_manager'], language="text")
                st.success("Plan affiché ci-dessus - vous pouvez le copier !")
        
        with col_btn2:
            if st.button("📥 Télécharger le plan", key="download_meta_plan", type="secondary"):
                st.download_button(
                    label="Télécharger le plan",
                    data=parsed['meta_manager'],
                    file_name="plan_meta_manager.txt",
                    mime="text/plain"
                )
    
    # Section LinkedIn Posts
    if parsed['linkedin_posts']:
        st.markdown("---")
        st.markdown("## 💼 Posts LinkedIn")
    
    # Créer des colonnes pour afficher les posts
    col1, col2 = st.columns(2)
    
    for i, post in enumerate(parsed['linkedin_posts']):
            with (col1 if i % 2 == 0 else col2):
                # Extraire le titre du post
                lines = post.split('\n')
                title = lines[0] if lines else f"Post LinkedIn {i+1}"
                content = '\n'.join(lines[1:]) if len(lines) > 1 else post
                
                # Afficher le titre formaté
                st.markdown(f"**{title}**")
                
                # Afficher le contenu dans une text_area éditable
                edited_content = st.text_area(
                    f"Contenu du {title.lower()}",
                    value=content.strip(),
                    height=120,
                    key=f"linkedin_{i+1}",
                    label_visibility="collapsed"
                )
                
                # Boutons d'action pour ce post
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📋 Copier", key=f"copy_linkedin_{i+1}", type="secondary"):
                        st.code(edited_content, language="text")
                        st.success("Contenu affiché ci-dessus - vous pouvez le copier !")
                
                with col_btn2:
                    if st.button("📥 Télécharger", key=f"download_linkedin_{i+1}", type="secondary"):
                        st.download_button(
                            label="Télécharger ce post",
                            data=edited_content,
                            file_name=f"post_linkedin_{i+1}.txt",
                            mime="text/plain"
                        )
    
    # Section Instagram Posts
    if parsed['instagram_posts']:
        st.markdown("---")
        st.markdown("## 📸 Posts Instagram")
    
        # Créer des colonnes pour afficher les posts
        col1, col2 = st.columns(2)
        
        for i, post in enumerate(parsed['instagram_posts']):
            with (col1 if i % 2 == 0 else col2):
                # Extraire le titre du post
                lines = post.split('\n')
                title = lines[0] if lines else f"Post Instagram {i+1}"
                content = '\n'.join(lines[1:]) if len(lines) > 1 else post
                
                # Afficher le titre formaté
                st.markdown(f"**{title}**")
                
                # Afficher le contenu dans une text_area éditable
                edited_content = st.text_area(
                    f"Contenu du {title.lower()}",
                    value=content.strip(),
                    height=120,
                    key=f"instagram_{i+1}",
                    label_visibility="collapsed"
                )
                
                # Boutons d'action pour ce post
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("📋 Copier", key=f"copy_instagram_{i+1}", type="secondary"):
                        st.code(edited_content, language="text")
                        st.success("Contenu affiché ci-dessus - vous pouvez le copier !")
                
                with col_btn2:
                    if st.button("📥 Télécharger", key=f"download_instagram_{i+1}", type="secondary"):
                        st.download_button(
                            label="Télécharger ce post",
                            data=edited_content,
                            file_name=f"post_instagram_{i+1}.txt",
                            mime="text/plain"
                        )
    
    # Section Autres contenus
    if parsed['other_content']:
        st.markdown("---")
        st.markdown("## 📋 Autres contenus")
        for content in parsed['other_content']:
            if content.strip():
                st.markdown(content)
    
    # Boutons d'action globaux
    st.markdown("---")
    st.markdown("## 🔧 Actions globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📥 Télécharger tous les posts", type="secondary"):
            # Collecter tous les posts
            all_posts = []
            for post in parsed['linkedin_posts'] + parsed['instagram_posts']:
                all_posts.append(post)
            
            # Créer un fichier texte
            posts_text = "\n\n".join(all_posts)
            st.download_button(
                label="Télécharger posts.txt",
                data=posts_text,
                file_name="posts_generes.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📋 Copier tous les posts", type="secondary"):
            # Collecter tous les posts
            all_posts = []
            for post in parsed['linkedin_posts'] + parsed['instagram_posts']:
                all_posts.append(post)
            
            posts_text = "\n\n".join(all_posts)
            st.code(posts_text, language="text")
            st.success("Contenu affiché ci-dessus - vous pouvez le copier !")
    
    with col3:
        if st.button("📊 Télécharger rapport complet", type="secondary"):
            # Créer un rapport complet
            rapport_complet = []
            
            if parsed['meta_manager']:
                rapport_complet.append("=== PLAN DU META MANAGER ===")
                rapport_complet.append(parsed['meta_manager'])
                rapport_complet.append("")
            
            if parsed['linkedin_posts']:
                rapport_complet.append("=== POSTS LINKEDIN ===")
                for i, post in enumerate(parsed['linkedin_posts'], 1):
                    rapport_complet.append(f"Post LinkedIn {i}:")
                    rapport_complet.append(post)
                    rapport_complet.append("")
            
            if parsed['instagram_posts']:
                rapport_complet.append("=== POSTS INSTAGRAM ===")
                for i, post in enumerate(parsed['instagram_posts'], 1):
                    rapport_complet.append(f"Post Instagram {i}:")
                    rapport_complet.append(post)
                    rapport_complet.append("")
            
            rapport_text = "\n".join(rapport_complet)
            st.download_button(
                label="Télécharger rapport complet",
                data=rapport_text,
                file_name="rapport_campagne_complet.txt",
                mime="text/plain"
            )
    
    with col4:
        if st.button("🔄 Régénérer les posts", type="secondary"):
            st.rerun()

def display_enhanced_result(result):
    """Affiche le résultat avec un formatage Markdown amélioré et des posts éditables"""
    result_str = str(result)
    
    # Afficher le résultat brut dans un onglet
    tab1, tab2 = st.tabs(["📋 Résultat Formaté", "🔍 Résultat Brut"])
    
    with tab1:
        # Parser et afficher le résultat formaté
        display_parsed_result(result)
    
    with tab2:
        # Afficher le résultat brut avec formatage Markdown
        st.markdown("## 📄 Résultat Brut (Markdown)")
        st.markdown(result_str)
        
        # Bouton pour copier le résultat brut
        if st.button("📋 Copier le résultat brut", type="secondary"):
            st.code(result_str, language="text")
            st.success("Résultat affiché ci-dessus - vous pouvez le copier !")

def display_generated_posts(result):
    """Affiche les posts générés de manière claire et structurée"""
    # Afficher le résultat parsé
    display_parsed_result(result)

def parse_agent_outputs_improved(result_str):
    """Parse amélioré des outputs des agents avec détection intelligente"""
    agent_sections = {}
    current_agent = None
    current_content = []
    
    lines = result_str.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Détecter les sections d'agents avec des patterns plus robustes
        agent_patterns = [
            r'^#+\s*(meta\s+manager|meta\s+agent)',
            r'^#+\s*(clara|détective\s+digitale)',
            r'^#+\s*(julien|analyste\s+stratégique)',
            r'^#+\s*(sophie|plume\s+solidaire)',
            r'^#+\s*(agent|résultat).*:',
            r'^##\s*(.*agent.*)',
            r'^###\s*(.*agent.*)'
        ]
        
        is_agent_section = False
        for pattern in agent_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                is_agent_section = True
                break
        
        if is_agent_section:
            # Sauvegarder le contenu précédent
            if current_agent and current_content:
                agent_sections[current_agent] = '\n'.join(current_content)
            
            # Nouvelle section d'agent
            current_agent = line.replace('#', '').strip()
            current_content = [line]
        elif current_agent and line:
            current_content.append(line)
    
    # Sauvegarder la dernière section
    if current_agent and current_content:
        agent_sections[current_agent] = '\n'.join(current_content)
    
    return agent_sections

def detect_content_type(content):
    """Détecte le type de contenu généré par l'agent"""
    content_lower = content.lower()
    
    if 'linkedin' in content_lower and ('post' in content_lower or 'contenu' in content_lower):
        return "Posts LinkedIn"
    elif 'instagram' in content_lower and ('post' in content_lower or 'contenu' in content_lower):
        return "Posts Instagram"
    elif any(keyword in content_lower for keyword in ['plan', 'stratégie', 'recommandation', 'objectif']):
        return "Plan stratégique"
    elif any(keyword in content_lower for keyword in ['analyse', 'données', 'tendances', 'recherche']):
        return "Analyse de données"
    elif any(keyword in content_lower for keyword in ['rapport', 'étude', 'évaluation']):
        return "Rapport d'analyse"
    else:
        return "Contenu général"

def get_file_extension(content_type):
    """Retourne l'extension de fichier appropriée selon le type de contenu"""
    if content_type == "Posts LinkedIn":
        return "md"
    elif content_type == "Posts Instagram":
        return "md"
    elif content_type == "Plan stratégique":
        return "md"
    elif content_type == "Analyse de données":
        return "txt"
    else:
        return "txt"

def display_linkedin_posts(content):
    """Affiche les posts LinkedIn de manière structurée"""
    posts = extract_posts_from_text(content, 'linkedin')
    
    if posts:
        for i, post in enumerate(posts, 1):
            with st.expander(f"📝 Post LinkedIn {i}", expanded=True):
                st.markdown(post)
                
                # Boutons d'action pour chaque post
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copier Post {i}", key=f"copy_linkedin_post_{i}"):
                        st.code(post, language="text")
                        st.success("✅ Post affiché ci-dessus !")
                with col2:
                    if st.button(f"📥 Télécharger Post {i}", key=f"download_linkedin_post_{i}"):
                        st.download_button(
                            label=f"Télécharger Post {i}",
                            data=post,
                            file_name=f"post_linkedin_{i}.md",
                            mime="text/plain"
                        )
    else:
        st.markdown(content)

def display_instagram_posts(content):
    """Affiche les posts Instagram de manière structurée"""
    posts = extract_posts_from_text(content, 'instagram')
    
    if posts:
        for i, post in enumerate(posts, 1):
            with st.expander(f"📸 Post Instagram {i}", expanded=True):
                st.markdown(post)
                
                # Boutons d'action pour chaque post
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copier Post {i}", key=f"copy_instagram_post_{i}"):
                        st.code(post, language="text")
                        st.success("✅ Post affiché ci-dessus !")
                with col2:
                    if st.button(f"📥 Télécharger Post {i}", key=f"download_instagram_post_{i}"):
                        st.download_button(
                            label=f"Télécharger Post {i}",
                            data=post,
                            file_name=f"post_instagram_{i}.md",
                            mime="text/plain"
                        )
    else:
        st.markdown(content)

def display_strategic_plan(content):
    """Affiche un plan stratégique de manière structurée"""
    # Diviser le contenu en sections
    sections = content.split('\n\n')
    
    for i, section in enumerate(sections):
        if section.strip():
            # Détecter les titres
            if section.strip().startswith('#'):
                st.markdown(section)
            else:
                # Afficher dans une boîte stylée
                st.info(section)

def display_data_analysis(content):
    """Affiche une analyse de données de manière structurée"""
    # Diviser le contenu en sections
    sections = content.split('\n\n')
    
    for i, section in enumerate(sections):
        if section.strip():
            # Détecter les listes à puces
            if section.strip().startswith('- '):
                st.markdown(section)
            else:
                # Afficher dans une boîte stylée
                st.success(section)

def analyze_agent_output(agent_name, content):
    """Analyse l'output d'un agent et affiche des insights"""
    st.markdown(f"### 🔍 Analyse de l'output de {agent_name}")
    
    # Statistiques de base
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        word_count = len(content.split())
        st.metric("Mots", word_count)
    
    with col2:
        char_count = len(content)
        st.metric("Caractères", char_count)
    
    with col3:
        line_count = len(content.split('\n'))
        st.metric("Lignes", line_count)
    
    with col4:
        # Détecter les hashtags
        hashtag_count = content.count('#')
        st.metric("Hashtags", hashtag_count)
    
    # Analyse du contenu
    st.markdown("#### 📊 Analyse du contenu")
    
    # Détecter les sections principales
    sections = content.split('\n\n')
    st.write(f"**Nombre de sections:** {len(sections)}")
    
    # Détecter les mots-clés fréquents
    words = content.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 3:  # Ignorer les mots courts
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Top 10 des mots les plus fréquents
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top_words:
        st.write("**Mots-clés les plus fréquents:**")
        for word, count in top_words:
            st.write(f"- {word}: {count} fois")
    
    # Détecter les émotions/ton
    positive_words = ['excellent', 'génial', 'fantastique', 'super', 'parfait', 'réussi']
    negative_words = ['problème', 'difficile', 'compliqué', 'échec', 'raté']
    
    positive_count = sum(1 for word in positive_words if word in content.lower())
    negative_count = sum(1 for word in negative_words if word in content.lower())
    
    if positive_count > negative_count:
        st.success("😊 Ton globalement positif")
    elif negative_count > positive_count:
        st.warning("😟 Ton globalement négatif")
    else:
        st.info("😐 Ton neutre")

def show_outputs_statistics():
    """Affiche des statistiques détaillées sur les outputs sauvegardés"""
    st.markdown("### 📊 Statistiques détaillées des outputs")
    
    if not st.session_state.agent_outputs:
        st.warning("Aucun output sauvegardé")
        return
    
    # Statistiques globales
    total_agents = len(st.session_state.agent_outputs)
    total_chars = sum(len(content) for content in st.session_state.agent_outputs.values())
    total_words = sum(len(content.split()) for content in st.session_state.agent_outputs.values())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Agents", total_agents)
    
    with col2:
        st.metric("Total caractères", f"{total_chars:,}")
    
    with col3:
        st.metric("Total mots", f"{total_words:,}")
    
    with col4:
        avg_words = total_words // total_agents if total_agents > 0 else 0
        st.metric("Moyenne mots/agent", avg_words)
    
    # Analyse par type de contenu
    st.markdown("#### 📈 Répartition par type de contenu")
    content_types = {}
    for agent_name, content in st.session_state.agent_outputs.items():
        content_type = detect_content_type(content)
        content_types[content_type] = content_types.get(content_type, 0) + 1
    
    for content_type, count in content_types.items():
        percentage = (count / total_agents) * 100
        st.write(f"**{content_type}:** {count} agent(s) ({percentage:.1f}%)")
    
    # Top 10 des mots les plus fréquents (tous agents confondus)
    st.markdown("#### 🔤 Mots-clés les plus fréquents")
    all_words = []
    for content in st.session_state.agent_outputs.values():
        words = content.lower().split()
        all_words.extend(words)
    
    word_freq = {}
    for word in all_words:
        if len(word) > 3:  # Ignorer les mots courts
            word_freq[word] = word_freq.get(word, 0) + 1
    
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if top_words:
        for i, (word, count) in enumerate(top_words, 1):
            st.write(f"{i}. **{word}** - {count} fois")
    else:
        st.write("Aucun mot-clé détecté")
    
    # Analyse de la qualité
    st.markdown("#### 🎯 Analyse de la qualité")
    
    # Détecter les outputs avec des hashtags
    hashtag_outputs = sum(1 for content in st.session_state.agent_outputs.values() if '#' in content)
    st.write(f"**Outputs avec hashtags:** {hashtag_outputs}/{total_agents}")
    
    # Détecter les outputs avec des listes
    list_outputs = sum(1 for content in st.session_state.agent_outputs.values() if '- ' in content or '* ' in content)
    st.write(f"**Outputs avec listes:** {list_outputs}/{total_agents}")
    
    # Détecter les outputs avec des titres
    title_outputs = sum(1 for content in st.session_state.agent_outputs.values() if content.strip().startswith('#'))
    st.write(f"**Outputs avec titres:** {title_outputs}/{total_agents}")
    
    # Recommandations
    st.markdown("#### 💡 Recommandations")
    
    if hashtag_outputs < total_agents * 0.5:
        st.info("💡 Considérez ajouter plus de hashtags pour améliorer la visibilité")
    
    if list_outputs < total_agents * 0.3:
        st.info("💡 Utilisez plus de listes à puces pour structurer le contenu")
    
    if title_outputs < total_agents * 0.7:
        st.info("💡 Ajoutez des titres pour mieux organiser le contenu")
    
    # Export des statistiques
    st.markdown("#### 📤 Export des statistiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Exporter statistiques", type="primary"):
            stats_data = {
                "total_agents": total_agents,
                "total_characters": total_chars,
                "total_words": total_words,
                "average_words_per_agent": avg_words,
                "content_types": content_types,
                "top_words": top_words,
                "quality_metrics": {
                    "hashtag_outputs": hashtag_outputs,
                    "list_outputs": list_outputs,
                    "title_outputs": title_outputs
                }
            }
            
            st.download_button(
                label="Télécharger statistiques JSON",
                data=json.dumps(stats_data, indent=2, ensure_ascii=False),
                file_name="outputs_statistics.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Copier statistiques", type="secondary"):
            stats_text = f"""
=== STATISTIQUES DES OUTPUTS ===

Agents: {total_agents}
Total caractères: {total_chars:,}
Total mots: {total_words:,}
Moyenne mots/agent: {avg_words}

RÉPARTITION PAR TYPE:
{chr(10).join([f"- {content_type}: {count} agent(s)" for content_type, count in content_types.items()])}

TOP 10 MOTS-CLÉS:
{chr(10).join([f"{i}. {word} - {count} fois" for i, (word, count) in enumerate(top_words, 1)])}

MÉTRIQUES DE QUALITÉ:
- Outputs avec hashtags: {hashtag_outputs}/{total_agents}
- Outputs avec listes: {list_outputs}/{total_agents}
- Outputs avec titres: {title_outputs}/{total_agents}
            """
            st.code(stats_text, language="text")
            st.success("✅ Statistiques affichées ci-dessus !")

# Navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Campagne", 
    "🤖 Gestion Agents", 
    "👥 Gestion Crews", 
    "📄 Documents PDF", 
    "🔧 Outils",
    "📊 Outputs Agents"
])

with tab1:
    st.title("🎯 Campagne Marketing")
    
    # Information sur l'utilisation
    st.info("""
    **🚀 Interface CrewAI Marketing :**
    
    1. **Créez vos agents** dans l'onglet "🤖 Gestion Agents" avec le bouton "➕ Créer un nouvel agent"
    2. **Créez vos crews** dans l'onglet "👥 Gestion Crews" en sélectionnant les agents souhaités
    3. **Lancez votre campagne** en sélectionnant le crew et en décrivant votre problématique
    4. **Le Meta Manager** analysera automatiquement votre problématique et créera/répartira les tâches aux agents
    """)
    
    # Information sur les optimisations de tokens
    st.success("""
    **⚡ Optimisations de Performance :**
    
    - **Gestion des tokens** : Le système optimise automatiquement la taille des requêtes pour éviter les limites de tokens
    - **Contexte simplifié** : Les descriptions sont raccourcies intelligemment pour respecter les limites des modèles
    - **Pas de contexte entre agents** : Chaque agent travaille de manière indépendante pour éviter l'accumulation de tokens
    - **Limites respectées** : Compatible avec gpt-4o-mini (200K tokens/minute) et autres modèles
    """)
    
    # Sélection du crew
    st.markdown("### 👥 Sélection du Crew")
    crews = st.session_state.crew_config_manager.get_all_crews()
    
    if crews:
        crew_names = list(crews.keys())
        selected_crew_name = st.selectbox(
            "Choisissez le crew à utiliser pour cette campagne :",
            crew_names,
            help="Sélectionnez le crew qui sera utilisé pour exécuter les tâches de votre campagne"
        )
        
        if selected_crew_name:
            selected_crew = crews[selected_crew_name]
            st.info(f"**Crew sélectionné :** {selected_crew.name}")
            st.write(f"**Description :** {selected_crew.description}")
            st.write(f"**Agents :** {', '.join(selected_crew.selected_agents)}")
            st.info("💡 Le Meta Manager créera automatiquement les tâches selon votre problématique")
    else:
        st.warning("Aucun crew configuré. Créez d'abord des agents et des crews dans les onglets correspondants.")
        selected_crew_name = None
    
    with st.sidebar:
        st.header("🔑 Configuration API")
        openai_key = st.text_input("OPENAI_API_KEY", type="password", value=os.getenv("OPENAI_API_KEY", ""))
        serper_key = st.text_input("SERPER_API_KEY", type="password", value=os.getenv("SERPER_API_KEY", ""))
        model = st.text_input("OPENAI_MODEL", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        st.caption("Ces valeurs peuvent aussi venir de .env")
        
        st.markdown("---")
        st.info("""
        **💡 Conseils :**
        - La télémetrie CrewAI est désactivée
        - Les PDFs sont automatiquement copiés dans le dossier `knowledge/`
        - Vérifiez vos clés API si des erreurs surviennent
        """)
    
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
    run_disabled = not problem_statement.strip() or not selected_crew_name
    
    if st.button("🚀 Lancer la campagne avec le crew sélectionné", type="primary", disabled=run_disabled):
        if not openai_key:
            st.error("❌ OPENAI_API_KEY manquant. Renseignez la clé dans la sidebar.")
        else:
            # Configuration des variables d'environnement
            os.environ["OPENAI_API_KEY"] = openai_key
            if serper_key:
                os.environ["SERPER_API_KEY"] = serper_key
            if model:
                os.environ["OPENAI_MODEL"] = model
            
            with st.spinner(f"🤖 Phase 1 : Le Meta Manager analyse votre problématique..."):
                try:
                    # Phase 1: Créer et exécuter le Meta Manager seul
                    meta_crew, task_manager, available_agents = build_two_phase_marketing_crew(
                        problem_statement=problem_statement,
                        company_context=company_context,
                        config_manager=st.session_state.config_manager,
                        pdf_paths=pdf_paths,
                        selected_agents=selected_crew.selected_agents
                    )
                    
                    # Exécuter le Meta Manager
                    st.info("🧠 Le Meta Manager analyse la problématique et définit l'ordre d'exécution optimal...")
                    meta_result = meta_crew.kickoff()
                    
                    # Afficher le plan du Meta Manager
                    st.success("✅ Phase 1 terminée : Plan d'exécution créé par le Meta Manager")
                    with st.expander("📋 Voir le plan du Meta Manager", expanded=True):
                        st.markdown(str(meta_result))
                    
                    # Phase 2: Créer et exécuter les agents dans l'ordre recommandé
                    st.info("🚀 Phase 2 : Exécution des agents dans l'ordre recommandé...")
                    
                    ordered_crew = build_ordered_crew_from_meta_result(
                        meta_result=str(meta_result),
                        problem_statement=problem_statement,
                        company_context=company_context,
                        config_manager=st.session_state.config_manager,
                        pdf_paths=pdf_paths,
                        available_agents=available_agents
                    )
                    
                    # Exécuter les agents dans l'ordre recommandé
                    agents_result = ordered_crew.kickoff()
                    
                    # Combiner les résultats
                    result = f"{meta_result}\n\n---\n\nRÉSULTATS DES AGENTS:\n\n{agents_result}"
                    
                    # Sauvegarder le résultat dans la session state pour l'onglet Outputs Agents
                    st.session_state.last_campaign_result = result
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'exécution du crew : {str(e)}")
                    st.error("💡 Vérifiez vos clés API et la configuration des agents")
                    result = None
            
            # Afficher les résultats de manière claire
            if result is not None:
                st.success("✅ Campagne terminée avec succès !")
                
                # Afficher le résultat avec formatage Markdown amélioré
                display_enhanced_result(result)
            else:
                st.error("❌ La campagne n'a pas pu être exécutée. Vérifiez les erreurs ci-dessus.")
    
    if not problem_statement.strip():
        st.info("💡 Décrivez votre problématique marketing pour que le Meta Agent Manager puisse créer des tâches adaptées")

with tab2:
    st.title("🤖 Gestion des Agents")
    
    # Section de création d'agent avec design en grille
    st.markdown("### ➕ Créer un nouvel agent")
    
    # Bouton de création dans un conteneur stylé
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Créer un nouvel agent", type="primary", use_container_width=True):
            st.session_state.show_new_agent_form = True
    
    if st.session_state.get('show_new_agent_form', False):
        st.markdown("### ➕ Créer un nouvel agent")
        
        with st.form("new_agent_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Nom de l'agent", placeholder="ex: mon_agent")
                new_role = st.text_input("Rôle", placeholder="ex: Analyste Marketing")
                new_goal = st.text_area("Objectif", placeholder="Décrivez l'objectif principal de cet agent", height=100)
            
            with col2:
                new_backstory = st.text_area("Backstory", placeholder="Décrivez l'histoire et les compétences de cet agent", height=100)
                new_max_iter = st.number_input("Max Iterations", value=3, min_value=1, max_value=10)
                new_verbose = st.checkbox("Verbose", value=True)
            
            # Configuration des outils
            available_tools = st.session_state.config_manager.get_available_tools()
            st.write("**Outils disponibles :**")
            selected_tools = []
            for tool_name, tool_info in available_tools.items():
                if st.checkbox(f"{tool_info['name']} - {tool_info['description']}", key=f"new_agent_tool_{tool_name}"):
                    selected_tools.append(tool_name)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer l'agent", type="primary"):
                    if new_name and new_role and new_goal:
                        try:
                            agent_name = st.session_state.config_manager.create_new_agent(
                                name=new_name,
                                role=new_role,
                                goal=new_goal,
                                backstory=new_backstory,
                                enabled_tools=selected_tools,
                                max_iter=new_max_iter,
                                verbose=new_verbose
                            )
                            st.success(f"Agent '{agent_name}' créé avec succès !")
                            st.session_state.show_new_agent_form = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la création : {e}")
                    else:
                        st.error("Veuillez remplir au moins le nom, le rôle et l'objectif")
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_new_agent_form = False
                    st.rerun()
    
    # Affichage des agents existants en grille
    st.markdown("### 📋 Agents existants")
    agents = st.session_state.config_manager.get_all_agents()
    
    if agents:
        # Créer une grille responsive
        cols_per_row = 3
        agent_items = list(agents.items())
        
        for i in range(0, len(agent_items), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, (agent_name, agent_config) in enumerate(agent_items[i:i+cols_per_row]):
                with cols[j]:
                    # Tuile carrée pour chaque agent
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #e0e0e0;
                            border-radius: 10px;
                            padding: 20px;
                            margin: 10px 0;
                            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            height: 300px;
                            overflow-y: auto;
                        ">
                            <h4 style="margin-top: 0; color: #2c3e50;">🤖 {agent_config.name}</h4>
                            <p style="color: #7f8c8d; font-size: 14px; margin: 5px 0;">{agent_config.role}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Informations détaillées
                        with st.expander("📋 Détails", expanded=False):
                            st.write(f"**Objectif :** {agent_config.goal}")
                            st.write(f"**Backstory :** {agent_config.backstory}")
                            st.write(f"**Outils :** {', '.join(agent_config.enabled_tools) if agent_config.enabled_tools else 'Aucun'}")
                            st.write(f"**Max Iterations :** {agent_config.max_iter}")
                            st.write(f"**Verbose :** {'Oui' if agent_config.verbose else 'Non'}")
                        
                        # Boutons d'action
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✏️ Modifier", key=f"edit_{agent_name}", type="secondary"):
                                st.session_state[f"editing_agent_{agent_name}"] = True
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Supprimer", key=f"delete_{agent_name}", type="secondary"):
                                if st.session_state.config_manager.delete_agent(agent_name):
                                    st.success(f"Agent '{agent_name}' supprimé !")
                                    st.rerun()
                                else:
                                    st.error("Erreur lors de la suppression")
        
        # Formulaire de modification d'agent
        for agent_name, agent_config in agents.items():
            if st.session_state.get(f"editing_agent_{agent_name}", False):
                st.markdown(f"### ✏️ Modification de l'agent : {agent_config.name}")
                
                with st.form(f"edit_agent_form_{agent_name}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_name = st.text_input("Nom de l'agent", value=agent_config.name, key=f"edit_name_{agent_name}")
                        edit_role = st.text_input("Rôle", value=agent_config.role, key=f"edit_role_{agent_name}")
                        edit_goal = st.text_area("Objectif", value=agent_config.goal, key=f"edit_goal_{agent_name}", height=100)
                    
                    with col2:
                        edit_backstory = st.text_area("Backstory", value=agent_config.backstory, key=f"edit_backstory_{agent_name}", height=100)
                        edit_max_iter = st.number_input("Max Iterations", value=agent_config.max_iter, min_value=1, max_value=10, key=f"edit_max_iter_{agent_name}")
                        edit_verbose = st.checkbox("Verbose", value=agent_config.verbose, key=f"edit_verbose_{agent_name}")
                    
                    # Configuration des outils pour cet agent
                    available_tools = st.session_state.config_manager.get_available_tools()
                    edit_enabled_tools = []
                    
                    st.write("**Outils disponibles :**")
                    for tool_name, tool_info in available_tools.items():
                        if st.checkbox(
                            f"{tool_info['name']} - {tool_info['description']}", 
                            value=tool_name in agent_config.enabled_tools,
                            key=f"edit_tool_{agent_name}_{tool_name}"
                        ):
                            edit_enabled_tools.append(tool_name)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.form_submit_button("💾 Sauvegarder", type="primary"):
                            # Mettre à jour la configuration
                            agent_config.name = edit_name
                            agent_config.role = edit_role
                            agent_config.goal = edit_goal
                            agent_config.backstory = edit_backstory
                            agent_config.verbose = edit_verbose
                            agent_config.max_iter = edit_max_iter
                            agent_config.enabled_tools = edit_enabled_tools
                            
                            st.session_state.config_manager.update_agent_config(agent_name, agent_config)
                            st.session_state[f"editing_agent_{agent_name}"] = False
                            st.success(f"Agent '{edit_name}' modifié avec succès !")
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state[f"editing_agent_{agent_name}"] = False
                            st.rerun()
                    
                    with col3:
                        if st.form_submit_button("🗑️ Supprimer"):
                            if st.session_state.config_manager.delete_agent(agent_name):
                                st.session_state[f"editing_agent_{agent_name}"] = False
                                st.success(f"Agent '{agent_name}' supprimé !")
                                st.rerun()
                            else:
                                st.error("Erreur lors de la suppression")
    else:
        st.info("Aucun agent configuré. Créez votre premier agent avec le bouton '➕ Créer un nouvel agent'")

with tab3:
    st.title("👥 Gestion des Crews")
    
    # Section de création de crew avec design en grille
    st.markdown("### ➕ Créer un nouveau crew")
    
    # Bouton de création dans un conteneur stylé
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Créer un nouveau crew", type="primary", use_container_width=True):
            st.session_state.show_new_crew_form = True
    
    if st.session_state.get('show_new_crew_form', False):
        st.markdown("### ➕ Créer un nouveau crew")
        
        with st.form("new_crew_form"):
            new_crew_name = st.text_input("Nom du crew", placeholder="ex: Mon Crew Marketing")
            new_crew_description = st.text_area("Description", placeholder="Décrivez le rôle de ce crew", height=100)
            
            # Sélection des agents
            available_agents = st.session_state.config_manager.get_all_agents()
            if available_agents:
                st.write("**Sélectionnez les agents pour ce crew :**")
                selected_agents = []
                for agent_name, agent_config in available_agents.items():
                    if st.checkbox(f"{agent_config.name} - {agent_config.role}", key=f"crew_agent_{agent_name}"):
                        selected_agents.append(agent_name)
            else:
                st.warning("Aucun agent disponible. Créez d'abord des agents.")
                selected_agents = []
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Créer le crew", type="primary"):
                    if new_crew_name and selected_agents:
                        try:
                            crew_name = st.session_state.crew_config_manager.create_new_crew(
                                name=new_crew_name,
                                description=new_crew_description,
                                selected_agents=selected_agents
                            )
                            st.success(f"Crew '{crew_name}' créé avec succès !")
                            st.session_state.show_new_crew_form = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur lors de la création : {e}")
                    else:
                        st.error("Veuillez remplir le nom et sélectionner au moins un agent")
            
            with col2:
                if st.form_submit_button("❌ Annuler"):
                    st.session_state.show_new_crew_form = False
                    st.rerun()
    
    # Affichage des crews existants en grille
    st.markdown("### 📋 Crews existants")
    crews = st.session_state.crew_config_manager.get_all_crews()
    
    if crews:
        # Créer une grille responsive
        cols_per_row = 2
        crew_items = list(crews.items())
        
        for i in range(0, len(crew_items), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, (crew_name, crew_config) in enumerate(crew_items[i:i+cols_per_row]):
                with cols[j]:
                    # Tuile carrée pour chaque crew
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #e0e0e0;
                            border-radius: 10px;
                            padding: 20px;
                            margin: 10px 0;
                            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            height: 250px;
                            overflow-y: auto;
                        ">
                            <h4 style="margin-top: 0; color: #1565c0;">👥 {crew_config.name}</h4>
                            <p style="color: #424242; font-size: 14px; margin: 5px 0;">{crew_config.description}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Informations détaillées
                        with st.expander("📋 Détails", expanded=False):
                            st.write(f"**Description :** {crew_config.description}")
                            st.write(f"**Agents :** {', '.join(crew_config.selected_agents)}")
                            st.write(f"**Type de processus :** {crew_config.process_type}")
                            st.info("💡 Le Meta Manager créera automatiquement les tâches selon votre problématique")
                        
                        # Boutons d'action
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("✏️ Modifier", key=f"edit_crew_{crew_name}", type="secondary"):
                                st.session_state[f"editing_crew_{crew_name}"] = True
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Supprimer", key=f"delete_crew_{crew_name}", type="secondary"):
                                if st.session_state.crew_config_manager.delete_crew(crew_name):
                                    st.success(f"Crew '{crew_name}' supprimé !")
                                    st.rerun()
                                else:
                                    st.error("Erreur lors de la suppression")
        
        # Formulaire de modification de crew
        for crew_name, crew_config in crews.items():
            if st.session_state.get(f"editing_crew_{crew_name}", False):
                st.markdown(f"### ✏️ Modification du crew : {crew_config.name}")
                
                with st.form(f"edit_crew_form_{crew_name}"):
                    edit_crew_name = st.text_input("Nom du crew", value=crew_config.name, key=f"edit_crew_name_{crew_name}")
                    edit_crew_description = st.text_area("Description", value=crew_config.description, key=f"edit_crew_description_{crew_name}", height=100)
                    
                    # Sélection des agents
                    available_agents = st.session_state.config_manager.get_all_agents()
                    if available_agents:
                        st.write("**Sélectionnez les agents pour ce crew :**")
                        edit_selected_agents = []
                        for agent_name, agent_config in available_agents.items():
                            if st.checkbox(f"{agent_config.name} - {agent_config.role}", 
                                         value=agent_name in crew_config.selected_agents,
                                         key=f"edit_crew_agent_{crew_name}_{agent_name}"):
                                edit_selected_agents.append(agent_name)
                    else:
                        st.warning("Aucun agent disponible.")
                        edit_selected_agents = []
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.form_submit_button("💾 Sauvegarder", type="primary"):
                            if edit_crew_name and edit_selected_agents:
                                # Mettre à jour la configuration
                                crew_config.name = edit_crew_name
                                crew_config.description = edit_crew_description
                                crew_config.selected_agents = edit_selected_agents
                                
                                st.session_state.crew_config_manager.update_crew_config(crew_name, crew_config)
                                st.session_state[f"editing_crew_{crew_name}"] = False
                                st.success(f"Crew '{edit_crew_name}' modifié avec succès !")
                                st.rerun()
                            else:
                                st.error("Veuillez remplir le nom et sélectionner au moins un agent")
                    
                    with col2:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state[f"editing_crew_{crew_name}"] = False
                            st.rerun()
                    
                    with col3:
                        if st.form_submit_button("🗑️ Supprimer"):
                            if st.session_state.crew_config_manager.delete_crew(crew_name):
                                st.session_state[f"editing_crew_{crew_name}"] = False
                                st.success(f"Crew '{crew_name}' supprimé !")
                                st.rerun()
                            else:
                                st.error("Erreur lors de la suppression")
    else:
        st.info("Aucun crew configuré. Créez votre premier crew avec le bouton '➕ Créer un nouveau crew'")

with tab4:
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
        
        # Synchroniser avec les PDFs existants dans le dossier knowledge
        knowledge_dir = "knowledge"
        if os.path.exists(knowledge_dir):
            existing_pdfs = []
            for file in os.listdir(knowledge_dir):
                if file.lower().endswith('.pdf'):
                    existing_pdfs.append(os.path.join(knowledge_dir, file))
            if existing_pdfs:
                st.session_state.uploaded_pdfs = existing_pdfs
                st.info(f"🔄 {len(existing_pdfs)} PDF(s) existant(s) détecté(s) dans le dossier knowledge/")
    
    if uploaded_files:
        # Sauvegarder les fichiers directement dans le dossier knowledge
        import os
        import shutil
        
        # Créer le dossier knowledge s'il n'existe pas
        knowledge_dir = "knowledge"
        os.makedirs(knowledge_dir, exist_ok=True)
        
        pdf_paths = []
        for uploaded_file in uploaded_files:
            # Sauvegarder directement dans le dossier knowledge avec le nom original
            knowledge_file_path = os.path.join(knowledge_dir, uploaded_file.name)
            try:
                # Écrire le contenu du fichier uploadé directement dans knowledge/
                with open(knowledge_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                pdf_paths.append(knowledge_file_path)
                print(f"📁 PDF sauvegardé dans knowledge/: {uploaded_file.name}")
            except Exception as e:
                print(f"⚠️ Erreur lors de la sauvegarde dans knowledge/: {e}")
        
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
    
    # Boutons de test et gestion
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualiser la détection"):
            # Re-scanner le dossier knowledge
            knowledge_dir = "knowledge"
            if os.path.exists(knowledge_dir):
                existing_pdfs = []
                for file in os.listdir(knowledge_dir):
                    if file.lower().endswith('.pdf'):
                        existing_pdfs.append(os.path.join(knowledge_dir, file))
                st.session_state.uploaded_pdfs = existing_pdfs
                st.success(f"🔄 {len(existing_pdfs)} PDF(s) détecté(s)")
            else:
                st.session_state.uploaded_pdfs = []
                st.info("📁 Dossier knowledge vide ou inexistant")
            st.rerun()
    
    with col2:
        if st.button("🧪 Test détection PDFs"):
            from src.tools import get_available_pdfs
            pdfs = get_available_pdfs()
            if pdfs:
                st.success(f"✅ {len(pdfs)} PDF(s) détecté(s) par les outils:")
                for pdf in pdfs:
                    st.write(f"   - {os.path.basename(pdf)}")
            else:
                st.warning("⚠️ Aucun PDF détecté par les outils")
    
    with col3:
        if st.session_state.uploaded_pdfs:
            if st.button("🗑️ Vider tous les PDFs"):
                # Supprimer les fichiers du dossier knowledge
                knowledge_dir = "knowledge"
                if os.path.exists(knowledge_dir):
                    import shutil
                    try:
                        shutil.rmtree(knowledge_dir)
                        os.makedirs(knowledge_dir, exist_ok=True)  # Recréer le dossier vide
                        st.write("📁 Dossier knowledge vidé")
                    except Exception as e:
                        st.error(f"Erreur lors de la suppression: {e}")
                
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
    
    # Afficher le contenu du dossier knowledge avec debug
    knowledge_dir = "knowledge"
    st.write("**📁 État du dossier knowledge :**")
    
    # Debug: Afficher le chemin absolu
    abs_knowledge_dir = os.path.abspath(knowledge_dir)
    st.write(f"**Chemin absolu :** `{abs_knowledge_dir}`")
    
    if os.path.exists(knowledge_dir):
        st.write("✅ Le dossier knowledge existe")
        knowledge_files = os.listdir(knowledge_dir)
        if knowledge_files:
            st.write(f"📄 {len(knowledge_files)} fichier(s) trouvé(s) :")
            for file in knowledge_files:
                file_path = os.path.join(knowledge_dir, file)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                st.write(f"   - {file} ({file_size} bytes)")
        else:
            st.write("⚠️ Le dossier knowledge est vide")
    else:
        st.write("❌ Le dossier knowledge n'existe pas")
        st.write("💡 Il sera créé automatiquement lors du prochain upload de PDF")

with tab5:
    st.title("🔧 Outils et Configuration Avancée")
    
    # Section de sauvegarde/chargement
    st.markdown("### 💾 Sauvegarde et Chargement")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Exporter configuration complète", type="primary"):
            # Exporter la configuration des agents
            agents_config = st.session_state.config_manager.export_config()
            # Exporter la configuration des crews
            crews_config = st.session_state.crew_config_manager.export_config()
            
            # Combiner les configurations
            full_config = {
                "agents": agents_config,
                "crews": crews_config,
                "version": "1.0"
            }
            
            st.download_button(
                label="Télécharger configuration.json",
                data=json.dumps(full_config, indent=2, ensure_ascii=False),
                file_name="crewai_configuration.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Importer configuration", type=['json'])
        if uploaded_file is not None:
            try:
                config = json.load(uploaded_file)
                
                # Importer la configuration des agents
                if "agents" in config:
                    st.session_state.config_manager.import_config(config["agents"])
                
                # Importer la configuration des crews
                if "crews" in config:
                    st.session_state.crew_config_manager.import_config(config["crews"])
                
                st.success("Configuration importée avec succès!")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'import: {e}")

    with col3:
        if st.button("🔄 Réinitialiser tout", type="secondary"):
            st.session_state.config_manager = AgentConfigManager()
            st.session_state.crew_config_manager = CrewConfigManager(st.session_state.config_manager)
            st.success("Configuration réinitialisée!")
            st.rerun()
    
    st.markdown("---")
    
    # Section de configuration des outils
    st.markdown("### 🔧 Configuration des Outils")
    
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

with tab6:
    st.title("📊 Outputs des Agents")
    
    # Initialiser la session state pour stocker les outputs des agents
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = {}
    
    if 'last_campaign_result' not in st.session_state:
        st.session_state.last_campaign_result = None
    
    # Section pour afficher les outputs de la dernière campagne
    st.markdown("### 🎯 Dernière campagne exécutée")
    
    if st.session_state.last_campaign_result:
        st.success("✅ Dernière campagne disponible")
        
        # Parser le résultat pour extraire les outputs par agent
        result_str = str(st.session_state.last_campaign_result)
        
        # Diviser le résultat en sections par agent avec un parsing amélioré
        agent_sections = parse_agent_outputs_improved(result_str)
        
        # Afficher les outputs par agent avec une interface améliorée
        if agent_sections:
            st.markdown("### 📋 Outputs par agent")
            
            # Créer des onglets pour chaque agent avec des icônes
            agent_tab_names = []
            for agent_name in agent_sections.keys():
                if 'meta' in agent_name.lower():
                    agent_tab_names.append(f"🧠 {agent_name}")
                elif 'clara' in agent_name.lower():
                    agent_tab_names.append(f"🔍 {agent_name}")
                elif 'julien' in agent_name.lower():
                    agent_tab_names.append(f"📊 {agent_name}")
                elif 'sophie' in agent_name.lower():
                    agent_tab_names.append(f"✍️ {agent_name}")
                else:
                    agent_tab_names.append(f"🤖 {agent_name}")
            
            agent_tabs = st.tabs(agent_tab_names)
            
            for i, (agent_name, content) in enumerate(agent_sections.items()):
                with agent_tabs[i]:
                    # En-tête de l'agent avec informations
                    col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
                    
                    with col_header1:
                        st.markdown(f"#### {agent_tab_names[i]}")
                        # Afficher le type de contenu détecté
                        content_type = detect_content_type(content)
                        st.caption(f"📄 Type de contenu: {content_type}")
                    
                    with col_header2:
                        # Statistiques du contenu
                        word_count = len(content.split())
                        char_count = len(content)
                        st.metric("Mots", word_count)
                    
                    with col_header3:
                        st.metric("Caractères", char_count)
                    
                    # Affichage du contenu avec formatage amélioré
                    st.markdown("---")
                    
                    # Afficher le contenu dans un conteneur stylé
                    with st.container():
                        if content_type == "Posts LinkedIn":
                            display_linkedin_posts(content)
                        elif content_type == "Posts Instagram":
                            display_instagram_posts(content)
                        elif content_type == "Plan stratégique":
                            display_strategic_plan(content)
                        elif content_type == "Analyse de données":
                            display_data_analysis(content)
                        else:
                            # Affichage par défaut avec formatage Markdown
                            st.markdown(content)
                    
                    # Boutons d'action améliorés
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📋 Copier", key=f"copy_{agent_name}", type="secondary"):
                            st.code(content, language="text")
                            st.success("✅ Contenu affiché ci-dessus - vous pouvez le copier !")
                    
                    with col2:
                        if st.button(f"📥 Télécharger", key=f"download_{agent_name}", type="secondary"):
                            file_extension = get_file_extension(content_type)
                            st.download_button(
                                label=f"Télécharger {file_extension}",
                                data=content,
                                file_name=f"output_{agent_name.lower().replace(' ', '_')}.{file_extension}",
                                mime="text/plain"
                            )
                    
                    with col3:
                        if st.button(f"💾 Sauvegarder", key=f"save_{agent_name}", type="primary"):
                            st.session_state.agent_outputs[agent_name] = content
                            st.success(f"✅ Output de {agent_name} sauvegardé !")
                            st.rerun()
                    
                    with col4:
                        if st.button(f"🔍 Analyser", key=f"analyze_{agent_name}", type="secondary"):
                            analyze_agent_output(agent_name, content)
        
        # Section pour les outputs sauvegardés
        if st.session_state.agent_outputs:
            st.markdown("---")
            st.markdown("### 💾 Outputs sauvegardés")
            
            # Afficher les outputs sauvegardés avec une interface améliorée
            for agent_name, content in st.session_state.agent_outputs.items():
                # En-tête de l'agent sauvegardé
                col_header1, col_header2, col_header3 = st.columns([2, 1, 1])
                
                with col_header1:
                    st.markdown(f"#### 💾 {agent_name}")
                    content_type = detect_content_type(content)
                    st.caption(f"📄 Type: {content_type} | 💾 Sauvegardé")
                
                with col_header2:
                    word_count = len(content.split())
                    st.metric("Mots", word_count)
                
                with col_header3:
                    char_count = len(content)
                    st.metric("Caractères", char_count)
                
                # Afficher le contenu dans un conteneur stylé
                with st.container():
                    st.markdown("---")
                    
                    if content_type == "Posts LinkedIn":
                        display_linkedin_posts(content)
                    elif content_type == "Posts Instagram":
                        display_instagram_posts(content)
                    elif content_type == "Plan stratégique":
                        display_strategic_plan(content)
                    elif content_type == "Analyse de données":
                        display_data_analysis(content)
                    else:
                        st.markdown(content)
                    
                    # Boutons d'action pour les outputs sauvegardés
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📋 Copier", key=f"copy_saved_{agent_name}", type="secondary"):
                            st.code(content, language="text")
                            st.success("✅ Contenu affiché ci-dessus !")
                    
                    with col2:
                        if st.button(f"📥 Télécharger", key=f"download_saved_{agent_name}", type="secondary"):
                            file_extension = get_file_extension(content_type)
                            st.download_button(
                                label=f"Télécharger {file_extension}",
                                data=content,
                                file_name=f"saved_{agent_name.lower().replace(' ', '_')}.{file_extension}",
                                mime="text/plain"
                            )
                    
                    with col3:
                        if st.button(f"🔍 Analyser", key=f"analyze_saved_{agent_name}", type="secondary"):
                            analyze_agent_output(agent_name, content)
                    
                    with col4:
                        if st.button(f"🗑️ Supprimer", key=f"delete_saved_{agent_name}", type="secondary"):
                            del st.session_state.agent_outputs[agent_name]
                            st.success(f"✅ Output de {agent_name} supprimé !")
                            st.rerun()
            
            # Bouton pour vider tous les outputs sauvegardés
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Vider tous les outputs sauvegardés", type="secondary"):
                    st.session_state.agent_outputs = {}
                    st.success("✅ Tous les outputs sauvegardés ont été supprimés !")
                    st.rerun()
            
            with col2:
                if st.button("📊 Statistiques des outputs", type="secondary"):
                    show_outputs_statistics()
    
    else:
        st.info("💡 Aucune campagne exécutée récemment. Lancez une campagne dans l'onglet '🎯 Campagne' pour voir les outputs des agents.")
    
    # Section pour analyser les outputs
    st.markdown("---")
    st.markdown("### 🔍 Analyse des outputs")
    
    if st.session_state.agent_outputs:
        # Statistiques des outputs
        st.markdown("#### 📊 Statistiques")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Agents avec outputs", len(st.session_state.agent_outputs))
        
        with col2:
            total_chars = sum(len(content) for content in st.session_state.agent_outputs.values())
            st.metric("Total de caractères", f"{total_chars:,}")
        
        with col3:
            avg_chars = total_chars // len(st.session_state.agent_outputs) if st.session_state.agent_outputs else 0
            st.metric("Moyenne par agent", f"{avg_chars:,}")
        
        # Recherche dans les outputs
        st.markdown("#### 🔍 Recherche dans les outputs")
        search_term = st.text_input("Rechercher un terme dans les outputs", placeholder="Ex: LinkedIn, stratégie, RSE...")
        
        if search_term:
            matching_agents = []
            for agent_name, content in st.session_state.agent_outputs.items():
                if search_term.lower() in content.lower():
                    matching_agents.append((agent_name, content))
            
            if matching_agents:
                st.success(f"✅ {len(matching_agents)} agent(s) trouvé(s) avec le terme '{search_term}'")
                
                for agent_name, content in matching_agents:
                    with st.expander(f"🤖 {agent_name} - Résultats pour '{search_term}'", expanded=False):
                        # Mettre en évidence le terme recherché
                        highlighted_content = content.replace(
                            search_term, 
                            f"**{search_term}**"
                        )
                        st.markdown(highlighted_content)
            else:
                st.warning(f"❌ Aucun agent trouvé avec le terme '{search_term}'")
    
    # Section pour exporter tous les outputs
    st.markdown("---")
    st.markdown("### 📤 Export des outputs")
    
    if st.session_state.agent_outputs:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Exporter tous les outputs", type="primary"):
                # Créer un rapport complet
                export_content = []
                export_content.append("=== OUTPUTS DES AGENTS ===\n")
                
                for agent_name, content in st.session_state.agent_outputs.items():
                    export_content.append(f"--- {agent_name} ---")
                    export_content.append(content)
                    export_content.append("\n")
                
                export_text = "\n".join(export_content)
                st.download_button(
                    label="Télécharger tous les outputs",
                    data=export_text,
                    file_name="outputs_agents_complet.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📊 Exporter en JSON", type="secondary"):
                import json
                json_data = {
                    "timestamp": str(pd.Timestamp.now()),
                    "agent_outputs": st.session_state.agent_outputs,
                    "total_agents": len(st.session_state.agent_outputs)
                }
                
                st.download_button(
                    label="Télécharger en JSON",
                    data=json.dumps(json_data, indent=2, ensure_ascii=False),
                    file_name="outputs_agents.json",
                    mime="application/json"
                )
    else:
        st.info("💡 Aucun output sauvegardé. Sauvegardez des outputs d'agents pour pouvoir les exporter.")