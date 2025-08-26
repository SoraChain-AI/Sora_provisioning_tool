#!/usr/bin/env python3
"""
API Views for Sorachain Provisioning Dashboard
"""

from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from .models import User, Project, Server, Client, Admin, UserApplication
from .provisioning import NVFlareProvisioningService
import io
from datetime import datetime

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize provisioning service
provisioning_service = NVFlareProvisioningService()

def add_cors_headers(response):
    """Add CORS headers to response"""
    # Handle both response objects and tuples (status_code, response)
    if isinstance(response, tuple):
        # If response is a tuple (status_code, response), extract the response object
        status_code, response_obj = response
        response_obj.headers['Access-Control-Allow-Origin'] = '*'
        response_obj.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response_obj.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response_obj
    else:
        # If response is a response object
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        User.query.first()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        response = jsonify({'status': 'unhealthy', 'error': str(e)})
        response.status_code = 500
        return response

@main_bp.route('/')
def index():
    """Main dashboard page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sorachain Provisioning Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #007acc; color: white; padding: 20px; border-radius: 5px; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #007acc; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
            .btn:hover { background: #005a9e; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Sorachain Provisioning Dashboard</h1>
                <p>Manage your Sorachain federated learning projects and generate startup kits</p>
            </div>
            
            <div class="section">
                <h2>Quick Actions</h2>
                <button class="btn" onclick="location.href='/api/v1/projects'">View Projects</button>
                <button class="btn" onclick="location.href='/api/v1/users'">Manage Users</button>
                <button class="btn" onclick="location.href='/api/v1/provision'">Provision Project</button>
            </div>
            
            <div class="section">
                <h2>API Endpoints</h2>
                <ul>
                    <li><strong>GET /api/v1/projects</strong> - List all projects</li>
                    <li><strong>POST /api/v1/projects</strong> - Create new project</li>
                    <li><strong>GET /api/v1/projects/{id}</strong> - Get project details</li>
                    <li><strong>POST /api/v1/provision/{id}</strong> - Provision project</li>
                    <li><strong>GET /api/v1/download/{type}/{id}</strong> - Download startup kit</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@main_bp.route('/test')
def test():
    """Simple test endpoint"""
    return jsonify({'message': 'Backend is working!', 'status': 'ok'})

@api_bp.route('/users', methods=['GET', 'POST', 'OPTIONS'])
def users_api():
    """Users API endpoint"""
    if request.method == 'OPTIONS':
        response = make_response()
        return add_cors_headers(response)
    
    if request.method == 'GET':
        try:
            # Get users (no authentication required for basic listing)
            users = User.query.all()
            response = jsonify({
                'users': [{
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'organization': user.organization,
                    'approval_state': user.approval_state,
                    'is_active': user.is_active
                } for user in users]
            })
            return add_cors_headers(response)
        except Exception as e:
            print(f"Error in GET /users: {e}")
            response = jsonify({'error': 'Internal server error'})
            response.status_code = 500
            return add_cors_headers(response)
    
    elif request.method == 'POST':
        try:
            # Create new user (registration)
            data = request.get_json()
            
            if not data:
                response = jsonify({'error': 'No data provided'})
                response.status_code = 400
                return add_cors_headers(response)
            
            # Validate required fields
            required_fields = ['email', 'name', 'password', 'organization']
            for field in required_fields:
                if not data.get(field):
                    response = jsonify({'error': f'Missing required field: {field}'})
                    response.status_code = 400
                    return add_cors_headers(response)
            
            # Check if user already exists
            if User.query.filter_by(email=data['email']).first():
                response = jsonify({'error': 'User already exists'})
                response.status_code = 400
                return add_cors_headers(response)
            
            # Create new user
            user = User(
                email=data['email'],
                name=data['name'],
                password_hash=generate_password_hash(data['password']),
                organization=data['organization'],
                approval_state=0  # Pending approval
            )
            
            db.session.add(user)
            db.session.commit()
            
            print(f"User created successfully: {user.email}")
            response = jsonify({'message': 'User created successfully', 'user_id': user.id})
            return add_cors_headers(response)
            
        except Exception as e:
            print(f"Error in POST /users: {e}")
            db.session.rollback()
            response = jsonify({'error': 'Internal server error'})
            response.status_code = 500
            return add_cors_headers(response)

@api_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            response = jsonify({'error': 'No data provided'})
            response.status_code = 400
            return add_cors_headers(response)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            response = jsonify({'error': 'Email and password required'})
            response.status_code = 400
            return add_cors_headers(response)
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.email)
            print(f"User logged in successfully: {user.email}")
            response = jsonify({
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role,
                    'organization': user.organization,
                    'approval_state': user.approval_state
                }
            })
            return add_cors_headers(response)
        
        response = jsonify({'error': 'Invalid credentials'})
        response.status_code = 401
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error in login: {e}")
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    """Get all projects"""
    try:
        print("Getting projects...")
        projects = Project.query.all()
        print(f"Found {len(projects)} projects")
        
        project_list = []
        for project in projects:
            try:
                # Get creator information
                creator = User.query.get(project.created_by)
                project_data = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'scheme': project.scheme,
                    'ha_mode': project.ha_mode,
                    'frozen': project.frozen,
                    'public': project.public,
                    'server_name': project.server_name,
                    'created_by': project.created_by,
                    'creator_name': creator.name if creator else 'Unknown',
                    'creator_email': creator.email if creator else 'Unknown',
                    'created_at': project.created_at.isoformat()
                }
                project_list.append(project_data)
                print(f"Processed project: {project.name}")
            except Exception as e:
                print(f"Error processing project {project.id}: {e}")
                continue
        
        print(f"Returning {len(project_list)} projects")
        response = jsonify({'projects': project_list})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error in get_projects: {e}")
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    """Create new project"""
    try:
        print(f"Creating project - request headers: {dict(request.headers)}")
        # Get current user
        current_user_email = get_jwt_identity()
        print(f"Current user email from JWT: {current_user_email}")
        current_user = User.query.filter_by(email=current_user_email).first()
        print(f"Current user found: {current_user}")
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        data = request.get_json()
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            scheme=data.get('scheme', 'grpc'),
            ha_mode=data.get('ha_mode', False),
            frozen=data.get('frozen', False),
            public=data.get('public', False),
            server_name=data.get('server_name', 'FLServer.com'),
            created_by=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        response = jsonify({'message': 'Project created successfully', 'project_id': project.id})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error creating project: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project details"""
    try:
        print(f"Getting project {project_id}")
        project = Project.query.get(project_id)
        if not project:
            print(f"Project {project_id} not found")
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return add_cors_headers(response)
        
        print(f"Found project: {project.name}")
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        print(f"Found {len(servers)} servers, {len(clients)} clients, {len(admins)} admins")
        
        # Get creator information
        creator = User.query.get(project.created_by)
        
        # Check provisioning status
        try:
            provisioning_status = provisioning_service.get_project_status(project_id)
            is_provisioned = provisioning_status and provisioning_status.get('status') == 'provisioned'
        except Exception as e:
            print(f"Error checking provisioning status: {e}")
            is_provisioned = False
        
        response_data = {
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'scheme': project.scheme,
                'ha_mode': project.ha_mode,
                'frozen': project.frozen,
                'public': project.public,
                'server_name': project.server_name,
                'created_by': project.created_by,
                'creator_name': creator.name if creator else 'Unknown',
                'creator_email': creator.email if creator else 'Unknown',
                'created_at': project.created_at.isoformat(),
                'provisioned': is_provisioned
            },
            'servers': [{
                'id': server.id,
                'name': server.name,
                'org': server.org,
                'fed_learn_port': server.fed_learn_port,
                'admin_port': server.admin_port,
                'connection_security': server.connection_security,
                'approval_state': server.approval_state
            } for server in servers],
            'clients': [{
                'id': client.id,
                'name': client.name,
                'org': client.org,
                'description': client.description,
                'num_gpus': client.num_gpus,
                'gpu_memory': client.gpu_memory,
                'approval_state': client.approval_state
            } for client in clients],
            'admins': [{
                'id': admin.id,
                'email': admin.email,
                'org': admin.org,
                'role': admin.role,
                'approval_state': admin.approval_state
            } for admin in admins]
        }
        
        response = jsonify(response_data)
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error getting project {project_id}: {e}")
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update project details - only project creator can update"""
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can update this project'})
            response.status_code = 403
            return response
        
        data = request.get_json()
        
        # Update project fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'scheme' in data:
            project.scheme = data['scheme']
        if 'server_name' in data:
            project.server_name = data['server_name']
        if 'ha_mode' in data:
            project.ha_mode = data['ha_mode']
        if 'frozen' in data:
            project.frozen = data['frozen']
        if 'public' in data:
            project.public = data['public']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Project updated successfully'})
        
    except Exception as e:
        print(f"Error updating project: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

@api_bp.route('/projects/<int:project_id>/servers', methods=['POST'])
@jwt_required()
def add_server(project_id):
    """Add server to project"""
    try:
        data = request.get_json()
        
        if not data:
            response = jsonify({'error': 'No data provided'})
            response.status_code = 400
            return response
        
        # Validate required fields
        required_fields = ['name', 'org']
        for field in required_fields:
            if not data.get(field):
                response = jsonify({'error': f'Missing required field: {field}'})
                response.status_code = 400
                return response
        
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        server = Server(
            project_id=project_id,
            name=data['name'],
            org=data['org'],
            fed_learn_port=data.get('fed_learn_port', 8002),
            admin_port=data.get('admin_port', 8003),
            connection_security=data.get('connection_security', 'mtls'),
            approval_state=1  # Auto-approved for now
        )
        
        db.session.add(server)
        db.session.commit()
        
        print(f"Server added successfully: {server.name}")
        return jsonify({'message': 'Server added successfully', 'server_id': server.id})
        
    except Exception as e:
        print(f"Error adding server: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

@api_bp.route('/projects/<int:project_id>/servers/<int:server_id>', methods=['PUT'])
@jwt_required()
def update_server(project_id, server_id):
    """Update server in project"""
    try:
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project to check ownership
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        data = request.get_json()
        server = Server.query.filter_by(id=server_id, project_id=project_id).first()
        
        if not server:
            response = jsonify({'error': 'Server not found'})
            response.status_code = 404
            return response
    
            server.name = data['name']
        server.org = data['org']
        server.fed_learn_port = data.get('fed_learn_port', 8002)
        server.admin_port = data.get('admin_port', 8003)
        server.connection_security = data.get('connection_security', 'mtls')
        
        db.session.commit()
        return jsonify({'message': 'Server updated successfully'})
        
    except Exception as e:
        print(f"Error updating server: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

@api_bp.route('/projects/<int:project_id>/servers/<int:server_id>', methods=['DELETE'])
@jwt_required()
def delete_server(project_id, server_id):
    """Delete server from project"""
    try:
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project to check ownership
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        server = Server.query.filter_by(id=server_id, project_id=project_id).first()
        
        if not server:
            response = jsonify({'error': 'Server not found'})
            response.status_code = 404
            return response
        
        db.session.delete(server)
        db.session.commit()
        
        print(f"Server {server_id} deleted successfully from project {project_id}")
        response = jsonify({'message': 'Server deleted successfully'})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error deleting server: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>/clients', methods=['POST'])
@jwt_required()
def add_client(project_id):
    """Add client to project"""
    try:
        data = request.get_json()
        
        if not data:
            response = jsonify({'error': 'No data provided'})
            response.status_code = 400
            return response
        
        # Validate required fields
        required_fields = ['name', 'org']
        for field in required_fields:
            if data.get(field) is None or data.get(field) == '':
                response = jsonify({'error': f'Missing required field: {field}'})
                response.status_code = 400
                return response
        
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        client = Client(
            project_id=project_id,
            name=data['name'],
            org=data['org'],
            description=data.get('description', ''),
            num_gpus=data.get('num_gpus', 1),
            gpu_memory=data.get('gpu_memory', 16),
            approval_state=0  # Pending approval
        )
        
        db.session.add(client)
        db.session.commit()
        
        print(f"Client added successfully: {client.name}")
        response = jsonify({'message': 'Client added successfully', 'client_id': client.id})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error adding client: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>/clients/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(project_id, client_id):
    """Update client in project"""
    data = request.get_json()
    client = Client.query.filter_by(id=client_id, project_id=project_id).first()
    
    if not client:
        response = jsonify({'error': 'Client not found'})
        response.status_code = 404
        return response
    
    client.name = data['name']
    client.org = data['org']
    client.description = data.get('description', '')
    client.num_gpus = data.get('num_gpus', 1)
    client.gpu_memory = data.get('gpu_memory', 16)
    
    db.session.commit()
    return jsonify({'message': 'Client updated successfully'})

@api_bp.route('/projects/<int:project_id>/clients/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(project_id, client_id):
    """Delete client from project"""
    try:
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project to check ownership
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        client = Client.query.filter_by(id=client_id, project_id=project_id).first()
        
        if not client:
            response = jsonify({'error': 'Client not found'})
            response.status_code = 404
            return response
        
        db.session.delete(client)
        db.session.commit()
        
        print(f"Client {client_id} deleted successfully from project {project_id}")
        response = jsonify({'message': 'Client deleted successfully'})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error deleting client: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>/admins', methods=['POST'])
@jwt_required()
def add_admin(project_id):
    """Add admin to project"""
    try:
        data = request.get_json()
        
        if not data:
            response = jsonify({'error': 'No data provided'})
            response.status_code = 400
            return response
        
        # Validate required fields
        required_fields = ['email', 'org']
        for field in required_fields:
            if not data.get(field):
                response = jsonify({'error': f'Missing required field: {field}'})
                response.status_code = 400
                return response
        
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        admin = Admin(
            project_id=project_id,
            email=data['email'],
            org=data['org'],
            role=data.get('role', 'project_admin'),
            approval_state=1  # Auto-approved for admins
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin added successfully: {admin.email}")
        response = jsonify({'message': 'Admin added successfully', 'admin_id': admin.id})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error adding admin: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/projects/<int:project_id>/admins/<int:admin_id>', methods=['PUT'])
@jwt_required()
def update_admin(project_id, admin_id):
    """Update admin in project"""
    data = request.get_json()
    admin = Admin.query.filter_by(id=admin_id, project_id=project_id).first()
    
    if not admin:
        response = jsonify({'error': 'Admin not found'})
        response.status_code = 404
        return response
    
    admin.email = data['email']
    admin.org = data['org']
    admin.role = data.get('role', 'project_admin')
    
    db.session.commit()
    return jsonify({'message': 'Admin updated successfully'})

@api_bp.route('/projects/<int:project_id>/admins/<int:admin_id>', methods=['DELETE'])
@jwt_required()
def delete_admin(project_id, admin_id):
    """Delete admin from project"""
    try:
        # Check if user has permission to modify this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project to check ownership
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator or a system admin
        if current_user.role != 'admin' and project.created_by != current_user.id:
            response = jsonify({'error': 'Only the project creator can modify this project'})
            response.status_code = 403
            return response
        
        admin = Admin.query.filter_by(id=admin_id, project_id=project_id).first()
        
        if not admin:
            response = jsonify({'error': 'Admin not found'})
            response.status_code = 404
            return response
        
        db.session.delete(admin)
        db.session.commit()
        
        print(f"Admin {admin_id} deleted successfully from project {project_id}")
        response = jsonify({'message': 'Admin deleted successfully'})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error deleting admin: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

# User Application endpoints
@api_bp.route('/projects/<int:project_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_project(project_id):
    """User applies to join a project"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 404
            return response
        
        data = request.get_json()
        
        # Check if already applied
        existing_application = UserApplication.query.filter_by(
            user_id=user.id, 
            project_id=project_id
        ).first()
        
        if existing_application:
            response = jsonify({'error': 'Already applied to this project'})
            response.status_code = 400
            return response
        
        application = UserApplication(
            user_id=user.id,
            project_id=project_id,
            role_requested=data.get('role_requested', 'user'),
            message=data.get('message', '')
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({'message': 'Application submitted successfully'})
        
    except Exception as e:
        print(f"Error applying to project: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

@api_bp.route('/projects/<int:project_id>/applications', methods=['GET'])
@jwt_required()
def get_project_applications(project_id):
    """Get applications for a project (admin only)"""
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Check if user is admin, project admin, or project creator
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        if user.role not in ['admin', 'project_admin'] and project.created_by != user.id:
            response = jsonify({'error': 'Unauthorized'})
            response.status_code = 403
            return response
        
        applications = UserApplication.query.filter_by(project_id=project_id).all()
        
        result = []
        for app in applications:
            app_user = User.query.get(app.user_id)
            result.append({
                'id': app.id,
                'user_name': app_user.name,
                'user_email': app_user.email,
                'organization': app_user.organization,
                'role_requested': app.role_requested,
                'message': app.message,
                'status': app.status,
                'created_at': app.created_at.isoformat()
            })
        
        response = jsonify({'applications': result})
        return add_cors_headers(response)
        
    except Exception as e:
        print(f"Error getting applications: {e}")
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/applications/<int:application_id>/approve', methods=['POST'])
@jwt_required()
def approve_application(application_id):
    """Approve or reject a user application"""
    try:
        current_user_email = get_jwt_identity()
        admin_user = User.query.filter_by(email=current_user_email).first()
        
        if not admin_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Check if user is admin, project admin, or project creator
        application = UserApplication.query.get(application_id)
        if not application:
            response = jsonify({'error': 'Application not found'})
            response.status_code = 404
            return response
        
        project = Project.query.get(application.project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        if admin_user.role not in ['admin', 'project_admin'] and project.created_by != admin_user.id:
            response = jsonify({'error': 'Unauthorized'})
            response.status_code = 403
            return response
        
        data = request.get_json()
        action = data.get('action')  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            response = jsonify({'error': 'Invalid action'})
            response.status_code = 400
            return response
        
        application = UserApplication.query.get(application_id)
        if not application:
            response = jsonify({'error': 'Application not found'})
            response.status_code = 404
            return response
        
        if action == 'approve':
            application.status = 'approved'
            # Update user approval state
            user = User.query.get(application.user_id)
            user.approval_state = 1
        else:
            application.status = 'rejected'
        
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = admin_user.id
        
        db.session.commit()
        
        return jsonify({'message': f'Application {action}ed successfully'})
        
    except Exception as e:
        print(f"Error processing application: {e}")
        db.session.rollback()
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response

@api_bp.route('/provision/<int:project_id>', methods=['POST'])
@jwt_required()
def provision_project(project_id):
    """Provision a project using NVFlare CLI"""
    try:
        workspace = provisioning_service.call_nvflare_provision(project_id)
        return jsonify({
            'message': 'Project provisioned successfully',
            'workspace': workspace
        })
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response

@api_bp.route('/download/<target_type>/<int:project_id>')
@api_bp.route('/download/<target_type>/<int:project_id>/<int:item_id>')
@jwt_required()
def download_startup_kit(target_type, project_id, item_id=None):
    """Download startup kit for server, client, or admin"""
    try:
        # Check if user has permission to access this project
        current_user_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_user_email).first()
        
        if not current_user:
            response = jsonify({'error': 'User not found'})
            response.status_code = 401
            return response
        
        # Get project to check ownership
        project = Project.query.get(project_id)
        if not project:
            response = jsonify({'error': 'Project not found'})
            response.status_code = 404
            return response
        
        # Check if user is the project creator, system admin, or project participant
        if current_user.role != 'admin' and project.created_by != current_user.id:
            # Check if user is a participant in this project
            is_participant = False
            if target_type == 'server':
                is_participant = Server.query.filter_by(project_id=project_id, org=current_user.organization).first() is not None
            elif target_type == 'client':
                is_participant = Client.query.filter_by(project_id=project_id, org=current_user.organization).first() is not None
            elif target_type == 'admin':
                is_participant = Admin.query.filter_by(project_id=project_id, email=current_user.email).first() is not None
            
            if not is_participant:
                response = jsonify({'error': 'Unauthorized to access this project'})
                response.status_code = 403
                return response
        
        if item_id:
            # Download specific item startup kit
            zip_buffer, filename = provisioning_service.generate_item_startup_kit(project_id, target_type, item_id)
        else:
            # Download general startup kit
            zip_buffer, filename = provisioning_service.generate_startup_kit(project_id, target_type)
        
        return send_file(
            io.BytesIO(zip_buffer.getvalue()),
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return add_cors_headers(response)

@api_bp.route('/status/<int:project_id>')
@jwt_required()
def get_project_status(project_id):
    """Get project provisioning status"""
    try:
        status = provisioning_service.get_project_status(project_id)
        return jsonify(status)
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response

