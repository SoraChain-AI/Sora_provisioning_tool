import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Divider,
  Alert,
  Switch,
  FormControlLabel,
  Avatar,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  Edit as EditIcon,
  Cancel as CancelIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

function Settings({ user }) {
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    organization: user?.organization || '',
  });
  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    darkMode: false,
    autoSave: true,
  });
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleProfileChange = (field, value) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePreferenceChange = (field, value) => {
    setPreferences(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEdit = () => {
    setEditing(true);
  };

  const handleCancel = () => {
    setProfileData({
      name: user?.name || '',
      email: user?.email || '',
      organization: user?.organization || '',
    });
    setEditing(false);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Here you would typically call an API to update the user profile
      // await UserService.updateProfile(profileData);
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setEditing(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
        Settings
      </Typography>

      {message.text && (
        <Alert severity={message.type} sx={{ mb: 3 }}>
          {message.text}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Avatar sx={{ width: 64, height: 64, mr: 2 }}>
                  {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
                </Avatar>
                <Box>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Profile Information
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Manage your account details and preferences
                  </Typography>
                </Box>
              </Box>

              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={profileData.name}
                    onChange={(e) => handleProfileChange('name', e.target.value)}
                    disabled={!editing}
                    InputProps={{
                      startAdornment: <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={profileData.email}
                    onChange={(e) => handleProfileChange('email', e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Organization"
                    value={profileData.organization}
                    onChange={(e) => handleProfileChange('organization', e.target.value)}
                    disabled={!editing}
                  />
                </Grid>
              </Grid>

              <Box display="flex" gap={2} mt={3}>
                {editing ? (
                  <>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      disabled={saving}
                    >
                      {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<CancelIcon />}
                      onClick={handleCancel}
                    >
                      Cancel
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={handleEdit}
                  >
                    Edit Profile
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Preferences */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Preferences
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Customize your dashboard experience
              </Typography>

              <Divider sx={{ mb: 3 }} />

              <Box display="flex" flexDirection="column" gap={3}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.emailNotifications}
                      onChange={(e) => handlePreferenceChange('emailNotifications', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Email Notifications"
                  labelPlacement="start"
                  sx={{ justifyContent: 'space-between', ml: 0 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.darkMode}
                      onChange={(e) => handlePreferenceChange('darkMode', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Dark Mode"
                  labelPlacement="start"
                  sx={{ justifyContent: 'space-between', ml: 0 }}
                />

                <FormControlLabel
                  control={
                    <Switch
                      checked={preferences.autoSave}
                      onChange={(e) => handlePreferenceChange('autoSave', e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Auto-save Forms"
                  labelPlacement="start"
                  sx={{ justifyContent: 'space-between', ml: 0 }}
                />
              </Box>

              <Box mt={3}>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={() => {
                    setMessage({ type: 'success', text: 'Preferences saved!' });
                    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
                  }}
                >
                  Save Preferences
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Account Security */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Account Security
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Manage your account security settings
              </Typography>

              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    sx={{ py: 2 }}
                  >
                    Change Password
                  </Button>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    sx={{ py: 2 }}
                  >
                    Enable Two-Factor Authentication
                  </Button>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    sx={{ py: 2 }}
                  >
                    View Login History
                  </Button>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Button
                    variant="outlined"
                    fullWidth
                    sx={{ py: 2 }}
                  >
                    Manage API Keys
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                System Information
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                Dashboard version and system details
              </Typography>

              <Divider sx={{ mb: 3 }} />

              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Dashboard Version
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    v1.0.0
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Last Login
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {new Date().toLocaleDateString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Account Status
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500, color: 'success.main' }}>
                    Active
                  </Typography>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Role
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 500 }}>
                    {user?.role || 'User'}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Settings;





