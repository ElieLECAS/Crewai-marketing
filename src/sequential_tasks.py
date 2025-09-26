from crewai import Task, Crew, Process
from textwrap import dedent
from typing import Dict, List, Optional
import os
import re
import json
from .agents import create_agent_from_config
from .agent_config import AgentConfigManager


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
        """Crée la tâche principale du Meta Agent Manager"""
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
            
            INSTRUCTIONS IMPORTANTES POUR LES AGENTS AVEC OUTILS PDF :
            - Les agents doivent utiliser l'outil "pdf_search" avec UNE SEULE chaîne de caractères comme query
            - Exemple correct : pdf_search("Gamme Lumeal")
            - Exemple incorrect : pdf_search({{"query": "Gamme Lumeal", "pdf": "fichier.pdf"}})
            - L'outil recherche automatiquement dans tous les PDFs disponibles
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
                
                agent_info = f"""- **{agent_config.name} ({agent_config.role})**
  - **Objectif** : {agent_config.goal}
  - **Backstory** : {agent_config.backstory}
  - **Outils disponibles** : {tools_text}
  - **Max Iterations** : {agent_config.max_iter}
  - **Verbose** : {'Oui' if agent_config.verbose else 'Non'}"""
                
                agents_info.append(agent_info)
        
        agents_list = "\n\n            ".join(agents_info) if agents_info else "Aucun agent disponible"
        
        return Task(
            description=dedent(f"""
            Tu es le Meta Agent Manager. Tu reçois une problématique marketing et tu dois l'analyser pour créer des tâches spécifiques et les déléguer.
            
            PROBLÉMATIQUE REÇUE :
            {problem_statement}
            
            CONTEXTE ENTREPRISE :
            {company_context if company_context else "Aucun contexte spécifique fourni"}{pdf_info}
            
            MISSION IMPORTANTE :
            1. **Analyser la problématique** : Comprendre les enjeux, objectifs et contraintes
            2. **Évaluer les compétences** : Analyser les capacités, outils et spécialisations de chaque agent
            3. **Déterminer l'ordre optimal** : Choisir l'ordre d'exécution selon la logique de la problématique et les compétences
            4. **Créer des tâches spécifiques** : Générer des tâches concrètes adaptées aux capacités de chaque agent
            5. **Déléguer intelligemment** : Assigner chaque tâche à l'agent le plus compétent avec les bons outils
            6. **Structurer pour transmission** : Préparer les informations pour transmission via le système de context
            
            AGENTS DISPONIBLES DANS TON CREW :
            {agents_list}
            
            FORMAT DE DÉLÉGATION REQUIS :
            Tu dois créer un plan d'action structuré avec :
            
            ## ORDRE D'EXÉCUTION RECOMMANDÉ :
            [Liste les agents dans l'ordre optimal d'exécution avec justification basée sur :
            - Les compétences spécifiques de chaque agent
            - Les outils disponibles pour chaque agent
            - La logique de la problématique
            - Les dépendances entre les tâches]
            
            ## TÂCHES PAR AGENT (dans l'ordre recommandé) :
            [Pour chaque agent, crée une section avec :]
            - **Agent assigné** : [Nom et rôle de l'agent]
            - **Compétences utilisées** : [Quelles compétences spécifiques de l'agent seront utilisées]
            - **Outils recommandés** : [Quels outils l'agent devrait utiliser]
            - **Objectif** : [Objectif précis pour cet agent]
            - **Instructions** : [Instructions détaillées adaptées aux capacités de l'agent]
            - **Livrables** : [Format et contenu attendus]
            - **Justification** : [Pourquoi cet agent est le plus approprié pour cette tâche]
            - **Dépendances** : [Quels résultats des agents précédents sont nécessaires]
            - **Ordre d'exécution** : [Position dans la séquence et pourquoi]
            
            IMPORTANT : 
            - Chaque agent recevra le contexte de tous les agents précédents
            - Utilise les compétences et outils spécifiques de chaque agent
            - L'ordre que tu recommandes sera respecté
            
            LIVRABLE :
            Plan d'action structuré avec l'ordre d'exécution recommandé et les tâches déléguées pour tous les agents de ton crew.
            """).strip(),
            agent=meta_agent,
            expected_output="Plan d'action structuré avec l'ordre d'exécution choisi et les tâches déléguées pour tous les agents de ton crew.",
        )
    
    def create_agent_task(self, agent_name: str, problem_statement: str, company_context: str = "") -> Task:
        """Crée une tâche dynamique pour un agent spécifique"""
        agent = create_agent_from_config(agent_name, self.config_manager)
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
        
        return Task(
            description=dedent(f"""
            Tu es {agent_config.name}, {agent_config.role}.
            
            CONTEXTE :
            Tu vas recevoir via le système de context les instructions du Meta Agent Manager qui a analysé cette problématique :
            {problem_statement}
            
            {f"Contexte entreprise : {company_context}" if company_context else ""}{pdf_context}
            
            MISSION :
            1. **Récupère ta tâche** : Dans le context, trouve la section "## TÂCHE POUR {agent_config.name.upper()}"
            2. **Comprends l'ordre** : Le Meta Manager a défini un ordre d'exécution optimal - respecte-le
            3. **Utilise les dépendances** : Si des agents ont travaillé avant toi, utilise leurs résultats
            4. **Exécute précisément** : Accomplis exactement l'objectif défini avec les instructions données
            5. **Utilise tes outils** : Emploie tes outils selon tes besoins
            6. **Respecte le format** : Livre le résultat selon le format demandé
            
            IMPORTANT : 
            - Exécute uniquement ce qui t'est demandé dans ta section du context
            - Respecte l'ordre d'exécution défini par le Meta Manager
            - Utilise les résultats des agents précédents si disponibles
            
            LIVRABLE :
            Résultat conforme aux spécifications reçues via le context du Meta Manager.
            """).strip(),
            agent=agent,
            expected_output="Résultat conforme aux spécifications reçues via le context du Meta Manager.",
        )
    
    
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
        
        # Si on a le résultat du Meta Manager, déterminer l'ordre recommandé
        if meta_manager_result:
            ordered_agents = self.parse_recommended_order(meta_manager_result, available_agents)
        else:
            ordered_agents = available_agents
        
        # Créer les tâches dans l'ordre recommandé
        previous_tasks = []  # Les agents recevront le contexte des précédents
        
        for agent_name in ordered_agents:
            # Vérifier que l'agent existe
            if self.config_manager.get_agent_config(agent_name):
                agent_task = self.create_agent_task(agent_name, problem_statement, company_context)
                agent_task.context = previous_tasks.copy()  # L'agent reçoit le contexte de tous les agents précédents
                tasks.append(agent_task)
                previous_tasks.append(agent_task)  # Ajouter cette tâche au contexte pour les suivantes
        
        return tasks
    
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
        
        # Créer l'agent
        try:
            agent = create_agent_from_config(agent_name, self.config_manager, pdf_paths)
        except Exception as e:
            print(f"❌ Erreur création agent {agent_name}: {e}")
            return None
        
        # Construire la description enrichie avec le contexte
        enriched_description = self._build_enriched_task_description(
            task_info, problem_statement, company_context, context_tasks
        )
        
        # Créer la Task avec les informations du plan
        task = Task(
            description=enriched_description,
            expected_output=task_info["expected_output"],
            agent=agent,
            context=context_tasks.copy()  # Contexte des tâches dépendantes
        )
        
        print(f"✅ Tâche créée pour {agent_name} (priorité {task_info.get('priority', 'N/A')}, parallèle: {task_info.get('can_run_parallel', 'N/A')})")
        return task
    
    def _build_enriched_task_description(self, task_info: dict, problem_statement: str, 
                                        company_context: str, previous_tasks: List[Task]) -> str:
        """Construit une description de tâche enrichie avec le contexte"""
        
        # Contexte des tâches précédentes/dépendantes
        context_info = ""
        if previous_tasks:
            context_info = f"""
            
            CONTEXTE DES TÂCHES DÉPENDANTES :
            Tu as accès aux résultats des agents suivants via le système de contexte CrewAI :
            {chr(10).join([f"- {i+1}. {task.agent.role}" for i, task in enumerate(previous_tasks)])}
            
            Utilise ces résultats pour enrichir ton travail et assurer la cohérence de l'ensemble.
            """
        
        # Dépendances spécifiques
        dependencies_info = ""
        if task_info.get("dependencies"):
            dependencies_info = f"""
            
            DÉPENDANCES SPÉCIFIQUES :
            Cette tâche dépend des résultats de : {', '.join(task_info['dependencies'])}
            Assure-toi de bien utiliser ces informations dans ton travail.
            """
        
        # Outils recommandés
        tools_info = ""
        if task_info.get("tools_to_use"):
            tools_info = f"""
            
            OUTILS RECOMMANDÉS PAR LE META MANAGER :
            {', '.join(task_info['tools_to_use'])}
            Utilise ces outils selon tes besoins pour accomplir ta mission optimalement.
            """
        
        # Information sur l'exécution parallèle
        parallel_info = ""
        if task_info.get("can_run_parallel"):
            parallel_info = f"""
            
            EXÉCUTION PARALLÈLE :
            Cette tâche peut être exécutée en parallèle avec d'autres tâches.
            Coordonne-toi efficacement avec les autres agents si nécessaire.
            """
        
        return dedent(f"""
        {task_info['description']}
        
        PROBLÉMATIQUE INITIALE :
        {problem_statement}
        
        {f"CONTEXTE ENTREPRISE : {company_context}" if company_context else ""}
        {context_info}
        {dependencies_info}
        {tools_info}
        {parallel_info}
        
        CONTEXTE NÉCESSAIRE : {task_info.get('context_needed', 'Aucun contexte spécifique requis')}
        DURÉE ESTIMÉE : {task_info.get('estimated_duration', 'Non spécifiée')}
        PRIORITÉ : {task_info.get('priority', 'Non spécifiée')}
        """).strip()
    
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

