import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://20.244.6.237:8443/api/v1';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 second timeout
});

console.log('🔧 Axios instance created with baseURL:', API_BASE_URL);

// Add request interceptor to include auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');

        console.log('📤 Request interceptor:', {
            method: config.method?.toUpperCase(),
            url: config.url,
            baseURL: config.baseURL,
            fullURL: config.baseURL + config.url,
            hasToken: !!token,
            tokenLength: token ? token.length : 0,
            tokenStart: token ? token.substring(0, 20) + '...' : 'none'
        });

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('🔑 Authorization header set:', `Bearer ${token.substring(0, 20)}...`);
        } else {
            console.log('⚠️ No access token found in localStorage');
        }
        return config;
    },
    (error) => {
        console.error('❌ Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
    (response) => {
        console.log('📥 Response interceptor success:', {
            status: response.status,
            statusText: response.statusText,
            url: response.config.url,
            data: response.data
        });
        return response;
    },
    (error) => {
        console.error('❌ Response interceptor error:', {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            data: error.response?.data,
            config: error.config
        });

        // Only auto-logout on 401 if it's not a project update request
        // This prevents automatic logout during project updates which might be permission-related
        if (error.response?.status === 401) {
            const url = error.config?.url || '';
            const method = error.config?.method || '';

            // Don't auto-logout for project updates - let the calling code handle it
            if (method === 'put' && url.includes('/projects/')) {
                console.log('🔒 401 on project update - not auto-logging out, letting caller handle it');
                return Promise.reject(error);
            }

            // For other 401 errors, proceed with logout
            console.log('🔒 401 error - logging out user');
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const AuthService = {
    async login(email, password) {
        console.log('🔐 AuthService.login called with:', { email, password: '***' });
        try {
            const response = await api.post('/login', { email, password });
            console.log('✅ Login response:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Login error:', error);
            throw error;
        }
    },

    async register(userData) {
        console.log('📝 AuthService.register called with:', { ...userData, password: '***' });
        try {
            console.log('🔄 Making API call to:', api.defaults.baseURL + '/users');
            console.log('🔄 Request data:', JSON.stringify(userData, null, 2));
            console.log('🔄 Request headers:', api.defaults.headers);

            const response = await api.post('/users', userData);
            console.log('✅ Registration response:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Registration error:', error);
            console.error('❌ Error details:', {
                message: error.message,
                response: error.response?.data,
                status: error.response?.status,
                statusText: error.response?.statusText
            });

            // Log the full error object for debugging
            console.error('❌ Full error object:', error);
            console.error('❌ Error config:', error.config);
            console.error('❌ Error request:', error.request);

            throw error;
        }
    },

    async validateToken(token) {
        try {
            const response = await api.get('/users', {
                headers: { Authorization: `Bearer ${token}` },
            });
            return response.data.users[0]; // Return first user as current user
        } catch (error) {
            throw new Error('Invalid token');
        }
    },

    logout() {
        localStorage.removeItem('access_token');
    },

    isAuthenticated() {
        return !!localStorage.getItem('access_token');
    },
};

export default api;


