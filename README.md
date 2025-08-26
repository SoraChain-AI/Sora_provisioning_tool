# Sorachain Provisioning Dashboard

A modern, full-stack dashboard for managing Sorachain federated learning projects with direct integration to the NVFlare CLI provisioning tool.

# start backend
source ~/FL/bin/activate && python3 run_dashboard.py --host 0.0.0.0 --port 8443 --debug &

# backend
cd /home/franky/nvflare-provisioning-dashboard/frontend && npm start

or
cd /home/franky/nvflare-provisioning-dashboard && ./start_frontend.sh

pkill -f "npm start"
pkill -f "python3 run_dashboard.py" && sleep 3


## 🚀 Features

### **Core Functionality**
- **User Authentication**: Secure JWT-based login/registration system
- **Project Management**: Create, edit, and manage Sorachain FL projects
- **Server Configuration**: Configure FL servers with ports and security settings
- **Client Management**: Manage FL clients with GPU specifications
- **Admin Roles**: Assign and manage project administrators
- **NVFlare Integration**: Direct integration with `nvflare provision` CLI tool
- **Startup Kits**: Generate and download server/client/admin startup kits

### **Technical Features**
- **Backend**: Flask-based REST API with SQLAlchemy ORM
- **Frontend**: Modern React 18 application with Material-UI
- **Database**: SQLite database with automatic schema management
- **Authentication**: JWT-based security with role-based access control
- **Provisioning**: Direct CLI integration for accurate configuration generation

## 🏗️ Architecture

```
nvflare-provisioning-dashboard/
├── application/                 # Flask backend application
│   ├── __init__.py            # App factory and configuration
│   ├── models.py              # Database models (User, Project, Server, Client, Admin)
│   ├── views.py               # API endpoints and routes
│   └── provisioning.py        # NVFlare CLI integration service
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API service modules
│   │   └── App.js             # Main application component
│   ├── package.json           # Frontend dependencies
│   └── README.md              # Frontend documentation
├── run_dashboard.py            # Backend entry point
├── start_dashboard.sh          # Complete startup script
├── start_frontend.sh           # Frontend-only startup script
├── check_status.sh             # Status monitoring script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+ (recommended) or 14+
- NVFlare CLI tool installed
- Virtual environment (recommended)

### Quick Start

1. **Clone and Setup**
   ```bash
   cd /home/franky
   git clone <repository-url> nvflare-provisioning-dashboard
   cd nvflare-provisioning-dashboard
   ```

2. **Activate Virtual Environment**
   ```bash
   source ~/FL/bin/activate
   ```

3. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

## 🚀 Usage

### **Start Complete Dashboard**
```bash
# This starts both backend and frontend
./start_dashboard.sh
```

### **Start Individual Services**
```bash
# Start backend only
python3 run_dashboard.py --host 0.0.0.0 --port 8443 --debug

# Start frontend only
./start_frontend.sh
```

### **Check Status**
```bash
./check_status.sh
```

## 🌐 Access URLs

After starting the dashboard:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8443
- **Backend Dashboard**: http://localhost:8443

## 🔐 Default Login

- **Email**: admin@example.com
- **Password**: admin123

## 📱 Frontend Features

### **Dashboard Overview**
- Project statistics and metrics
- Quick action buttons
- Recent projects list
- System status overview

### **Project Management**
- Create and edit projects
- Configure communication schemes (gRPC, HTTP, TCP)
- Set overseer agent paths and arguments
- Manage project metadata

### **Component Management**
- **Servers**: Add/edit servers with port configurations
- **Clients**: Configure clients with GPU specifications
- **Admins**: Assign project administrators with roles

### **Provisioning**
- Generate startup kits using NVFlare CLI
- Download server/client/admin kits
- Monitor provisioning status
- View workspace information

## 🔧 Backend API

### **Authentication Endpoints**
- `POST /api/v1/login` - User authentication
- `POST /api/v1/users` - User registration

### **Project Endpoints**
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### **Component Endpoints**
- `POST /api/v1/projects/{id}/servers` - Add server
- `PUT /api/v1/projects/{id}/servers/{server_id}` - Update server
- `DELETE /api/v1/projects/{id}/servers/{server_id}` - Delete server
- Similar endpoints for clients and admins

### **Provisioning Endpoints**
- `POST /api/v1/provision/{id}` - Provision project
- `GET /api/v1/download/{type}/{id}` - Download startup kit
- `GET /api/v1/status/{id}` - Get project status

## 🗄️ Database Schema

### **Users Table**
- User authentication and profile information
- Role-based access control
- Organization management

### **Projects Table**
- Project configuration and metadata
- Communication scheme settings
- Overseer agent configuration

### **Servers Table**
- Server specifications and ports
- Connection security settings
- Organization information

### **Clients Table**
- Client specifications and GPU details
- Organization and description
- Resource requirements

### **Admins Table**
- Project administrator assignments
- Role definitions
- Organization information

## 🔒 Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- Role-based access control
- Secure API endpoints
- CORS configuration


## 📊 Monitoring and Logs

### **Backend Logs**
- Flask debug logging
- Database operation logs
- NVFlare CLI execution logs
- Error tracking and reporting

### **Frontend Monitoring**
- API response monitoring
- User interaction tracking
- Error boundary handling
- Performance metrics

## 🛠️ Development

### **Backend Development**
```bash
cd application
# Edit models, views, or provisioning logic
# Restart backend to apply changes
```

### **Frontend Development**
```bash
cd frontend
npm start
# Edit React components
# Changes auto-reload in development
```

### **Database Changes**
```bash
# Database is auto-created on first run
# Models are defined in application/models.py
# Schema changes require database recreation
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Port Conflicts**
   ```bash
   ./check_status.sh
   # Kill conflicting processes if needed
   ```

2. **Dependency Issues**
   ```bash
   # Backend
   pip install -r requirements.txt --force-reinstall
   
   # Frontend
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Database Issues**
   ```bash
   # Remove database file to recreate
   rm provisioning_dashboard.db
   # Restart backend
   ```


### **Logs and Debugging**
```bash
# Backend logs
tail -f /var/log/syslog | grep python

# Frontend logs
# Check browser console and network tab

# Database inspection
sqlite3 provisioning_dashboard.db
.tables
.schema users
```

## 📈 Performance

### **Backend Optimization**
- SQLAlchemy query optimization
- Database connection pooling
- Efficient file handling
- Background task processing

### **Frontend Optimization**
- React component optimization
- API request caching
- Lazy loading for large datasets
- Efficient state management

## 🔄 Updates and Maintenance

### **Regular Maintenance**
- Database cleanup and optimization
- Log rotation and management
- Dependency updates
- Security patches

### **Backup and Recovery**
- Database backup procedures
- Configuration backup
- Workspace data management
- Disaster recovery planning

## 🤝 Contributing

1. Follow the existing code style
2. Add proper error handling
3. Ensure responsive design
4. Test on multiple devices
5. Update documentation
6. Add unit tests for new features

## 📄 License

This project follows the same licensing terms as NVFlare.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review API documentation
3. Check backend and frontend logs
4. Verify NVFlare installation
5. Create an issue in the project repository

## 🎯 Roadmap

### **Short Term**
- Enhanced error handling
- User management improvements
- Project templates
- Bulk operations

### **Long Term**
- Multi-tenant support
- Advanced monitoring
- Integration with other FL frameworks
- Cloud deployment support

---

**Happy Federated Learning! 🚀**

