import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

function Users() {
    return (
        <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                Users Management
            </Typography>
            <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary">
                    Users management functionality coming soon...
                </Typography>
            </Paper>
        </Box>
    );
}

export default Users;





