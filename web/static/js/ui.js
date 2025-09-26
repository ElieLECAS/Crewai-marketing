/**
 * Gestionnaire d'interface utilisateur
 * Gère les modales, notifications, navigation, etc.
 */

class UIManager {
    constructor() {
        this.currentPage = "dashboard";
        this.currentModal = null;
        this.init();
    }

    /**
     * Initialise l'interface utilisateur
     */
    init() {
        this.setupNavigation();
        this.setupModals();
        this.setupFileUpload();
        this.setupEventListeners();
    }

    /**
     * Configure la navigation
     */
    setupNavigation() {
        const navLinks = document.querySelectorAll(".nav-link");
        navLinks.forEach((link) => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.showPage(page);
            });
        });
    }

    /**
     * Affiche une page spécifique
     */
    showPage(pageName) {
        // Masquer toutes les pages
        document.querySelectorAll(".page").forEach((page) => {
            page.classList.remove("active");
        });

        // Désactiver tous les liens de navigation
        document.querySelectorAll(".nav-link").forEach((link) => {
            link.classList.remove("active");
        });

        // Afficher la page demandée
        const targetPage = document.getElementById(pageName);
        if (targetPage) {
            targetPage.classList.add("active");
        }

        // Activer le lien de navigation correspondant
        const targetLink = document.querySelector(`[data-page="${pageName}"]`);
        if (targetLink) {
            targetLink.classList.add("active");
        }

        this.currentPage = pageName;

        // Charger les données de la page
        this.loadPageData(pageName);
    }

    /**
     * Charge les données d'une page
     */
    async loadPageData(pageName) {
        try {
            switch (pageName) {
                case "dashboard":
                    await this.loadDashboard();
                    break;
                case "agents":
                    await this.loadAgents();
                    break;
                case "crews":
                    await this.loadCrews();
                    break;
                case "campaigns":
                    await this.loadCampaigns();
                    break;
                case "files":
                    await this.loadFiles();
                    break;
            }
        } catch (error) {
            this.showToast("Erreur lors du chargement des données", "error");
            console.error("Error loading page data:", error);
        }
    }

    /**
     * Configure les modales
     */
    setupModals() {
        // Fermer les modales en cliquant sur la croix
        document.querySelectorAll(".close").forEach((closeBtn) => {
            closeBtn.addEventListener("click", () => {
                this.closeModal();
            });
        });

        // Fermer les modales en cliquant à l'extérieur
        document.querySelectorAll(".modal").forEach((modal) => {
            modal.addEventListener("click", (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        });

        // Échapper pour fermer les modales
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.currentModal) {
                this.closeModal();
            }
        });
    }

    /**
     * Affiche une modale
     */
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add("active");
            this.currentModal = modalId;
            document.body.style.overflow = "hidden";
        }
    }

    /**
     * Ferme la modale actuelle
     */
    closeModal() {
        if (this.currentModal) {
            const modal = document.getElementById(this.currentModal);
            if (modal) {
                modal.classList.remove("active");
            }
            this.currentModal = null;
            document.body.style.overflow = "";
        }
    }

    /**
     * Configure l'upload de fichiers
     */
    setupFileUpload() {
        const uploadArea = document.getElementById("fileUploadArea");
        const fileInput = document.getElementById("fileInput");

        if (uploadArea && fileInput) {
            // Clic sur la zone d'upload
            uploadArea.addEventListener("click", () => {
                fileInput.click();
            });

            // Drag & Drop
            uploadArea.addEventListener("dragover", (e) => {
                e.preventDefault();
                uploadArea.classList.add("dragover");
            });

            uploadArea.addEventListener("dragleave", () => {
                uploadArea.classList.remove("dragover");
            });

            uploadArea.addEventListener("drop", (e) => {
                e.preventDefault();
                uploadArea.classList.remove("dragover");
                const files = e.dataTransfer.files;
                this.handleFileUpload(files);
            });

            // Sélection de fichiers
            fileInput.addEventListener("change", (e) => {
                this.handleFileUpload(e.target.files);
            });
        }
    }

    /**
     * Gère l'upload de fichiers
     */
    async handleFileUpload(files) {
        if (!files.length) return;

        // Pour l'instant, on a besoin d'une campagne sélectionnée
        // Dans une vraie implémentation, on devrait avoir un système de sélection de campagne
        this.showToast(
            "Veuillez d'abord créer une campagne pour uploader des fichiers",
            "warning"
        );
    }

    /**
     * Configure les écouteurs d'événements
     */
    setupEventListeners() {
        // Boutons de création
        document
            .getElementById("createAgentBtn")
            ?.addEventListener("click", () => {
                this.showCreateAgentModal();
            });

        document
            .getElementById("createCrewBtn")
            ?.addEventListener("click", () => {
                this.showCreateCrewModal();
            });

        document
            .getElementById("createCampaignBtn")
            ?.addEventListener("click", () => {
                this.showCreateCampaignModal();
            });

        document
            .getElementById("newCampaignBtn")
            ?.addEventListener("click", () => {
                this.showCreateCampaignModal();
            });

        // Formulaires
        document
            .getElementById("agentForm")
            ?.addEventListener("submit", (e) => {
                e.preventDefault();
                this.handleAgentSubmit();
            });

        document.getElementById("crewForm")?.addEventListener("submit", (e) => {
            e.preventDefault();
            this.handleCrewSubmit();
        });

        document
            .getElementById("campaignForm")
            ?.addEventListener("submit", (e) => {
                e.preventDefault();
                this.handleCampaignSubmit();
            });

        document
            .getElementById("executionForm")
            ?.addEventListener("submit", (e) => {
                e.preventDefault();
                this.handleExecutionSubmit();
            });

        // Boutons d'annulation
        document
            .getElementById("cancelAgent")
            ?.addEventListener("click", () => {
                this.closeModal();
            });

        document.getElementById("cancelCrew")?.addEventListener("click", () => {
            this.closeModal();
        });

        document
            .getElementById("cancelCampaign")
            ?.addEventListener("click", () => {
                this.closeModal();
            });

        document
            .getElementById("cancelExecution")
            ?.addEventListener("click", () => {
                this.closeModal();
            });
    }

    /**
     * Affiche un toast de notification
     */
    showToast(message, type = "info", title = "") {
        const container = document.getElementById("toastContainer");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast ${type}`;

        const iconMap = {
            success: "fas fa-check-circle",
            error: "fas fa-exclamation-circle",
            warning: "fas fa-exclamation-triangle",
            info: "fas fa-info-circle",
        };

        toast.innerHTML = `
            <i class="toast-icon ${iconMap[type] || iconMap.info}"></i>
            <div class="toast-content">
                ${title ? `<div class="toast-title">${title}</div>` : ""}
                <div class="toast-message">${message}</div>
            </div>
            <i class="toast-close fas fa-times"></i>
        `;

        // Bouton de fermeture
        toast.querySelector(".toast-close").addEventListener("click", () => {
            toast.remove();
        });

        container.appendChild(toast);

        // Suppression automatique après 5 secondes
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    /**
     * Affiche l'overlay de chargement
     */
    showLoading() {
        const overlay = document.getElementById("loadingOverlay");
        if (overlay) {
            overlay.classList.add("active");
        }
    }

    /**
     * Masque l'overlay de chargement
     */
    hideLoading() {
        const overlay = document.getElementById("loadingOverlay");
        if (overlay) {
            overlay.classList.remove("active");
        }
    }

    /**
     * Affiche la modale de création d'agent
     */
    showCreateAgentModal() {
        document.getElementById("agentModalTitle").textContent = "Nouvel Agent";
        document.getElementById("agentForm").reset();
        this.showModal("agentModal");
    }

    /**
     * Affiche la modale de création de crew
     */
    async showCreateCrewModal() {
        document.getElementById("crewModalTitle").textContent = "Nouveau Crew";
        document.getElementById("crewForm").reset();

        // Charger la liste des agents
        await this.loadAgentsForCrew();
        this.showModal("crewModal");
    }

    /**
     * Affiche la modale de création de campagne
     */
    async showCreateCampaignModal() {
        document.getElementById("campaignModalTitle").textContent =
            "Nouvelle Campagne";
        document.getElementById("campaignForm").reset();

        // Charger la liste des crews
        await this.loadCrewsForCampaign();
        this.showModal("campaignModal");
    }

    /**
     * Affiche la modale d'exécution de campagne
     */
    showExecutionModal(campaignId) {
        this.currentCampaignId = campaignId;
        document.getElementById("executionForm").reset();
        this.showModal("executionModal");
    }

    /**
     * Affiche la modale de résultats
     */
    showResultsModal(results) {
        this.displayCampaignResults(results);
        this.showModal("resultsModal");
    }

    /**
     * Affiche les résultats d'une campagne
     */
    displayCampaignResults(results) {
        const container = document.getElementById("campaignResults");
        if (!container) return;

        // Parser les résultats (similaire à la logique Streamlit)
        const parsed = this.parseCampaignResults(results);

        container.innerHTML = `
            <div class="campaign-results">
                ${
                    parsed.metaManager
                        ? `
                    <div class="result-section">
                        <h3><i class="fas fa-brain"></i> Plan du Meta Manager</h3>
                        <div class="result-content">${parsed.metaManager}</div>
                    </div>
                `
                        : ""
                }
                
                ${
                    parsed.linkedinPosts.length > 0
                        ? `
                    <div class="result-section">
                        <h3><i class="fab fa-linkedin"></i> Posts LinkedIn</h3>
                        ${parsed.linkedinPosts
                            .map(
                                (post, index) => `
                            <div style="margin-bottom: 1.5rem; padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <h4>Post LinkedIn ${index + 1}</h4>
                                <div class="result-content">${post}</div>
                            </div>
                        `
                            )
                            .join("")}
                    </div>
                `
                        : ""
                }
                
                ${
                    parsed.instagramPosts.length > 0
                        ? `
                    <div class="result-section">
                        <h3><i class="fab fa-instagram"></i> Posts Instagram</h3>
                        ${parsed.instagramPosts
                            .map(
                                (post, index) => `
                            <div style="margin-bottom: 1.5rem; padding: 1rem; background: white; border-radius: 8px; border: 1px solid #e2e8f0;">
                                <h4>Post Instagram ${index + 1}</h4>
                                <div class="result-content">${post}</div>
                            </div>
                        `
                            )
                            .join("")}
                    </div>
                `
                        : ""
                }
            </div>
        `;
    }

    /**
     * Parse les résultats d'une campagne (similaire à la logique Streamlit)
     */
    parseCampaignResults(result) {
        const resultStr = String(result);

        const parsed = {
            metaManager: "",
            linkedinPosts: [],
            instagramPosts: [],
            otherContent: [],
        };

        // Extraire les posts LinkedIn
        const linkedinRegex = /linkedin.*?post.*?/gi;
        const linkedinMatches = resultStr.match(linkedinRegex);
        if (linkedinMatches) {
            parsed.linkedinPosts = linkedinMatches.map((match) => match.trim());
        }

        // Extraire les posts Instagram
        const instagramRegex = /instagram.*?post.*?/gi;
        const instagramMatches = resultStr.match(instagramRegex);
        if (instagramMatches) {
            parsed.instagramPosts = instagramMatches.map((match) =>
                match.trim()
            );
        }

        // Extraire le plan du Meta Manager
        const metaRegex = /meta manager.*?(?=linkedin|instagram|$)/is;
        const metaMatch = resultStr.match(metaRegex);
        if (metaMatch) {
            parsed.metaManager = metaMatch[0].trim();
        }

        return parsed;
    }

    // Méthodes de chargement des données (seront implémentées dans app.js)
    async loadDashboard() {
        /* Implémenté dans app.js */
    }
    async loadAgents() {
        /* Implémenté dans app.js */
    }
    async loadCrews() {
        /* Implémenté dans app.js */
    }
    async loadCampaigns() {
        /* Implémenté dans app.js */
    }
    async loadFiles() {
        /* Implémenté dans app.js */
    }
    async loadAgentsForCrew() {
        /* Implémenté dans app.js */
    }
    async loadCrewsForCampaign() {
        /* Implémenté dans app.js */
    }
    async handleAgentSubmit() {
        /* Implémenté dans app.js */
    }
    async handleCrewSubmit() {
        /* Implémenté dans app.js */
    }
    async handleCampaignSubmit() {
        /* Implémenté dans app.js */
    }
    async handleExecutionSubmit() {
        /* Implémenté dans app.js */
    }
}

// Instance globale du gestionnaire UI
window.ui = new UIManager();
