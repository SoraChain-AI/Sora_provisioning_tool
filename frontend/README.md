# NVFlare Provisioning Dashboard Frontend

A modern, responsive React-based frontend for the NVFlare Provisioning Dashboard. This application provides an intuitive interface for managing federated learning projects, users, and configurations.

## Features

### 🚀 **Core Functionality**
- **User Authentication**: Secure login/registration system with JWT tokens
- **Project Management**: Create, edit, and manage FL projects
- **Server Configuration**: Add and configure FL servers with ports and security settings
- **Client Management**: Manage FL clients with GPU specifications
- **Admin Roles**: Assign and manage project administrators
- **NVFlare Integration**: Direct integration with `nvflare provision` CLI tool

### 🎨 **Modern UI/UX**
- **Material-UI Design**: Beautiful, responsive interface using Material-UI v5
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile devices
- **Dark/Light Theme**: Customizable theme system
- **Interactive Components**: Cards, dialogs, forms, and data tables
- **Real-time Updates**: Live data updates and status monitoring

### 🔧 **Technical Features**
- **React 18**: Latest React features with hooks and functional components
- **React Router**: Client-side routing with protected routes
- **State Management**: Efficient state management with React hooks
- **API Integration**: RESTful API integration with axios
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Smooth loading indicators and progress bars

## Project Structure

```
frontend/
├── public/
│   ├── index.html          # Main HTML template
│   └── favicon.ico         # App icon
├── src/
│   ├── components/         # Reusable UI components
│   │   └── Layout.js       # Main layout with navigation
│   ├── pages/              # Page components
│   │   ├── Dashboard.js    # Main dashboard view
│   │   ├── Login.js        # Authentication page
│   │   ├── Register.js     # User registration
│   │   ├── Projects.js     # Project management
│   │   ├── ProjectDetail.js # Detailed project view
│   │   ├── Users.js        # User management
│   │   └── Settings.js     # User settings
│   ├── services/           # API services
│   │   ├── authService.js  # Authentication API calls
│   │   └── projectService.js # Project management API calls
│   ├── utils/              # Utility functions
│   ├── styles/             # Custom styles
│   ├── App.js              # Main application component
│   └── index.js            # Application entry point
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## Installation

### Prerequisites
- Node.js 16+ and npm
- Backend API running on port 8443

### Setup
1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   Create a `.env` file in the frontend directory:
   ```env
   REACT_APP_API_URL=http://localhost:8443/api/v1
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```
   The app will open at `http://localhost:3000`

## Usage

### 🔐 **Authentication**
- **Login**: Use default credentials `admin@example.com` / `admin123`
- **Registration**: Create new user accounts
- **JWT Tokens**: Automatic token management and refresh

### 📊 **Dashboard**
- **Overview**: View project statistics and recent activities
- **Quick Actions**: Access common functions from the main dashboard
- **Navigation**: Easy navigation between different sections

### 🗂️ **Project Management**
- **Create Projects**: Set up new FL projects with configurations
- **Configure Components**: Add servers, clients, and admins
- **Communication Settings**: Configure gRPC, HTTP, or TCP schemes
- **Overseer Agent**: Set up overseer agent paths and arguments

### ⚙️ **Provisioning**
- **NVFlare Integration**: Direct integration with CLI provisioning tool
- **Startup Kits**: Generate and download server/client/admin kits
- **Project Status**: Monitor provisioning status and workspace information

### 👥 **User Management**
- **User Roles**: Manage different user roles and permissions
- **Organization Support**: Multi-organization user management
- **Profile Settings**: User profile customization and preferences

## API Integration

The frontend integrates with the backend API through service modules:

### **Authentication Service**
- User login/logout
- Token validation
- User registration

### **Project Service**
- CRUD operations for projects
- Server/client/admin management
- Provisioning and download operations

## Styling and Theming

### **Material-UI Components**
- Consistent design language
- Responsive grid system
- Customizable theme system

### **Custom Styling**
- CSS-in-JS with Material-UI's `sx` prop
- Responsive breakpoints
- Consistent spacing and typography

## Development

### **Available Scripts**
```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
npm run eject      # Eject from Create React App
```

### **Code Style**
- Functional components with hooks
- Consistent naming conventions
- Proper error handling
- Responsive design principles

### **State Management**
- React hooks for local state
- Context API for global state (if needed)
- Efficient re-rendering strategies

## Deployment

### **Build for Production**
```bash
npm run build
```

### **Static Hosting**
The built app can be deployed to any static hosting service:
- Netlify
- Vercel
- AWS S3
- GitHub Pages

### **Environment Variables**
Ensure production environment variables are set:
```env
REACT_APP_API_URL=https://your-api-domain.com/api/v1
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Ensure responsive design
4. Test on multiple devices
5. Update documentation as needed

## Troubleshooting

### **Common Issues**

1. **API Connection Errors**
   - Verify backend is running on port 8443
   - Check CORS configuration
   - Verify API endpoints

2. **Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify all dependencies are installed

3. **Styling Issues**
   - Check Material-UI version compatibility
   - Verify theme configuration
   - Check CSS-in-JS syntax

## License

This project is part of the NVFlare Provisioning Dashboard and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check backend logs
4. Create an issue in the project repository





