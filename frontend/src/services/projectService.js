import api from './authService';

export const ProjectService = {
    // Projects
    async getProjects() {
        const response = await api.get('/projects');
        return response.data;
    },

    async getProject(id) {
        const response = await api.get(`/projects/${id}`);
        return response.data;
    },

    async createProject(projectData) {
        const response = await api.post('/projects', projectData);
        return response.data;
    },

    async updateProject(id, projectData) {
        const response = await api.put(`/projects/${id}`, projectData);
        return response.data;
    },

    async deleteProject(id) {
        const response = await api.delete(`/projects/${id}`);
        return response.data;
    },

    // Users
    async getUsers() {
        const response = await api.get('/users');
        return response.data;
    },

    // Servers
    async addServer(projectId, serverData) {
        const response = await api.post(`/projects/${projectId}/servers`, serverData);
        return response.data;
    },

    async updateServer(projectId, serverId, serverData) {
        const response = await api.put(`/projects/${projectId}/servers/${serverId}`, serverData);
        return response.data;
    },

    async deleteServer(projectId, serverId) {
        const response = await api.delete(`/projects/${projectId}/servers/${serverId}`);
        return response.data;
    },

    // Clients
    async addClient(projectId, clientData) {
        const response = await api.post(`/projects/${projectId}/clients`, clientData);
        return response.data;
    },

    async updateClient(projectId, clientId, clientData) {
        const response = await api.put(`/projects/${projectId}/clients/${clientId}`, clientData);
        return response.data;
    },

    async deleteClient(projectId, clientId) {
        const response = await api.delete(`/projects/${projectId}/clients/${clientId}`);
        return response.data;
    },

    // Admins
    async addAdmin(projectId, adminData) {
        const response = await api.post(`/projects/${projectId}/admins`, adminData);
        return response.data;
    },

    async updateAdmin(projectId, adminId, adminData) {
        const response = await api.put(`/projects/${projectId}/admins/${adminId}`, adminData);
        return response.data;
    },

    async deleteAdmin(projectId, adminId) {
        const response = await api.delete(`/projects/${projectId}/admins/${adminId}`);
        return response.data;
    },

    // User Applications
    async applyToProject(projectId, applicationData) {
        const response = await api.post(`/projects/${projectId}/apply`, applicationData);
        return response.data;
    },

    async getProjectApplications(projectId) {
        const response = await api.get(`/projects/${projectId}/applications`);
        return response.data;
    },

    async processApplication(applicationId, actionData) {
        const response = await api.post(`/applications/${applicationId}/approve`, actionData);
        return response.data;
    },

    // Provisioning
    async provisionProject(projectId) {
        const response = await api.post(`/provision/${projectId}`);
        return response.data;
    },

    async reprovisionProject(projectId) {
        const response = await api.post(`/reprovision/${projectId}`);
        return response.data;
    },

    async getProjectStatus(projectId) {
        const response = await api.get(`/status/${projectId}`);
        return response.data;
    },

    // Downloads
    async downloadStartupKit(projectId, type, itemId = null) {
        let url = `/download/${type}/${projectId}`;
        if (itemId) {
            url += `/${itemId}`;
        }

        const response = await api.get(url, {
            responseType: 'blob',
        });

        // Create download link
        const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', `${type}_startup_kit.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        return response.data;
    },

    // Check if project is provisioned
    async checkProvisioningStatus(projectId) {
        try {
            const response = await api.get(`/status/${projectId}`);
            return response.data;
        } catch (error) {
            console.error('Error checking provisioning status:', error);
            return { status: 'not_provisioned' };
        }
    },

    // Download all startup kits at once
    async downloadAllStartupKits(projectId) {
        const response = await api.get(`/download-all/${projectId}`, {
            responseType: 'blob',
        });

        // Create download link
        const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', `project_${projectId}_all_startup_kits.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);

        return response.data;
    },
};

export default ProjectService;


