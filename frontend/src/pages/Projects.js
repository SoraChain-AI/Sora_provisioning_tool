import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Button,
    Card,
    CardContent,
    Grid,
    Chip,
    IconButton,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Alert,
    LinearProgress,
    Tooltip,
} from '@mui/material';
import {
    Add as AddIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Download as DownloadIcon,
    PlayArrow as ProvisionIcon,
    Info as InfoIcon,
} from '@mui/icons-material';
import { ProjectService } from '../services/projectService';

function Projects() {
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [openDialog, setOpenDialog] = useState(false);
    const [editingProject, setEditingProject] = useState(null);
    const [currentUser, setCurrentUser] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        scheme: 'grpc',
        server_name: 'FLServer.com',
    });

    useEffect(() => {
        // Get current user from localStorage
        const userData = localStorage.getItem('user');
        if (userData) {
            try {
                setCurrentUser(JSON.parse(userData));
            } catch (error) {
                console.error('Error parsing user data:', error);
            }
        }
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            setLoading(true);
            const response = await ProjectService.getProjects();
            setProjects(response.projects || []);
        } catch (err) {
            setError('Failed to load projects');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const canEditProject = (project) => {
        if (!currentUser) return false;
        return currentUser.role === 'admin' || project.created_by === currentUser.id;
    };

    const handleViewDetails = (projectId) => {
        // Navigate to project detail page
        window.location.href = `/projects/${projectId}`;
    };

    const handleOpenDialog = (project = null) => {
        if (project) {
            setEditingProject(project);
            setFormData({
                name: project.name,
                description: project.description || '',
                scheme: project.scheme || 'grpc',
                server_name: project.server_name || 'FLServer.com',
            });
        } else {
            setEditingProject(null);
            setFormData({
                name: '',
                description: '',
                scheme: 'grpc',
                server_name: 'FLServer.com',
            });
        }
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setEditingProject(null);
        setFormData({
            name: '',
            description: '',
            scheme: 'grpc',
            server_name: 'FLServer.com',
        });
    };

    const handleSubmit = async () => {
        try {
            if (editingProject) {
                await ProjectService.updateProject(editingProject.id, formData);
            } else {
                await ProjectService.createProject(formData);
            }
            handleCloseDialog();
            loadProjects();
        } catch (err) {
            if (err.response?.status === 401) {
                setError('Authentication failed. Please log in again.');
                // Don't redirect to login automatically - let user decide
                console.error('Authentication error during project update:', err);
            } else {
                setError('Failed to save project');
                console.error(err);
            }
        }
    };

    const handleDelete = async (projectId) => {
        if (window.confirm('Are you sure you want to delete this project?')) {
            try {
                await ProjectService.deleteProject(projectId);
                loadProjects();
            } catch (err) {
                setError('Failed to delete project');
                console.error(err);
            }
        }
    };

    const handleProvision = async (projectId) => {
        try {
            await ProjectService.provisionProject(projectId);
            alert('Project provisioned successfully!');
        } catch (err) {
            setError('Failed to provision project');
            console.error(err);
        }
    };

    const handleDownload = async (projectId, type) => {
        try {
            await ProjectService.downloadStartupKit(projectId, type);
        } catch (err) {
            setError('Failed to download startup kit');
            console.error(err);
        }
    };

    if (loading) {
        return (
            <Box>
                <LinearProgress />
                <Box sx={{ mt: 2 }}>
                    <Typography>Loading projects...</Typography>
                </Box>
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                    Projects
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => handleOpenDialog()}
                >
                    Create Project
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {projects.length === 0 ? (
                <Card>
                    <CardContent sx={{ textAlign: 'center', py: 4 }}>
                        <Typography variant="h6" color="text.secondary" gutterBottom>
                            No projects yet
                        </Typography>
                        <Typography variant="body2" color="text.secondary" mb={2}>
                            Create your first federated learning project to get started
                        </Typography>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => handleOpenDialog()}
                        >
                            Create Project
                        </Button>
                    </CardContent>
                </Card>
            ) : (
                <Grid container spacing={3}>
                    {projects.map((project) => (
                        <Grid item xs={12} md={6} lg={4} key={project.id}>
                            <Card sx={{ height: '100%' }}>
                                <CardContent>
                                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                                        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                                            {project.name}
                                        </Typography>
                                        <Chip
                                            label={project.scheme}
                                            size="small"
                                            color="primary"
                                            variant="outlined"
                                        />
                                    </Box>

                                    <Typography variant="body2" color="text.secondary" mb={2}>
                                        {project.description || 'No description available'}
                                    </Typography>

                                    <Typography variant="body2" color="text.secondary" mb={2} sx={{ fontSize: '0.875rem' }}>
                                        Created by: {project.creator_name || 'Unknown'} ({project.creator_email || 'Unknown'})
                                    </Typography>

                                    <Box display="flex" gap={1} mb={3}>
                                        <Chip
                                            label={`${project.servers?.length || 0} Servers`}
                                            size="small"
                                            variant="outlined"
                                        />
                                        <Chip
                                            label={`${project.clients?.length || 0} Clients`}
                                            size="small"
                                            variant="outlined"
                                        />
                                        <Chip
                                            label={`${project.admins?.length || 0} Admins`}
                                            size="small"
                                            variant="outlined"
                                        />
                                    </Box>

                                    <Box display="flex" gap={1} flexWrap="wrap">
                                        {/* View Details Button - Always visible */}
                                        <Tooltip title="View Project Details">
                                            <IconButton
                                                size="small"
                                                color="info"
                                                onClick={() => handleViewDetails(project.id)}
                                            >
                                                <InfoIcon />
                                            </IconButton>
                                        </Tooltip>

                                        {/* Edit Button - Only for project owners or admins */}
                                        {canEditProject(project) && (
                                            <Tooltip title="Edit Project">
                                                <IconButton
                                                    size="small"
                                                    onClick={() => handleOpenDialog(project)}
                                                >
                                                    <EditIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}

                                        {/* Provision Button - Only for project owners or admins */}
                                        {canEditProject(project) && (
                                            <Tooltip title="Provision Project">
                                                <IconButton
                                                    size="small"
                                                    color="success"
                                                    onClick={() => handleProvision(project.id)}
                                                >
                                                    <ProvisionIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}

                                        {/* Download Button - Only for project owners or admins */}
                                        {canEditProject(project) && (
                                            <Tooltip title="Download Server Kit">
                                                <IconButton
                                                    size="small"
                                                    color="primary"
                                                    onClick={() => handleDownload(project.id, 'server')}
                                                >
                                                    <DownloadIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}

                                        {/* Delete Button - Only for project owners or admins */}
                                        {canEditProject(project) && (
                                            <Tooltip title="Delete Project">
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleDelete(project.id)}
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </Tooltip>
                                        )}
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}

            {/* Create/Edit Project Dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
                <DialogTitle>
                    {editingProject ? 'Edit Project' : 'Create New Project'}
                </DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Project Name"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    fullWidth
                                    label="Description"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    multiline
                                    rows={3}
                                />
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <FormControl fullWidth>
                                    <InputLabel>Communication Scheme</InputLabel>
                                    <Select
                                        value={formData.scheme}
                                        label="Communication Scheme"
                                        onChange={(e) => setFormData({ ...formData, scheme: e.target.value })}
                                    >
                                        <MenuItem value="grpc">gRPC</MenuItem>
                                        <MenuItem value="http">HTTP</MenuItem>
                                        <MenuItem value="tcp">TCP</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <TextField
                                    fullWidth
                                    label="Server Name"
                                    value={formData.server_name}
                                    onChange={(e) => setFormData({ ...formData, server_name: e.target.value })}
                                    placeholder="e.g., FLServer.com"
                                />
                            </Grid>
                        </Grid>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Cancel</Button>
                    <Button onClick={handleSubmit} variant="contained">
                        {editingProject ? 'Update' : 'Create'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default Projects;





