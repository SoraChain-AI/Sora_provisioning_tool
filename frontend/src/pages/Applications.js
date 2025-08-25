import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
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
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Visibility as ViewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { ProjectService } from '../services/projectService';

function Applications() {
  const { id: projectId } = useParams();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [action, setAction] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadApplications();
  }, [projectId]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      const response = await ProjectService.getProjectApplications(projectId);
      setApplications(response.applications || []);
    } catch (err) {
      setError('Failed to load applications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (applicationId, action) => {
    try {
      await ProjectService.processApplication(applicationId, { action });
      setMessage(`Application ${action}ed successfully`);
      loadApplications();
      setOpenDialog(false);
    } catch (err) {
      setError(`Failed to ${action} application`);
      console.error(err);
    }
  };

  const handleOpenDialog = (application, actionType) => {
    setSelectedApplication(application);
    setAction(actionType);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedApplication(null);
    setAction('');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'rejected':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'proj_admin':
        return 'warning';
      case 'user':
        return 'info';
      case 'client':
        return 'success';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box>
        <LinearProgress />
        <Box sx={{ mt: 2 }}>
          <Typography>Loading applications...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Project Applications
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadApplications}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {message && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {applications.length === 0 ? (
        <Card>
          <CardContent>
            <Typography variant="body1" color="text.secondary" align="center">
              No applications found for this project.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Organization</TableCell>
                <TableCell>Role Requested</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Applied</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {applications.map((application) => (
                <TableRow key={application.id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {application.user_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {application.user_email}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>{application.organization}</TableCell>
                  <TableCell>
                    <Chip
                      label={application.role_requested}
                      color={getRoleColor(application.role_requested)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                      {application.message || 'No message'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={application.status}
                      color={getStatusColor(application.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption">
                      {new Date(application.created_at).toLocaleDateString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {application.status === 'pending' && (
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Approve">
                          <IconButton
                            color="success"
                            size="small"
                            onClick={() => handleOpenDialog(application, 'approve')}
                          >
                            <ApproveIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject">
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => handleOpenDialog(application, 'reject')}
                          >
                            <RejectIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    )}
                    {application.status !== 'pending' && (
                      <Tooltip title="View Details">
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={() => handleOpenDialog(application, 'view')}
                        >
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Action Confirmation Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {action === 'approve' && 'Approve Application'}
          {action === 'reject' && 'Reject Application'}
          {action === 'view' && 'Application Details'}
        </DialogTitle>
        <DialogContent>
          {selectedApplication && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    User
                  </Typography>
                  <Typography variant="body1">
                    {selectedApplication.user_name} ({selectedApplication.user_email})
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Organization
                  </Typography>
                  <Typography variant="body1">
                    {selectedApplication.organization}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Role Requested
                  </Typography>
                  <Typography variant="body1">
                    {selectedApplication.role_requested}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Message
                  </Typography>
                  <Typography variant="body1">
                    {selectedApplication.message || 'No message provided'}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Applied On
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedApplication.created_at).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          {action === 'approve' && (
            <Button
              color="success"
              variant="contained"
              onClick={() => handleAction(selectedApplication.id, 'approve')}
            >
              Approve
            </Button>
          )}
          {action === 'reject' && (
            <Button
              color="error"
              variant="contained"
              onClick={() => handleAction(selectedApplication.id, 'reject')}
            >
              Reject
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Applications;


