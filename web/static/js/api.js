/**
 * API Client pour CrewAI Marketing
 * Gère toutes les communications avec l'API FastAPI
 */

class CrewAIApi {
    constructor(baseUrl = "http://localhost:8000") {
        this.baseUrl = baseUrl;
        this.defaultHeaders = {
            "Content-Type": "application/json",
        };
    }

    /**
     * Effectue une requête HTTP
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.detail ||
                        `HTTP ${response.status}: ${response.statusText}`
                );
            }

            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return await response.json();
            }

            return await response.text();
        } catch (error) {
            console.error("API Request failed:", error);
            throw error;
        }
    }

    /**
     * Vérifie la santé de l'API
     */
    async healthCheck() {
        return this.request("/health");
    }

    /**
     * Récupère les statistiques du dashboard
     */
    async getDashboardStats() {
        return this.request("/dashboard/stats");
    }

    /**
     * Récupère les outils disponibles
     */
    async getTools() {
        return this.request("/tools");
    }

    // ===== AGENTS =====

    /**
     * Récupère tous les agents
     */
    async getAgents() {
        return this.request("/agents/");
    }

    /**
     * Récupère un agent par ID
     */
    async getAgent(id) {
        return this.request(`/agents/${id}`);
    }

    /**
     * Crée un nouvel agent
     */
    async createAgent(agentData) {
        return this.request("/agents/", {
            method: "POST",
            body: JSON.stringify(agentData),
        });
    }

    /**
     * Met à jour un agent
     */
    async updateAgent(id, agentData) {
        return this.request(`/agents/${id}`, {
            method: "PUT",
            body: JSON.stringify(agentData),
        });
    }

    /**
     * Supprime un agent
     */
    async deleteAgent(id) {
        return this.request(`/agents/${id}`, {
            method: "DELETE",
        });
    }

    // ===== CREWS =====

    /**
     * Récupère tous les crews
     */
    async getCrews() {
        return this.request("/crews/");
    }

    /**
     * Récupère un crew par ID
     */
    async getCrew(id) {
        return this.request(`/crews/${id}`);
    }

    /**
     * Crée un nouveau crew
     */
    async createCrew(crewData) {
        return this.request("/crews/", {
            method: "POST",
            body: JSON.stringify(crewData),
        });
    }

    /**
     * Met à jour un crew
     */
    async updateCrew(id, crewData) {
        return this.request(`/crews/${id}`, {
            method: "PUT",
            body: JSON.stringify(crewData),
        });
    }

    /**
     * Supprime un crew
     */
    async deleteCrew(id) {
        return this.request(`/crews/${id}`, {
            method: "DELETE",
        });
    }

    // ===== CAMPAGNES =====

    /**
     * Récupère toutes les campagnes
     */
    async getCampaigns() {
        return this.request("/campaigns/");
    }

    /**
     * Récupère une campagne par ID
     */
    async getCampaign(id) {
        return this.request(`/campaigns/${id}`);
    }

    /**
     * Crée une nouvelle campagne
     */
    async createCampaign(campaignData) {
        return this.request("/campaigns/", {
            method: "POST",
            body: JSON.stringify(campaignData),
        });
    }

    /**
     * Met à jour une campagne
     */
    async updateCampaign(id, campaignData) {
        return this.request(`/campaigns/${id}`, {
            method: "PUT",
            body: JSON.stringify(campaignData),
        });
    }

    /**
     * Supprime une campagne
     */
    async deleteCampaign(id) {
        return this.request(`/campaigns/${id}`, {
            method: "DELETE",
        });
    }

    /**
     * Exécute une campagne
     */
    async executeCampaign(id, executionData) {
        const formData = new FormData();
        Object.keys(executionData).forEach((key) => {
            if (
                executionData[key] !== null &&
                executionData[key] !== undefined
            ) {
                formData.append(key, executionData[key]);
            }
        });

        return this.request(`/campaigns/${id}/execute`, {
            method: "POST",
            headers: {}, // Ne pas définir Content-Type pour FormData
            body: formData,
        });
    }

    // ===== FICHIERS =====

    /**
     * Récupère les fichiers d'une campagne
     */
    async getCampaignFiles(campaignId) {
        return this.request(`/campaigns/${campaignId}/files`);
    }

    /**
     * Upload un fichier pour une campagne
     */
    async uploadFile(campaignId, file) {
        const formData = new FormData();
        formData.append("file", file);

        return this.request(`/campaigns/${campaignId}/files`, {
            method: "POST",
            headers: {}, // Ne pas définir Content-Type pour FormData
            body: formData,
        });
    }

    /**
     * Supprime un fichier
     */
    async deleteFile(fileId) {
        return this.request(`/files/${fileId}`, {
            method: "DELETE",
        });
    }
}

// Instance globale de l'API
window.api = new CrewAIApi();
