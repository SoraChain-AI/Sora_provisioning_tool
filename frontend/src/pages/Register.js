import React, { useState } from 'react';
import {
    Box,
    Paper,
    TextField,
    Button,
    Typography,
    Link,
    Alert,
    CircularProgress,
    Grid,
} from '@mui/material';
import { PersonAddOutlined } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { AuthService } from '../services/authService';

function Register() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        organization: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('🚀 Register form submitted');

        if (formData.password !== formData.confirmPassword) {
            console.log('❌ Passwords do not match');
            setError('Passwords do not match');
            return;
        }

        console.log('✅ Form validation passed, starting registration...');
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            console.log('🔄 Calling AuthService.register with:', { ...formData, password: '***' });

            // Filter out confirmPassword field before sending to API
            const { confirmPassword, ...registrationData } = formData;
            console.log('🔄 Sending registration data (without confirmPassword):', { ...registrationData, password: '***' });

            const result = await AuthService.register(registrationData);
            console.log('✅ Registration successful, result:', result);
            setSuccess('Registration successful! Please log in.');
            setTimeout(() => {
                navigate('/login');
            }, 2000);
        } catch (err) {
            console.error('❌ Registration failed in component:', err);
            const errorMessage = err.response?.data?.error || 'Registration failed. Please try again.';
            console.log('❌ Setting error message:', errorMessage);
            setError(errorMessage);
        } finally {
            console.log('🏁 Registration process completed, setting loading to false');
            setLoading(false);
        }
    };

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                p: 2,
            }}
        >
            <Paper
                elevation={24}
                sx={{
                    p: 4,
                    width: '100%',
                    maxWidth: 500,
                    textAlign: 'center',
                }}
            >
                <Box sx={{ mb: 3 }}>
                    <Box
                        sx={{
                            width: 64,
                            height: 64,
                            borderRadius: '50%',
                            backgroundColor: 'primary.main',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 16px',
                        }}
                    >
                        <PersonAddOutlined sx={{ color: 'white', fontSize: 32 }} />
                    </Box>
                    <Typography variant="h4" component="h1" gutterBottom>
                        Create Account
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Join Sorachain Dashboard and start managing your federated learning projects
                    </Typography>
                </Box>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {success && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                        {success}
                    </Alert>
                )}

                <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                id="name"
                                label="Full Name"
                                name="name"
                                autoComplete="name"
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                id="organization"
                                label="Organization"
                                name="organization"
                                autoComplete="organization"
                                value={formData.organization}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                required
                                fullWidth
                                id="email"
                                label="Email Address"
                                name="email"
                                autoComplete="email"
                                type="email"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                name="password"
                                label="Password"
                                type="password"
                                id="password"
                                autoComplete="new-password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                            <TextField
                                required
                                fullWidth
                                name="confirmPassword"
                                label="Confirm Password"
                                type="password"
                                id="confirmPassword"
                                autoComplete="new-password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                            />
                        </Grid>
                    </Grid>

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        size="large"
                        disabled={loading}
                        sx={{
                            py: 1.5,
                            fontSize: '1.1rem',
                            fontWeight: 600,
                            mt: 3,
                        }}
                    >
                        {loading ? <CircularProgress size={24} /> : 'Create Account'}
                    </Button>
                </Box>

                <Box sx={{ mt: 3, textAlign: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                        Already have an account?{' '}
                        <Link
                            component="button"
                            variant="body2"
                            onClick={() => navigate('/login')}
                            sx={{ cursor: 'pointer' }}
                        >
                            Sign in
                        </Link>
                    </Typography>
                </Box>
            </Paper>
        </Box>
    );
}

export default Register;


