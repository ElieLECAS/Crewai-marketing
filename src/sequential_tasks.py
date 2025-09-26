from crewai import Task, Crew, Process
from textwrap import dedent
from typing import Dict, List, Optional
import os
import re
import json
from .agents import create_agent_from_config
from .agent_config import AgentConfigManager

def estimate_tokens(text: str) -> int:
    """Estime le nombre de tokens d'un texte (approximation: 1 token ≈ 4 caractères)"""
    return len(text) // 4

def check_token_limit(text: str, limit: int = 50000) -> bool:
    """Vérifie si un texte respecte la limite de tokens"""
    return estimate_tokens(text) <= limit


class SequentialTaskManager:
    """Gestionnaire de tâches séquentielles avec transmission des résultats"""
    
    def __init__(self, config_manager: AgentConfigManager):
        self.config_manager = config_manager
    
    def parse_recommended_order(self, meta_manager_result: str, available_agents: List[str]) -> List[str]:
        """Parse le résultat du Meta Manager pour extraire l'ordre d'exécution recommandé"""
        # Mappage entre les noms utilisés dans le résultat et les noms techniques des agents
        agent_name_mapping = {
            "julien": "julien_analyste_strategique",
            "analyste de contexte": "julien_analyste_strategique", 
            "clara": "clara_detective_digitale",
            "chercheuse web": "clara_detective_digitale",
            "sophie": "sophie_plume_solidaire",
            "rédactrice linkedin": "sophie_plume_solidaire",
            "plume solidaire": "sophie_plume_solidaire"
        }
        
        # Chercher la section "ORDRE D'EXÉCUTION RECOMMANDÉ"
        order_section_match = re.search(r'##\s*ORDRE\s*D.*?EXÉCUTION\s*RECOMMANDÉ\s*[:\s]*(.+?)(?=##|\Z)', 
                                       meta_manager_result, re.DOTALL | re.IGNORECASE)
        
        if not order_section_match:
            print("⚠️ Aucun ordre d'exécution trouvé dans les recommandations du Meta Manager")
            return available_agents  # Retourner l'ordre par défaut
        
        order_text = order_section_match.group(1)
        
        # Extraire les mentions d'agents avec des patterns flexibles
        recommended_order = []
        
        # Pattern pour détecter les mentions d'agents avec leur position
        patterns = [
            r'(\d+)\.\s*\*\*([^*]+(?:\([^)]+\))?)',  # Format: 1. **Agent (Role)**
            r'(\d+)\.\s*([^:\n]+)',  # Format: 1. Agent
            r'(\d+)\.?\s*(?:\*\*)?([^*\n:]+?)(?:\*\*)?(?:\s*:|$)',  # Format plus flexible
        ]
        
        positions_found = {}
        
        for pattern in patterns:
            matches = re.finditer(pattern, order_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                position = int(match.group(1))
                agent_mention = match.group(2).strip().lower()
                
                # Nettoyer la mention de l'agent
                agent_mention = re.sub(r'[*():]', '', agent_mention).strip()
                
                # Chercher quel agent technique cela correspond
                matched_agent = None
                for name_variant, technical_name in agent_name_mapping.items():
                    if name_variant.lower() in agent_mention or agent_mention in name_variant.lower():
                        matched_agent = technical_name
                        break
                
                if matched_agent and matched_agent in available_agents:
                    positions_found[position] = matched_agent
        
        # Construire l'ordre recommandé
        for position in sorted(positions_found.keys()):
            if positions_found[position] not in recommended_order:
                recommended_order.append(positions_found[position])
        
        # Ajouter les agents manquants à la fin
        for agent in available_agents:
            if agent not in recommended_order:
                recommended_order.append(agent)
        
        print(f"🔄 Ordre d'exécution détecté par le Meta Manager: {recommended_order}")
        return recommended_order
    
    def create_meta_manager_task(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None) -> Task:
        """Crée la tâche principale du Meta Agent Manager qui génère un plan JSON structuré"""
        meta_agent = create_agent_from_config("meta_manager_agent", self.config_manager)
        
        # Construire la liste des agents disponibles dynamiquement
        if available_agents is None:
            # Tous les agents sauf le méta
            available_agents = [name for name in self.config_manager.get_all_agents().keys() if name != "meta_manager_agent"]
        
        # Vérifier les PDFs disponibles
        from .tools import get_available_pdfs
        pdf_files = get_available_pdfs()
        pdf_info = ""
        if pdf_files:
            pdf_info = f"""
            
            📚 SOURCES DE CONNAISSANCES DISPONIBLES :
            {len(pdf_files)} fichier(s) PDF disponible(s) dans le dossier knowledge/ :
            {chr(10).join([f"- {os.path.basename(pdf)}" for pdf in pdf_files])}
            
            Les agents avec les outils PDF peuvent utiliser ces documents pour enrichir leurs réponses.
            """
        else:
            pdf_info = """
            
            📚 SOURCES DE CONNAISSANCES :
            Aucun fichier PDF disponible actuellement.
            Les agents avec les outils PDF ne pourront pas les utiliser.
            """
        
        # Récupérer les informations complètes des agents
        agents_info = []
        for agent_name in available_agents:
            agent_config = self.config_manager.get_agent_config(agent_name)
            if agent_config:
                # Récupérer les outils disponibles
                available_tools = self.config_manager.get_available_tools()
                agent_tools = []
                for tool_name in agent_config.enabled_tools:
                    if tool_name in available_tools:
                        agent_tools.append(available_tools[tool_name]["name"])
                
                tools_text = ", ".join(agent_tools) if agent_tools else "Aucun outil"
                
                agents_info.append({
                    "name": agent_name,
                    "role": agent_config.role,
                    "goal": agent_config.goal,
                    "tools": agent_tools,
                    "max_iter": agent_config.max_iter
                })
        
        agents_list = "\n".join([f"- {agent['name']} ({agent['role']}) - Outils: {', '.join(agent['tools']) if agent['tools'] else 'Aucun'}" for agent in agents_info])
        
        # Contexte entreprise simplifié (limité à 300 caractères)
        company_context_short = company_context[:300] + "..." if len(company_context) > 300 else company_context
        
        # Problématique simplifiée (limité à 500 caractères)
        problem_short = problem_statement[:500] + "..." if len(problem_statement) > 500 else problem_statement
        
        description = dedent(f"""
        Tu es le Meta Agent Manager. Analyse cette problématique et crée un plan JSON.
        
        PROBLÉMATIQUE : {problem_short}
        
        CONTEXTE : {company_context_short if company_context else "Aucun contexte"}{pdf_info}
        
        AGENTS : {agents_list}
        
        MISSION :
        1. Analyser la problématique et identifier les enjeux clés
        2. Déterminer l'ordre optimal d'exécution des agents
        3. Créer des tâches spécifiques pour chaque agent
        4. Générer un plan JSON structuré
        
        FORMAT JSON OBLIGATOIRE :
        {{
            "execution_order": ["agent1", "agent2", "agent3"],
            "problem_analysis": {{
                "main_objective": "Objectif principal",
                "key_challenges": ["Défi 1", "Défi 2"],
                "target_audience": "Audience cible"
            }},
            "tasks": {{
                "nom_agent_technique": {{
                    "description": "Tâche spécifique pour cet agent",
                    "expected_output": "Format du livrable attendu",
                    "dependencies": ["agent_précédent"] ou [],
                    "tools_to_use": ["outil1", "outil2"],
                    "priority": 1
                }}
            }}
        }}
        
        RÈGLES :
        - Chaque tâche adaptée aux compétences de l'agent
        - JSON valide et parsable
        - Utilise les noms techniques des agents
        - Chaque agent exécute UNIQUEMENT sa tâche assignée
        
        LIVRABLE : Plan JSON structuré et exécutable.
        """).strip()
        
        # Vérifier la limite de tokens pour la tâche Meta Manager
        if not check_token_limit(description, 15000):  # Limite pour le Meta Manager
            print("⚠️ Tâche Meta Manager dépasse la limite de tokens, réduction supplémentaire...")
            # Réduire encore plus si nécessaire
            problem_short = problem_statement[:300] + "..."
            company_context_short = company_context[:200] + "..." if company_context else ""
            
            description = dedent(f"""
            Tu es le Meta Agent Manager. Crée un plan JSON.
            
            PROBLÉMATIQUE : {problem_short}
            
            CONTEXTE : {company_context_short if company_context else "Aucun contexte"}
            
            AGENTS : {agents_list}
            
            MISSION : Créer un plan JSON avec tâches pour chaque agent.
            
            FORMAT JSON :
            {{
                "execution_order": ["agent1", "agent2", "agent3"],
                "tasks": {{
                    "nom_agent": {{
                        "description": "Tâche pour cet agent",
                        "expected_output": "Livrable attendu",
                        "priority": 1
                    }}
                }}
            }}
            
            LIVRABLE : Plan JSON structuré.
            """).strip()
        
        return Task(
            description=description,
            agent=meta_agent,
            expected_output="Plan JSON structuré et valide pour créer les Task CrewAI dynamiquement.",
        )
    
    def create_agent_task_from_plan(self, agent_name: str, task_info: dict, problem_statement: str, company_context: str = "", pdf_paths: List[str] = None) -> Task:
        """Crée une tâche spécifique pour un agent basée sur le plan du Meta Manager"""
        agent = create_agent_from_config(agent_name, self.config_manager, pdf_paths)
        agent_config = self.config_manager.get_agent_config(agent_name)
        
        if not agent_config:
            raise ValueError(f"Configuration non trouvée pour l'agent: {agent_name}")
        
        # Vérifier les PDFs disponibles pour cet agent
        from .tools import get_available_pdfs
        pdf_files = get_available_pdfs()
        pdf_context = ""
        if pdf_files and any(tool in agent_config.enabled_tools for tool in ["pdf_search", "rag_tool"]):
            pdf_context = f"""
            
            📚 SOURCES PDF DISPONIBLES :
            Tu as accès à {len(pdf_files)} fichier(s) PDF via tes outils PDF :
            {chr(10).join([f"- {os.path.basename(pdf)}" for pdf in pdf_files])}
            
            INSTRUCTIONS IMPORTANTES POUR L'UTILISATION DES OUTILS PDF :
            - Utilise l'outil "pdf_search" avec UNE SEULE chaîne de caractères comme query
            - Exemple correct : pdf_search("Gamme Lumeal")
            - Exemple incorrect : pdf_search({{"query": "Gamme Lumeal", "pdf": "fichier.pdf"}})
            - L'outil recherche automatiquement dans tous les PDFs disponibles
            - Utilise tes outils PDF pour enrichir tes réponses avec le contenu de ces documents
            """
        elif any(tool in agent_config.enabled_tools for tool in ["pdf_search", "rag_tool"]):
            pdf_context = """
            
            📚 SOURCES PDF :
            Aucun fichier PDF n'est disponible actuellement.
            Tes outils PDF ne pourront pas être utilisés.
            """
        
        # Construire la description enrichie avec les informations du plan
        enriched_description = self._build_enriched_task_description(
            task_info, problem_statement, company_context, pdf_context, agent_config
        )
        
        return Task(
            description=enriched_description,
            expected_output=task_info["expected_output"],
            agent=agent
        )
    
    def _build_enriched_task_description(self, task_info: dict, problem_statement: str, 
                                        company_context: str, pdf_context: str, agent_config) -> str:
        """Construit une description de tâche enrichie avec les informations du plan"""
        
        # Dépendances spécifiques (simplifiées)
        dependencies_info = ""
        if task_info.get("dependencies"):
            dependencies_info = f"""
            
            DÉPENDANCES : Cette tâche dépend des résultats de : {', '.join(task_info['dependencies'])}
            """
        
        # Outils recommandés (simplifiés)
        tools_info = ""
        if task_info.get("tools_to_use"):
            tools_info = f"""
            
            OUTILS RECOMMANDÉS : {', '.join(task_info['tools_to_use'])}
            """
        
        # Contexte entreprise simplifié (limité à 200 caractères)
        company_context_short = company_context[:200] + "..." if len(company_context) > 200 else company_context
        
        # Problématique simplifiée (limité à 300 caractères)
        problem_short = problem_statement[:300] + "..." if len(problem_statement) > 300 else problem_statement
        
        # Description de tâche simplifiée (limité à 500 caractères)
        task_description = task_info['description'][:500] + "..." if len(task_info['description']) > 500 else task_info['description']
        
        # Expected output simplifié (limité à 200 caractères)
        expected_output = task_info['expected_output'][:200] + "..." if len(task_info['expected_output']) > 200 else task_info['expected_output']
        
        description = dedent(f"""
        Tu es {agent_config.name}, {agent_config.role}.
        
        TÂCHE : {task_description}
        
        PROBLÉMATIQUE : {problem_short}
        
        {f"CONTEXTE : {company_context_short}" if company_context else ""}
        {pdf_context}
        {dependencies_info}
        {tools_info}
        
        INSTRUCTIONS :
        - Exécute UNIQUEMENT cette tâche assignée
        - Respecte le format de livrable demandé
        - Utilise tes outils selon tes besoins
        
        LIVRABLE : {expected_output}
        """).strip()
        
        # Vérifier la limite de tokens
        if not check_token_limit(description, 10000):  # Limite plus stricte pour les tâches individuelles
            print(f"⚠️ Tâche pour {agent_config.name} dépasse la limite de tokens, réduction supplémentaire...")
            # Réduire encore plus si nécessaire
            task_description = task_info['description'][:200] + "..."
            problem_short = problem_statement[:150] + "..."
            company_context_short = company_context[:100] + "..." if company_context else ""
            
            description = dedent(f"""
            Tu es {agent_config.name}, {agent_config.role}.
            
            TÂCHE : {task_description}
            
            PROBLÉMATIQUE : {problem_short}
            
            {f"CONTEXTE : {company_context_short}" if company_context else ""}
            
            INSTRUCTIONS : Exécute cette tâche selon tes compétences.
            
            LIVRABLE : {expected_output}
            """).strip()
        
        return description
    
    
    def create_sequential_tasks(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None) -> List[Task]:
        """Crée un ensemble de tâches séquentielles avec transmission des résultats via le système de context"""
        tasks = []
        
        # Utiliser les agents par défaut si aucun n'est fourni
        if available_agents is None:
            available_agents = [name for name in self.config_manager.get_all_agents().keys() if name != "meta_manager_agent"]
        
        # Tâche 1: Meta Manager - Analyse et délégation (avec choix de l'ordre)
        meta_task = self.create_meta_manager_task(problem_statement, company_context, available_agents)
        tasks.append(meta_task)
        
        # NOTE IMPORTANTE : L'ordre dans cette liste statique ne sera PAS respecté !
        # CrewAI exécute les agents dans l'ordre des tâches, pas selon les recommandations du Meta Manager
        # Pour résoudre ce problème, il faut créer un système de parsing des résultats du Meta Manager
        # et réorganiser dynamiquement l'ordre d'exécution
        
        # Tâches pour chaque agent du crew dans l'ordre choisi par le Meta Manager
        # Le Meta Manager décidera de l'ordre optimal dans sa tâche
        previous_tasks = [meta_task]  # Tous les agents reçoivent le contexte du Meta Manager
        
        for agent_name in available_agents:
            # Vérifier que l'agent existe
            if self.config_manager.get_agent_config(agent_name):
                agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                agent_task.context = previous_tasks.copy()  # L'agent reçoit le contexte de tous les agents précédents
                tasks.append(agent_task)
                previous_tasks.append(agent_task)  # Ajouter cette tâche au contexte pour les suivantes
        
        return tasks
    
    def create_ordered_sequential_tasks(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None, meta_manager_result: str = None) -> List[Task]:
        """Crée des tâches séquentielles dans l'ordre recommandé par le Meta Manager"""
        tasks = []
        
        # Utiliser les agents par défaut si aucun n'est fourni
        if available_agents is None:
            available_agents = [name for name in self.config_manager.get_all_agents().keys() if name != "meta_manager_agent"]
        
        # Si on a le résultat du Meta Manager, parser le plan JSON
        if meta_manager_result:
            try:
                # Extraire le JSON du résultat
                json_match = re.search(r'\{.*\}', meta_manager_result, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group(0))
                    ordered_agents = plan.get("execution_order", available_agents)
                    
                    # Créer les tâches selon le plan JSON SANS contexte pour éviter les limites de tokens
                    for agent_name in ordered_agents:
                        if agent_name in plan.get("tasks", {}):
                            task_info = plan["tasks"][agent_name]
                            
                            # Créer la tâche spécifique SANS contexte pour éviter les limites de tokens
                            agent_task = self.create_agent_task_from_plan(
                                agent_name, task_info, problem_statement, company_context
                            )
                            # Ne pas ajouter de contexte pour éviter les limites de tokens
                            agent_task.context = []
                            tasks.append(agent_task)
                else:
                    # Fallback vers l'ancien système
                    ordered_agents = self.parse_recommended_order(meta_manager_result, available_agents)
                    for agent_name in ordered_agents:
                        if self.config_manager.get_agent_config(agent_name):
                            agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                            # Ne pas ajouter de contexte pour éviter les limites de tokens
                            agent_task.context = []
                            tasks.append(agent_task)
            except Exception as e:
                print(f"⚠️ Erreur parsing plan Meta Manager: {e}")
                # Fallback vers l'ancien système
                ordered_agents = self.parse_recommended_order(meta_manager_result, available_agents)
        for agent_name in ordered_agents:
                    if self.config_manager.get_agent_config(agent_name):
                        agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                        # Ne pas ajouter de contexte pour éviter les limites de tokens
                        agent_task.context = []
                        tasks.append(agent_task)
        else:
            # Pas de résultat Meta Manager, utiliser l'ordre par défaut
            for agent_name in available_agents:
                if self.config_manager.get_agent_config(agent_name):
                    agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                    # Ne pas ajouter de contexte pour éviter les limites de tokens
                    agent_task.context = []
                    tasks.append(agent_task)
        
        return tasks
    
    def create_agent_task(self, agent_name: str, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche générique pour un agent (méthode de fallback)"""
        agent = create_agent_from_config(agent_name, self.config_manager)
        agent_config = self.config_manager.get_agent_config(agent_name)
        
        if not agent_config:
            raise ValueError(f"Configuration non trouvée pour l'agent: {agent_name}")
        
        # Contexte entreprise simplifié (limité à 100 caractères)
        company_context_short = company_context[:100] + "..." if len(company_context) > 100 else company_context
        
        # Problématique simplifiée (limité à 200 caractères)
        problem_short = problem_statement[:200] + "..." if len(problem_statement) > 200 else problem_statement
        
        return Task(
            description=dedent(f"""
            Tu es {agent_config.name}, {agent_config.role}.
            
            PROBLÉMATIQUE : {problem_short}
            
            {f"CONTEXTE : {company_context_short}" if company_context else ""}
            
            MISSION : Exécute ta tâche selon tes compétences.
            
            LIVRABLE : Résultat conforme à ton rôle.
            """).strip(),
            agent=agent,
            expected_output="Résultat conforme au rôle de l'agent.",
        )
    
    def create_meta_manager_with_json_plan(self, problem_statement: str, company_context: str = "", available_agents: List[str] = None) -> Task:
        """Crée la tâche du Meta Manager qui génère un plan JSON structuré"""
        meta_agent = create_agent_from_config("meta_manager_agent", self.config_manager)
        
        if available_agents is None:
            available_agents = [name for name in self.config_manager.get_all_agents().keys() if name != "meta_manager_agent"]
        
        # Informations sur les agents disponibles
        agents_info = []
        for agent_name in available_agents:
            agent_config = self.config_manager.get_agent_config(agent_name)
            if agent_config:
                available_tools = self.config_manager.get_available_tools()
                agent_tools = []
                for tool_name in agent_config.enabled_tools:
                    if tool_name in available_tools:
                        agent_tools.append(available_tools[tool_name]["name"])
                
                agents_info.append({
                    "name": agent_name,
                    "role": agent_config.role,
                    "goal": agent_config.goal,
                    "tools": agent_tools,
                    "max_iter": agent_config.max_iter
                })
        
        # Vérifier les PDFs disponibles
        from .tools import get_available_pdfs
        pdf_files = get_available_pdfs()
        pdf_context = ""
        if pdf_files:
            pdf_context = f"""
        
        📚 SOURCES DE CONNAISSANCES DISPONIBLES :
        {len(pdf_files)} fichier(s) PDF disponible(s) dans le dossier knowledge/ :
        {chr(10).join([f"- {os.path.basename(pdf)}" for pdf in pdf_files])}
        Les agents avec outils PDF peuvent utiliser ces documents pour enrichir leurs réponses."""
        
        return Task(
            description=dedent(f"""
            Tu es le Meta Agent Manager. Tu dois analyser cette problématique et créer un plan JSON structuré 
            pour orchestrer une équipe d'agents spécialisés.
            
            PROBLÉMATIQUE À RÉSOUDRE :
            {problem_statement}
            
            CONTEXTE ENTREPRISE :
            {company_context if company_context else "Aucun contexte spécifique fourni"}{pdf_context}
            
            AGENTS DISPONIBLES DANS TON CREW :
            {chr(10).join([f"- {agent['name']} ({agent['role']}) - Outils: {', '.join(agent['tools']) if agent['tools'] else 'Aucun'}" for agent in agents_info])}
            
            MISSION CRITIQUE :
            1. **Analyser en profondeur** la problématique et identifier les enjeux clés
            2. **Déterminer l'ordre optimal** d'exécution des agents selon la logique métier
            3. **Choisir le type de processus** : séquentiel (une tâche après l'autre) ou asynchrone (en parallèle)
            4. **Créer des tâches spécifiques** pour chaque agent avec des instructions détaillées
            5. **Définir les dépendances** entre les tâches et le contexte nécessaire
            6. **Générer un plan JSON** structuré et exécutable
            
            CHOIX DU PROCESSUS D'EXÉCUTION :
            - **SÉQUENTIEL** : Utilise quand les tâches dépendent les unes des autres (ex: recherche → analyse → rédaction)
            - **ASYNCHRONE** : Utilise quand les tâches peuvent être faites en parallèle (ex: plusieurs recherches indépendantes)
            
            FORMAT DE SORTIE OBLIGATOIRE (JSON valide) :
            {{
                "execution_type": "sequential" ou "async",
                "execution_order": ["agent1", "agent2", "agent3"],
                "problem_analysis": {{
                    "main_objective": "Objectif principal clairement défini",
                    "key_challenges": ["Défi 1", "Défi 2", "Défi 3"],
                    "target_audience": "Audience cible identifiée",
                    "execution_rationale": "Pourquoi ce type d'exécution (sequential/async)"
                }},
                "tasks": {{
                    "nom_agent_technique": {{
                        "description": "Description détaillée de la tâche spécifique à cet agent, adaptée à ses compétences et outils.",
                        "expected_output": "Format et contenu exact du livrable attendu, avec structure claire.",
                        "dependencies": ["agent_précédent"] ou [],
                        "tools_to_use": ["outil1", "outil2"],
                        "context_needed": "Description du contexte nécessaire des agents précédents",
                        "priority": 1,
                        "estimated_duration": "X-Y minutes",
                        "can_run_parallel": true ou false
                    }}
                }},
                "crew_configuration": {{
                    "process_type": "sequential" ou "async",
                    "total_estimated_duration": "X-Y minutes",
                    "success_criteria": "Critères de succès clairs et mesurables",
                    "coordination_strategy": "Comment les agents se coordonnent (si async)"
                }}
            }}
            
            RÈGLES IMPORTANTES :
            - execution_type et process_type doivent être cohérents
            - Si "async", assure-toi que les tâches peuvent vraiment être parallélisées
            - Si "sequential", respecte l'ordre logique des dépendances
            - Chaque tâche doit être spécifiquement adaptée aux compétences de l'agent assigné
            - Le JSON doit être valide et parsable
            - Utilise les noms techniques des agents (ex: "clara_detective_digitale")
            
            LIVRABLE :
            Plan JSON structuré et exécutable pour orchestrer l'équipe d'agents avec le bon type d'exécution.
            """).strip(),
            agent=meta_agent,
            expected_output="Plan JSON structuré et valide pour créer les Task CrewAI dynamiquement avec choix du processus d'exécution."
        )
    
    def parse_json_plan_and_create_tasks(self, json_plan: str, problem_statement: str, company_context: str = "", pdf_paths: List[str] = None) -> tuple[List[Task], str]:
        """Parse le plan JSON du Meta Manager et crée les vraies Task CrewAI
        
        Returns:
            tuple: (tasks, process_type) où process_type est "sequential" ou "async"
        """
        
        # Extraire le JSON du résultat (gérer les cas où il y a du texte avant/après)
        json_match = re.search(r'\{.*\}', json_plan, re.DOTALL)
        if not json_match:
            raise ValueError("❌ Aucun plan JSON valide trouvé dans le résultat du Meta Manager")
        
        try:
            plan = json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Erreur de parsing JSON : {e}")
        
        # Valider la structure du plan
        required_keys = ["execution_order", "tasks", "crew_configuration"]
        for key in required_keys:
            if key not in plan:
                raise ValueError(f"❌ Clé manquante dans le plan : {key}")
        
        # Déterminer le type de processus
        process_type = plan.get("execution_type", "sequential")
        if process_type not in ["sequential", "async"]:
            print(f"⚠️ Type d'exécution non reconnu '{process_type}', utilisation de 'sequential'")
            process_type = "sequential"
        
        tasks = []
        previous_tasks = []
        
        print(f"🔄 Création des tâches selon l'ordre : {plan['execution_order']}")
        print(f"⚙️ Type d'exécution choisi par le Meta Manager : {process_type}")
        
        if process_type == "sequential":
            # Exécution séquentielle : chaque tâche dépend des précédentes
            for agent_name in plan["execution_order"]:
                if agent_name not in plan["tasks"]:
                    print(f"⚠️ Aucune tâche définie pour l'agent {agent_name}")
                    continue
                
                task = self._create_single_task(agent_name, plan["tasks"][agent_name], 
                                               problem_statement, company_context, 
                                               pdf_paths, previous_tasks)
                if task:
                    tasks.append(task)
                    previous_tasks.append(task)
        else:
            # Exécution asynchrone : créer les tâches avec dépendances définies
            for agent_name in plan["execution_order"]:
                if agent_name not in plan["tasks"]:
                    print(f"⚠️ Aucune tâche définie pour l'agent {agent_name}")
                    continue
                
                task_info = plan["tasks"][agent_name]
                
                # Pour l'async, construire le contexte basé sur les dépendances explicites
                dependency_tasks = []
                if task_info.get("dependencies"):
                    for dep_agent in task_info["dependencies"]:
                        # Trouver la tâche correspondante
                        for existing_task in tasks:
                            if existing_task.agent.role and dep_agent in existing_task.agent.role.lower():
                                dependency_tasks.append(existing_task)
                                break
                
                task = self._create_single_task(agent_name, task_info, 
                                               problem_statement, company_context, 
                                               pdf_paths, dependency_tasks)
                if task:
                    tasks.append(task)
        
        print(f"🎯 {len(tasks)} tâche(s) créée(s) avec succès en mode {process_type}")
        return tasks, process_type
    
    def _create_single_task(self, agent_name: str, task_info: dict, problem_statement: str, 
                           company_context: str, pdf_paths: List[str], context_tasks: List[Task]) -> Optional[Task]:
        """Crée une seule tâche pour un agent donné"""
        
        # Vérifier que l'agent existe dans la configuration
        if not self.config_manager.get_agent_config(agent_name):
            print(f"⚠️ Agent {agent_name} non trouvé dans la configuration")
            return None
        
        try:
            # Utiliser la nouvelle méthode qui crée des tâches spécifiques
            task = self.create_agent_task_from_plan(
                agent_name, task_info, problem_statement, company_context, pdf_paths
            )
            
            # Ajouter le contexte des tâches dépendantes
            if context_tasks:
                task.context = context_tasks.copy()
            
            print(f"✅ Tâche créée pour {agent_name} (priorité {task_info.get('priority', 'N/A')}, parallèle: {task_info.get('can_run_parallel', 'N/A')})")
            return task
            
        except Exception as e:
            print(f"❌ Erreur création tâche pour {agent_name}: {e}")
            return None
    
    
    def create_dynamic_crew_with_json_plan(self, problem_statement: str, company_context: str = "", 
                                          pdf_paths: List[str] = None, selected_agents: List[str] = None) -> Crew:
        """Crée un crew complet où le Meta Manager génère un plan JSON pour créer les vraies Task"""
        
        if selected_agents is None:
            selected_agents = [name for name in self.config_manager.get_all_agents().keys() if name != "meta_manager_agent"]
        
        # 1. Créer et exécuter le Meta Manager
        print("🧠 Phase 1: Exécution du Meta Manager...")
        meta_task = self.create_meta_manager_with_json_plan(problem_statement, company_context, selected_agents)
        
        meta_agent = create_agent_from_config("meta_manager_agent", self.config_manager, pdf_paths)
        meta_crew = Crew(
            agents=[meta_agent],
            tasks=[meta_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Exécuter le Meta Manager
        meta_result = meta_crew.kickoff()
        print("✅ Meta Manager terminé")
        
        # 2. Parser le résultat et créer les vraies Task
        print("🔄 Phase 2: Création des tâches dynamiques...")
        dynamic_tasks, process_type = self.parse_json_plan_and_create_tasks(
            meta_result, problem_statement, company_context, pdf_paths
        )
        
        if not dynamic_tasks:
            raise ValueError("❌ Aucune tâche créée - vérifiez le plan du Meta Manager")
        
        # 3. Créer les agents pour les tâches dynamiques
        dynamic_agents = []
        for task in dynamic_tasks:
            # L'agent est déjà créé dans la tâche
            dynamic_agents.append(task.agent)
        
        # 4. Déterminer le type de processus CrewAI
        crew_process = Process.sequential
        if process_type == "async":
            # CrewAI n'a pas de Process.async, on utilise hierarchical pour permettre plus de parallélisme
            crew_process = Process.hierarchical
            print("📋 Utilisation du processus hierarchical (le plus proche de l'asynchrone)")
        else:
            print("📋 Utilisation du processus sequential")
        
        # 5. Créer le crew final avec les vraies Task
        print("🎯 Phase 3: Création du crew final...")
        return Crew(
            agents=dynamic_agents,
            tasks=dynamic_tasks,
            process=crew_process,
            verbose=True
        )

def create_sequential_tasks_from_problem(problem_statement: str, company_context: str = "", config_manager: AgentConfigManager = None, available_agents: List[str] = None) -> List[Task]:
    """Fonction utilitaire pour créer des tâches séquentielles à partir d'une problématique"""
    if config_manager is None:
        config_manager = AgentConfigManager()
    
    task_manager = SequentialTaskManager(config_manager)
    return task_manager.create_sequential_tasks(problem_statement, company_context, available_agents)

