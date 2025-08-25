import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Card,
    CardContent,
    Typography,
    Button,
    Chip,
    LinearProgress,
    Alert,
    IconButton,
    Tooltip,
} from '@mui/material';
import {
    Folder as ProjectsIcon,
    People as UsersIcon,
    Storage as StorageIcon,
    Download as DownloadIcon,
    Refresh as RefreshIcon,
    Add as AddIcon,
    Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ProjectService } from '../services/projectService';

function Dashboard({ user }) {
    const [stats, setStats] = useState({
        totalProjects: 0,
        totalUsers: 0,
        totalClients: 0,
        totalServers: 0,
    });
    const [recentProjects, setRecentProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        loadDashboardData();
    }, []);

    const loadDashboardData = async () => {
        try {
            setLoading(true);
            const [projectsResponse, usersResponse] = await Promise.all([
                ProjectService.getProjects(),
                ProjectService.getUsers(),
            ]);

            const projects = projectsResponse.projects || [];
            const users = usersResponse.users || [];

            setStats({
                totalProjects: projects.length,
                totalUsers: users.length,
                totalClients: projects.reduce((acc, p) => acc + (p.clients?.length || 0), 0),
                totalServers: projects.reduce((acc, p) => acc + (p.servers?.length || 0), 0),
            });

            setRecentProjects(projects.slice(0, 3));
        } catch (err) {
            setError('Failed to load dashboard data');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const StatCard = ({ title, value, icon, color, onClick }) => (
        <Card
            sx={{
                height: '100%',
                cursor: onClick ? 'pointer' : 'default',
                '&:hover': onClick ? { boxShadow: 4, transform: 'translateY(-2px)' } : {},
                transition: 'all 0.2s ease-in-out',
            }}
            onClick={onClick}
        >
            <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Box>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                            {title}
                        </Typography>
                        <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color }}>
                            {value}
                        </Typography>
                    </Box>
                    <Box
                        sx={{
                            width: 48,
                            height: 48,
                            borderRadius: '50%',
                            backgroundColor: `${color}.light`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        {icon}
                    </Box>
                </Box>
            </CardContent>
        </Card>
    );

    const ProjectCard = ({ project }) => (
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
                <Box display="flex" gap={1} mb={2}>
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
                </Box>
                <Button
                    size="small"
                    variant="outlined"
                    onClick={() => navigate(`/projects/${project.id}`)}
                >
                    View Details
                </Button>
            </CardContent>
        </Card>
    );

    if (loading) {
        return (
            <Box>
                <LinearProgress />
                <Box sx={{ mt: 2 }}>
                    <Typography>Loading dashboard...</Typography>
                </Box>
            </Box>
        );
    }

    return (
        <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
                    Welcome back, {user?.name || user?.email}!
                </Typography>
                <Box>
                    <Tooltip title="Refresh Dashboard">
                        <IconButton onClick={loadDashboardData} color="primary">
                            <RefreshIcon />
                        </IconButton>
                    </Tooltip>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            {/* Statistics Cards */}
            <Grid container spacing={3} mb={4}>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Projects"
                        value={stats.totalProjects}
                        icon={<ProjectsIcon sx={{ color: 'primary.main' }} />}
                        color="primary"
                        onClick={() => navigate('/projects')}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Users"
                        value={stats.totalUsers}
                        icon={<UsersIcon sx={{ color: 'secondary.main' }} />}
                        color="secondary"
                        onClick={() => navigate('/users')}
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Servers"
                        value={stats.totalServers}
                        icon={<StorageIcon sx={{ color: 'success.main' }} />}
                        color="success"
                    />
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                    <StatCard
                        title="Total Clients"
                        value={stats.totalClients}
                        icon={<DownloadIcon sx={{ color: 'warning.main' }} />}
                        color="warning"
                    />
                </Grid>
            </Grid>

            {/* Quick Actions */}
            <Box mb={4}>
                <Typography variant="h5" component="h2" gutterBottom sx={{ fontWeight: 600 }}>
                    Quick Actions
                </Typography>
                <Box display="flex" gap={2} flexWrap="wrap">
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => navigate('/projects')}
                        size="large"
                    >
                        Create New Project
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<UsersIcon />}
                        onClick={() => navigate('/users')}
                        size="large"
                    >
                        Manage Users
                    </Button>
                    <Button
                        variant="outlined"
                        startIcon={<SettingsIcon />}
                        onClick={() => navigate('/settings')}
                        size="large"
                    >
                        Settings
                    </Button>
                </Box>
            </Box>

            {/* Recent Projects */}
            <Box>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
                        Recent Projects
                    </Typography>
                    <Button
                        variant="text"
                        onClick={() => navigate('/projects')}
                        size="small"
                    >
                        View All
                    </Button>
                </Box>

                {recentProjects.length === 0 ? (
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
                                onClick={() => navigate('/projects')}
                            >
                                Create Project
                            </Button>
                        </CardContent>
                    </Card>
                ) : (
                    <Grid container spacing={3}>
                        {recentProjects.map((project) => (
                            <Grid item xs={12} md={4} key={project.id}>
                                <ProjectCard project={project} />
                            </Grid>
                        ))}
                    </Grid>
                )}
            </Box>
        </Box>
    );
}

export default Dashboard;

