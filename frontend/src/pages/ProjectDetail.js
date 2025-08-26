import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
  Tabs,
  Tab,
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
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  PlayArrow as ProvisionIcon,
  Storage as ServerIcon,
  Person as ClientIcon,
  AdminPanelSettings as AdminIcon,
  Assignment as ApplicationsIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { ProjectService } from '../services/projectService';

function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({});
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    loadProject();
    // Get current user from localStorage
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setCurrentUser(user);
  }, [id]);

  const canEditProject = () => {
    if (!currentUser || !project) return false;

    // Admin can edit any project
    if (currentUser.role === 'admin') return true;
    // Project creator can edit their own project
    return project.created_by === currentUser.id;
  };

  const loadProject = async () => {
    try {
      setLoading(true);
      const response = await ProjectService.getProject(id);

      // ProjectService.getProject() already returns response.data, so response is the data
      // Backend returns { project: {...}, servers: [...], clients: [...], admins: [...] }
      const projectData = response.project;
      const servers = response.servers || [];
      const clients = response.clients || [];
      const admins = response.admins || [];

      // Combine all data into the project object
      const combinedProject = {
        ...projectData,
        servers: servers,
        clients: clients,
        admins: admins
      };

      setProject(combinedProject);
    } catch (err) {
      setError('Failed to load project');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (type, item = null) => {
    setDialogType(type);
    setEditingItem(item);

    if (item) {
      // Set form data based on item type
      if (type === 'server') {
        setFormData({
          name: item.name,
          org: item.org,
          fed_learn_port: item.fed_learn_port || 8002,
          admin_port: item.admin_port || 8003,
          connection_security: item.connection_security || 'mtls',
        });
      } else if (type === 'client') {
        setFormData({
          name: item.name,
          org: item.org,
          description: item.description || '',
          num_gpus: item.num_gpus || 1,
          gpu_memory: item.gpu_memory || 16,
        });
      } else if (type === 'admin') {
        setFormData({
          email: item.email,
          org: item.org,
          role: item.role || 'project_admin',
        });
      }
    } else {
      // Set default form data based on type
      if (type === 'server') {
        setFormData({
          name: '',
          org: '',
          fed_learn_port: 8002,
          admin_port: 8003,
          connection_security: 'mtls',
        });
      } else if (type === 'client') {
        setFormData({
          name: '',
          org: '',
          description: '',
          num_gpus: 1,
          gpu_memory: 16,
        });
      } else if (type === 'admin') {
        setFormData({
          email: '',
          org: '',
          role: 'project_admin',
        });
      }
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setDialogType('');
    setEditingItem(null);
    setFormData({});
  };

  const handleSubmit = async () => {
    try {
      if (dialogType === 'server') {
        if (editingItem) {
          await ProjectService.updateServer(id, editingItem.id, formData);
        } else {
          await ProjectService.addServer(id, formData);
        }
      } else if (dialogType === 'client') {
        if (editingItem) {
          await ProjectService.updateClient(id, editingItem.id, formData);
        } else {
          await ProjectService.addClient(id, formData);
        }
      } else if (dialogType === 'admin') {
        if (editingItem) {
          await ProjectService.updateAdmin(id, editingItem.id, formData);
        } else {
          await ProjectService.addAdmin(id, formData);
        }
      }
      handleCloseDialog();
      loadProject();
    } catch (err) {
      setError('Failed to save item');
      console.error(err);
    }
  };

  const handleDelete = async (type, itemId) => {
    if (window.confirm('Are you sure you want to delete this item?')) {
      try {
        if (type === 'server') {
          await ProjectService.deleteServer(id, itemId);
        } else if (type === 'client') {
          await ProjectService.deleteClient(id, itemId);
        } else if (type === 'admin') {
          await ProjectService.deleteAdmin(id, itemId);
        }
        loadProject();
      } catch (err) {
        setError('Failed to delete item');
        console.error(err);
      }
    }
  };

  const handleProvision = async () => {
    try {
      await ProjectService.provisionProject(id);
      alert('Project provisioned successfully!');
    } catch (err) {
      setError('Failed to provision project');
      console.error(err);
    }
  };

  const handleDownload = async (type) => {
    try {
      await ProjectService.downloadStartupKit(id, type);
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
          <Typography>Loading project...</Typography>
        </Box>
      </Box>
    );
  }

  if (!project) {
    return (
      <Box>
        <Alert severity="error">Project not found</Alert>
      </Box>
    );
  }

  const renderServerForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Server Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Organization"
          value={formData.org}
          onChange={(e) => setFormData({ ...formData, org: e.target.value })}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Fed Learn Port"
          type="number"
          value={formData.fed_learn_port}
          onChange={(e) => setFormData({ ...formData, fed_learn_port: parseInt(e.target.value) || 8002 })}
          inputProps={{ min: 1024, max: 65535 }}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Admin Port"
          type="number"
          value={formData.admin_port}
          onChange={(e) => setFormData({ ...formData, admin_port: parseInt(e.target.value) || 8003 })}
          inputProps={{ min: 1024, max: 65535 }}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Connection Security</InputLabel>
          <Select
            value={formData.connection_security}
            label="Connection Security"
            onChange={(e) => setFormData({ ...formData, connection_security: e.target.value })}
          >
            <MenuItem value="clear">Clear</MenuItem>
            <MenuItem value="tls">TLS</MenuItem>
            <MenuItem value="mtls">mTLS</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderClientForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Client Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Organization"
          value={formData.org}
          onChange={(e) => setFormData({ ...formData, org: e.target.value })}
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
        <TextField
          fullWidth
          label="Number of GPUs"
          type="number"
          value={formData.num_gpus}
          onChange={(e) => setFormData({ ...formData, num_gpus: parseInt(e.target.value) || 0 })}
          inputProps={{ min: 0 }}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="GPU Memory (GB)"
          type="number"
          value={formData.gpu_memory}
          onChange={(e) => setFormData({ ...formData, gpu_memory: parseInt(e.target.value) || 0 })}
          inputProps={{ min: 0 }}
          required
        />
      </Grid>
    </Grid>
  );

  const renderAdminForm = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
      </Grid>
      <Grid item xs={12} sm={6}>
        <TextField
          fullWidth
          label="Organization"
          value={formData.org}
          onChange={(e) => setFormData({ ...formData, org: e.target.value })}
          required
        />
      </Grid>
      <Grid item xs={12}>
        <FormControl fullWidth>
          <InputLabel>Role</InputLabel>
          <Select
            value={formData.role}
            label="Role"
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
          >
            <MenuItem value="project_admin">Project Admin</MenuItem>
            <MenuItem value="project_lead">Project Lead</MenuItem>
            <MenuItem value="researcher">Researcher</MenuItem>
          </Select>
        </FormControl>
      </Grid>
    </Grid>
  );

  const renderForm = () => {
    switch (dialogType) {
      case 'server':
        return renderServerForm();
      case 'client':
        return renderClientForm();
      case 'admin':
        return renderAdminForm();
      default:
        return null;
    }
  };

  const getDialogTitle = () => {
    const action = editingItem ? 'Edit' : 'Add';
    const type = dialogType.charAt(0).toUpperCase() + dialogType.slice(1);
    return `${action} ${type}`;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          {project.name}
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<ProvisionIcon />}
            onClick={handleProvision}
            disabled={!canEditProject()}
            title={!canEditProject() ? "Only project creators can provision projects" : ""}
          >
            Provision Project
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('server')}
            disabled={!canEditProject()}
            title={!canEditProject() ? "Only project creators can download server kits" : ""}
          >
            Download Server Kit
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Project Info Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Project Details
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {project.description || 'No description available'}
              </Typography>
              <Box display="flex" gap={1}>
                <Chip label={project.scheme} color="primary" variant="outlined" />
                <Chip label={`API v${project.api_version}`} variant="outlined" />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Configuration
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Server Name:</strong> {project.server_name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Scheme:</strong> {project.scheme}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>



      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab
            label={`Servers (${project.servers?.length || 0})`}
            icon={<ServerIcon />}
            iconPosition="start"
          />
          <Tab
            label={`Clients (${project.clients?.length || 0})`}
            icon={<ClientIcon />}
            iconPosition="start"
          />
          <Tab
            label={`Admins (${project.admins?.length || 0})`}
            icon={<AdminIcon />}
            iconPosition="start"
          />
          <Tab
            label="Applications"
            icon={<ApplicationsIcon />}
            iconPosition="start"
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5">Servers</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog('server')}
              disabled={!canEditProject()}
              title={!canEditProject() ? "Only project creators can add servers" : ""}
            >
              Add Server
            </Button>
          </Box>
          <Grid container spacing={3}>
            {project.servers?.map((server) => (
              <Grid item xs={12} md={6} lg={4} key={server.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Typography variant="h6">{server.name}</Typography>
                      <Chip label={server.connection_security} size="small" color="primary" />
                    </Box>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Org: {server.org}
                    </Typography>
                    <Box display="flex" gap={1} mb={2}>
                      <Chip label={`Port: ${server.fed_learn_port}`} size="small" variant="outlined" />
                      <Chip label={`Admin: ${server.admin_port}`} size="small" variant="outlined" />
                    </Box>
                    <Box display="flex" gap={1}>
                      {canEditProject() && (
                        <Tooltip title="Edit Server">
                          <IconButton size="small" onClick={() => handleOpenDialog('server', server)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      {canEditProject() && (
                        <Tooltip title="Delete Server">
                          <IconButton size="small" color="error" onClick={() => handleDelete('server', server.id)}>
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
        </Box>
      )}

      {activeTab === 1 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5">Clients</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog('client')}
              disabled={!canEditProject()}
              title={!canEditProject() ? "Only project creators can add clients" : ""}
            >
              Add Client
            </Button>
          </Box>
          <Grid container spacing={3}>
            {project.clients?.map((client) => (
              <Grid item xs={12} md={6} lg={4} key={client.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>{client.name}</Typography>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {client.description || 'No description'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Org: {client.org}
                    </Typography>
                    <Box display="flex" gap={1} mb={2}>
                      <Chip label={`${client.num_gpus} GPUs`} size="small" variant="outlined" />
                      <Chip label={`${client.gpu_memory}GB`} size="small" variant="outlined" />
                    </Box>
                    <Box display="flex" gap={1}>
                      {canEditProject() && (
                        <Tooltip title="Edit Client">
                          <IconButton size="small" onClick={() => handleOpenDialog('client', client)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      {canEditProject() && (
                        <Tooltip title="Delete Client">
                          <IconButton size="small" color="error" onClick={() => handleDelete('client', client.id)}>
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
        </Box>
      )}

      {activeTab === 2 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5">Admins</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog('admin')}
              disabled={!canEditProject()}
              title={!canEditProject() ? "Only project creators can add admins" : ""}
            >
              Add Admin
            </Button>
          </Box>
          <Grid container spacing={3}>
            {project.admins?.map((admin) => (
              <Grid item xs={12} md={6} lg={4} key={admin.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>{admin.email}</Typography>
                    <Typography variant="body2" color="text.secondary" mb={2}>
                      Org: {admin.org}
                    </Typography>
                    <Chip label={admin.role} size="small" color="secondary" />
                    <Box display="flex" gap={1} mt={2}>
                      {canEditProject() && (
                        <Tooltip title="Edit Admin">
                          <IconButton size="small" onClick={() => handleOpenDialog('admin', admin)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      {canEditProject() && (
                        <Tooltip title="Delete Admin">
                          <IconButton size="small" color="error" onClick={() => handleDelete('admin', admin.id)}>
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
        </Box>
      )}

      {activeTab === 3 && (
        <Box>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5">Applications</Typography>
            <Button
              variant="outlined"
              onClick={() => navigate(`/projects/${id}/applications`)}
            >
              Manage Applications
            </Button>
          </Box>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary">
                View and manage user applications to join this project. Click "Manage Applications" to see all pending, approved, and rejected applications.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>{getDialogTitle()}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            {renderForm()}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingItem ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ProjectDetail;




