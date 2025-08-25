import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetail from './pages/ProjectDetail';
import Applications from './pages/Applications';
import Users from './pages/Users';
import Settings from './pages/Settings';
import { AuthService } from './services/authService';

// Create theme
const theme = createTheme({
    palette: {
        primary: {
            main: '#1976d2',
        },
        secondary: {
            main: '#dc004e',
        },
        background: {
            default: '#f5f5f5',
        },
    },
    typography: {
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
        h4: {
            fontWeight: 600,
        },
        h5: {
            fontWeight: 600,
        },
    },
});

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            AuthService.validateToken(token)
                .then((userData) => {
                    setUser(userData);
                    setIsAuthenticated(true);
                })
                .catch(() => {
                    localStorage.removeItem('access_token');
                })
                .finally(() => {
                    setLoading(false);
                });
        } else {
            setLoading(false);
        }
    }, []);

    const handleLogin = (token, userData) => {
        localStorage.setItem('access_token', token);
        setUser(userData);
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
        setIsAuthenticated(false);
    };

    if (loading) {
        return (
            <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight="100vh"
            >
                Loading...
            </Box>
        );
    }

    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Router
                future={{
                    v7_startTransition: true,
                    v7_relativeSplatPath: true
                }}
            >
                <Routes>
                    <Route
                        path="/login"
                        element={
                            !isAuthenticated ? (
                                <Login onLogin={handleLogin} />
                            ) : (
                                <Navigate to="/dashboard" replace />
                            )
                        }
                    />
                    <Route
                        path="/register"
                        element={
                            !isAuthenticated ? (
                                <Register />
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Navigate to="/dashboard" replace />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/dashboard"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Dashboard user={user} />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/projects"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Projects />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/projects/:id"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <ProjectDetail />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/projects/:id/applications"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Applications />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/users"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Users />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                    <Route
                        path="/settings"
                        element={
                            isAuthenticated ? (
                                <Layout user={user} onLogout={handleLogout}>
                                    <Settings user={user} />
                                </Layout>
                            ) : (
                                <Navigate to="/login" replace />
                            )
                        }
                    />
                </Routes>
            </Router>
        </ThemeProvider>
    );
}

export default App;

