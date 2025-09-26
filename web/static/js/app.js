/**
 * Application principale CrewAI Marketing
 * Gère la logique métier et l'intégration avec l'API
 */

class CrewAIApp {
    constructor() {
        this.api = window.api;
        this.ui = window.ui;
        this.data = {
            agents: [],
            crews: [],
            campaigns: [],
            stats: null,
        };
        this.init();
    }

    /**
     * Initialise l'application
     */
    async init() {
        try {
            this.ui.showLoading();

            // Vérifier la connexion à l'API
            await this.api.healthCheck();

            // Charger les données initiales
            await this.loadInitialData();

            // Configurer les méthodes de l'UI
            this.setupUIMethods();

            this.ui.hideLoading();
            this.ui.showToast("Application chargée avec succès", "success");
        } catch (error) {
            this.ui.hideLoading();
            this.ui.showToast("Erreur de connexion à l'API", "error");
            console.error("Initialization error:", error);
        }
    }

    /**
     * Charge les données initiales
     */
    async loadInitialData() {
        try {
            // Charger les statistiques
            this.data.stats = await this.api.getDashboardStats();

            // Charger les agents
            this.data.agents = await this.api.getAgents();

            // Charger les crews
            this.data.crews = await this.api.getCrews();

            // Charger les campagnes
            this.data.campaigns = await this.api.getCampaigns();
        } catch (error) {
            console.error("Error loading initial data:", error);
            throw error;
        }
    }

    /**
     * Configure les méthodes de l'UI
     */
    setupUIMethods() {
        // Remplacer les méthodes vides de l'UI par les vraies implémentations
        this.ui.loadDashboard = () => this.loadDashboard();
        this.ui.loadAgents = () => this.loadAgents();
        this.ui.loadCrews = () => this.loadCrews();
        this.ui.loadCampaigns = () => this.loadCampaigns();
        this.ui.loadFiles = () => this.loadFiles();
        this.ui.loadAgentsForCrew = () => this.loadAgentsForCrew();
        this.ui.loadCrewsForCampaign = () => this.loadCrewsForCampaign();
        this.ui.handleAgentSubmit = () => this.handleAgentSubmit();
        this.ui.handleCrewSubmit = () => this.handleCrewSubmit();
        this.ui.handleCampaignSubmit = () => this.handleCampaignSubmit();
        this.ui.handleExecutionSubmit = () => this.handleExecutionSubmit();
    }

    /**
     * Charge le dashboard
     */
    async loadDashboard() {
        try {
            // Mettre à jour les statistiques
            this.data.stats = await this.api.getDashboardStats();
            this.updateDashboardStats();

            // Charger les campagnes récentes
            this.data.campaigns = await this.api.getCampaigns();
            this.updateRecentCampaigns();
        } catch (error) {
            this.ui.showToast(
                "Erreur lors du chargement du dashboard",
                "error"
            );
            console.error("Dashboard load error:", error);
        }
    }

    /**
     * Met à jour les statistiques du dashboard
     */
    updateDashboardStats() {
        if (!this.data.stats) return;

        document.getElementById("totalAgents").textContent =
            this.data.stats.total_agents || 0;
        document.getElementById("totalCrews").textContent =
            this.data.stats.total_crews || 0;
        document.getElementById("totalCampaigns").textContent =
            this.data.stats.total_campaigns || 0;
        document.getElementById("completedCampaigns").textContent =
            this.data.stats.completed_campaigns || 0;
    }

    /**
     * Met à jour les campagnes récentes
     */
    updateRecentCampaigns() {
        const container = document.getElementById("recentCampaigns");
        if (!container) return;

        const recentCampaigns = this.data.campaigns.slice(0, 5);

        if (recentCampaigns.length === 0) {
            container.innerHTML =
                '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Aucune campagne récente</p>';
            return;
        }

        container.innerHTML = recentCampaigns
            .map(
                (campaign) => `
            <div class="card">
                <div class="card-body">
                    <div class="card-title">${campaign.name}</div>
                    <div class="card-subtitle">${campaign.problem_statement.substring(
                        0,
                        100
                    )}...</div>
                    <div class="card-description">
                        <span class="status status-${campaign.status}">${
                    campaign.status
                }</span>
                        <span style="margin-left: 1rem; color: var(--text-muted);">
                            ${new Date(campaign.created_at).toLocaleDateString(
                                "fr-FR"
                            )}
                        </span>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="app.executeCampaign(${
                        campaign.id
                    })">
                        <i class="fas fa-play"></i> Exécuter
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="app.viewCampaignResults(${
                        campaign.id
                    })">
                        <i class="fas fa-eye"></i> Voir
                    </button>
                </div>
            </div>
        `
            )
            .join("");
    }

    /**
     * Charge les agents
     */
    async loadAgents() {
        try {
            this.data.agents = await this.api.getAgents();
            this.updateAgentsGrid();
        } catch (error) {
            this.ui.showToast("Erreur lors du chargement des agents", "error");
            console.error("Agents load error:", error);
        }
    }

    /**
     * Met à jour la grille des agents
     */
    updateAgentsGrid() {
        const container = document.getElementById("agentsGrid");
        if (!container) return;

        if (this.data.agents.length === 0) {
            container.innerHTML =
                '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Aucun agent créé</p>';
            return;
        }

        container.innerHTML = this.data.agents
            .map(
                (agent) => `
            <div class="card">
                <div class="card-body">
                    <div class="card-title">${agent.name}</div>
                    <div class="card-subtitle">${agent.role}</div>
                    <div class="card-description">${agent.goal}</div>
                    <div style="margin-top: 1rem;">
                        <small style="color: var(--text-muted);">
                            Outils: ${agent.enabled_tools.length} | 
                            Max Iter: ${agent.max_iter} | 
                            Verbose: ${agent.verbose ? "Oui" : "Non"}
                        </small>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="app.editAgent(${
                        agent.id
                    })">
                        <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="btn btn-error btn-sm" onclick="app.deleteAgent(${
                        agent.id
                    })">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                </div>
            </div>
        `
            )
            .join("");
    }

    /**
     * Charge les crews
     */
    async loadCrews() {
        try {
            this.data.crews = await this.api.getCrews();
            this.updateCrewsGrid();
        } catch (error) {
            this.ui.showToast("Erreur lors du chargement des crews", "error");
            console.error("Crews load error:", error);
        }
    }

    /**
     * Met à jour la grille des crews
     */
    updateCrewsGrid() {
        const container = document.getElementById("crewsGrid");
        if (!container) return;

        if (this.data.crews.length === 0) {
            container.innerHTML =
                '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Aucun crew créé</p>';
            return;
        }

        container.innerHTML = this.data.crews
            .map(
                (crew) => `
            <div class="card">
                <div class="card-body">
                    <div class="card-title">${crew.name}</div>
                    <div class="card-subtitle">${
                        crew.description || "Aucune description"
                    }</div>
                    <div class="card-description">
                        <strong>Agents:</strong> ${crew.agents
                            .map((a) => a.name)
                            .join(", ")}
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="app.editCrew(${
                        crew.id
                    })">
                        <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="btn btn-error btn-sm" onclick="app.deleteCrew(${
                        crew.id
                    })">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                </div>
            </div>
        `
            )
            .join("");
    }

    /**
     * Charge les campagnes
     */
    async loadCampaigns() {
        try {
            this.data.campaigns = await this.api.getCampaigns();
            this.updateCampaignsGrid();
        } catch (error) {
            this.ui.showToast(
                "Erreur lors du chargement des campagnes",
                "error"
            );
            console.error("Campaigns load error:", error);
        }
    }

    /**
     * Met à jour la grille des campagnes
     */
    updateCampaignsGrid() {
        const container = document.getElementById("campaignsGrid");
        if (!container) return;

        if (this.data.campaigns.length === 0) {
            container.innerHTML =
                '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Aucune campagne créée</p>';
            return;
        }

        container.innerHTML = this.data.campaigns
            .map(
                (campaign) => `
            <div class="card">
                <div class="card-body">
                    <div class="card-title">${campaign.name}</div>
                    <div class="card-subtitle">${campaign.problem_statement.substring(
                        0,
                        150
                    )}...</div>
                    <div class="card-description">
                        <span class="status status-${campaign.status}">${
                    campaign.status
                }</span>
                        <span style="margin-left: 1rem; color: var(--text-muted);">
                            ${new Date(campaign.created_at).toLocaleDateString(
                                "fr-FR"
                            )}
                        </span>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-primary btn-sm" onclick="app.executeCampaign(${
                        campaign.id
                    })">
                        <i class="fas fa-play"></i> Exécuter
                    </button>
                    <button class="btn btn-secondary btn-sm" onclick="app.viewCampaignResults(${
                        campaign.id
                    })">
                        <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="btn btn-error btn-sm" onclick="app.deleteCampaign(${
                        campaign.id
                    })">
                        <i class="fas fa-trash"></i> Supprimer
                    </button>
                </div>
            </div>
        `
            )
            .join("");
    }

    /**
     * Charge les fichiers
     */
    async loadFiles() {
        // Pour l'instant, on affiche un message
        const container = document.getElementById("filesList");
        if (container) {
            container.innerHTML =
                '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Sélectionnez une campagne pour voir ses fichiers</p>';
        }
    }

    /**
     * Charge les agents pour la sélection dans un crew
     */
    async loadAgentsForCrew() {
        const container = document.getElementById("crewAgentsList");
        if (!container) return;

        container.innerHTML = this.data.agents
            .map(
                (agent) => `
            <div class="agent-checkbox">
                <input type="checkbox" id="agent_${agent.id}" name="selected_agents" value="${agent.name}">
                <label for="agent_${agent.id}">${agent.name} - ${agent.role}</label>
            </div>
        `
            )
            .join("");
    }

    /**
     * Charge les crews pour la sélection dans une campagne
     */
    async loadCrewsForCampaign() {
        const select = document.getElementById("campaignCrew");
        if (!select) return;

        select.innerHTML =
            '<option value="">Sélectionner un crew...</option>' +
            this.data.crews
                .map(
                    (crew) => `
                <option value="${crew.id}">${crew.name}</option>
            `
                )
                .join("");
    }

    /**
     * Gère la soumission du formulaire d'agent
     */
    async handleAgentSubmit() {
        try {
            this.ui.showLoading();

            const formData = new FormData(document.getElementById("agentForm"));
            const agentData = {
                name: formData.get("name"),
                role: formData.get("role"),
                goal: formData.get("goal"),
                backstory: formData.get("backstory"),
                enabled_tools: [], // Pour l'instant, on laisse vide
                max_iter: parseInt(formData.get("max_iter")),
                verbose: formData.has("verbose"),
            };

            await this.api.createAgent(agentData);

            this.ui.closeModal();
            this.ui.showToast("Agent créé avec succès", "success");
            await this.loadAgents();
        } catch (error) {
            this.ui.showToast("Erreur lors de la création de l'agent", "error");
            console.error("Agent creation error:", error);
        } finally {
            this.ui.hideLoading();
        }
    }

    /**
     * Gère la soumission du formulaire de crew
     */
    async handleCrewSubmit() {
        try {
            this.ui.showLoading();

            const formData = new FormData(document.getElementById("crewForm"));
            const selectedAgents = Array.from(
                document.querySelectorAll(
                    'input[name="selected_agents"]:checked'
                )
            ).map((input) => input.value);

            if (selectedAgents.length === 0) {
                this.ui.showToast(
                    "Veuillez sélectionner au moins un agent",
                    "warning"
                );
                return;
            }

            const crewData = {
                name: formData.get("name"),
                description: formData.get("description"),
                process_type: "sequential",
                selected_agents: selectedAgents,
            };

            await this.api.createCrew(crewData);

            this.ui.closeModal();
            this.ui.showToast("Crew créé avec succès", "success");
            await this.loadCrews();
        } catch (error) {
            this.ui.showToast("Erreur lors de la création du crew", "error");
            console.error("Crew creation error:", error);
        } finally {
            this.ui.hideLoading();
        }
    }

    /**
     * Gère la soumission du formulaire de campagne
     */
    async handleCampaignSubmit() {
        try {
            this.ui.showLoading();

            const formData = new FormData(
                document.getElementById("campaignForm")
            );
            const campaignData = {
                name: formData.get("name"),
                problem_statement: formData.get("problem_statement"),
                company_context: formData.get("company_context"),
                crew_id: parseInt(formData.get("crew_id")),
            };

            const campaign = await this.api.createCampaign(campaignData);

            this.ui.closeModal();
            this.ui.showToast("Campagne créée avec succès", "success");
            await this.loadCampaigns();

            // Proposer d'exécuter la campagne
            setTimeout(() => {
                if (
                    confirm("Voulez-vous exécuter cette campagne maintenant ?")
                ) {
                    this.ui.showExecutionModal(campaign.id);
                }
            }, 1000);
        } catch (error) {
            this.ui.showToast(
                "Erreur lors de la création de la campagne",
                "error"
            );
            console.error("Campaign creation error:", error);
        } finally {
            this.ui.hideLoading();
        }
    }

    /**
     * Gère la soumission du formulaire d'exécution
     */
    async handleExecutionSubmit() {
        try {
            this.ui.showLoading();

            const formData = new FormData(
                document.getElementById("executionForm")
            );
            const executionData = {
                openai_api_key: formData.get("openai_api_key"),
                serper_api_key: formData.get("serper_api_key") || null,
                openai_model: formData.get("openai_model"),
            };

            // Afficher le statut d'exécution
            document.getElementById("executionStatus").style.display = "block";
            document.getElementById("executeBtn").disabled = true;

            const result = await this.api.executeCampaign(
                this.ui.currentCampaignId,
                executionData
            );

            this.ui.closeModal();

            if (result.success) {
                this.ui.showToast("Campagne exécutée avec succès", "success");
                this.ui.showResultsModal(result.result);
                await this.loadCampaigns();
            } else {
                this.ui.showToast(
                    "Erreur lors de l'exécution de la campagne",
                    "error"
                );
            }
        } catch (error) {
            this.ui.showToast(
                "Erreur lors de l'exécution de la campagne",
                "error"
            );
            console.error("Campaign execution error:", error);
        } finally {
            this.ui.hideLoading();
            document.getElementById("executionStatus").style.display = "none";
            document.getElementById("executeBtn").disabled = false;
        }
    }

    // Méthodes d'action
    async executeCampaign(campaignId) {
        this.ui.showExecutionModal(campaignId);
    }

    async viewCampaignResults(campaignId) {
        try {
            const campaign = await this.api.getCampaign(campaignId);
            if (campaign.result) {
                this.ui.showResultsModal(campaign.result);
            } else {
                this.ui.showToast(
                    "Aucun résultat disponible pour cette campagne",
                    "warning"
                );
            }
        } catch (error) {
            this.ui.showToast(
                "Erreur lors du chargement des résultats",
                "error"
            );
        }
    }

    async deleteAgent(agentId) {
        if (confirm("Êtes-vous sûr de vouloir supprimer cet agent ?")) {
            try {
                await this.api.deleteAgent(agentId);
                this.ui.showToast("Agent supprimé avec succès", "success");
                await this.loadAgents();
            } catch (error) {
                this.ui.showToast(
                    "Erreur lors de la suppression de l'agent",
                    "error"
                );
            }
        }
    }

    async deleteCrew(crewId) {
        if (confirm("Êtes-vous sûr de vouloir supprimer ce crew ?")) {
            try {
                await this.api.deleteCrew(crewId);
                this.ui.showToast("Crew supprimé avec succès", "success");
                await this.loadCrews();
            } catch (error) {
                this.ui.showToast(
                    "Erreur lors de la suppression du crew",
                    "error"
                );
            }
        }
    }

    async deleteCampaign(campaignId) {
        if (confirm("Êtes-vous sûr de vouloir supprimer cette campagne ?")) {
            try {
                await this.api.deleteCampaign(campaignId);
                this.ui.showToast("Campagne supprimée avec succès", "success");
                await this.loadCampaigns();
            } catch (error) {
                this.ui.showToast(
                    "Erreur lors de la suppression de la campagne",
                    "error"
                );
            }
        }
    }

    editAgent(agentId) {
        // TODO: Implémenter l'édition d'agent
        this.ui.showToast(
            "Fonctionnalité d'édition en cours de développement",
            "info"
        );
    }

    editCrew(crewId) {
        // TODO: Implémenter l'édition de crew
        this.ui.showToast(
            "Fonctionnalité d'édition en cours de développement",
            "info"
        );
    }
}

// Initialiser l'application quand le DOM est chargé
document.addEventListener("DOMContentLoaded", () => {
    window.app = new CrewAIApp();
});
