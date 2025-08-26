#!/usr/bin/env python3
"""
Database Models for Sorachain Provisioning Dashboard
"""

from datetime import datetime
from . import db

class User(db.Model):
    """User model for authentication and authorization"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(64), default='user')  # admin, user, org_admin, proj_admin
    organization = db.Column(db.String(128), nullable=False)
    approval_state = db.Column(db.Integer, default=0)  # 0: pending, 1: approved, 2: rejected
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Project(db.Model):
    """Project configuration model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512))
    api_version = db.Column(db.Integer, default=3)
    scheme = db.Column(db.String(64), default='grpc')
    server_name = db.Column(db.String(128), nullable=False, default='FLServer.com')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ha_mode = db.Column(db.Boolean, default=False)
    frozen = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Server(db.Model):
    """Server configuration model"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    org = db.Column(db.String(128), nullable=False)
    fed_learn_port = db.Column(db.Integer, default=8002)
    admin_port = db.Column(db.Integer, default=8003)
    connection_security = db.Column(db.String(64), default='mtls')  # mtls, tls, none
    approval_state = db.Column(db.Integer, default=1)  # 0: pending, 1: approved, 2: rejected
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Client(db.Model):
    """Client configuration model"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    org = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512))
    num_gpus = db.Column(db.Integer, default=1)
    gpu_memory = db.Column(db.Integer, default=16)  # GB
    approval_state = db.Column(db.Integer, default=0)  # 0: pending, 1: approved, 2: rejected
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    """Admin configuration model"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    org = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), default='project_admin')
    approval_state = db.Column(db.Integer, default=1)  # 0: pending, 1: approved, 2: rejected
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserApplication(db.Model):
    """User application to join projects"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    role_requested = db.Column(db.String(64), default='user')  # user, client, admin
    message = db.Column(db.String(512))
    status = db.Column(db.String(64), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))

def init_default_data():
    """Initialize default data if database is empty"""
    try:
        if not User.query.first():
            # Create default admin user
            from werkzeug.security import generate_password_hash
            admin_user = User(
                email='admin@example.com',
                name='Admin User',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                organization='example',
                approval_state=1
            )
            db.session.add(admin_user)
            db.session.flush()  # Get the admin user ID first
            
            # Create default project
            project = Project(
                name='Example Sorachain Project',
                description='Default Sorachain project',
                scheme='grpc',
                server_name='FLServer.com',
                created_by=admin_user.id
            )
            db.session.add(project)
            db.session.flush()  # Get the project ID
            
            # Create default server
            server = Server(
                project_id=project.id,
                name='FLServer.com',
                org='example',
                fed_learn_port=8002,
                admin_port=8003,
                connection_security='mtls',
                approval_state=1
            )
            db.session.add(server)
            
            # Create default admin
            admin = Admin(
                project_id=project.id,
                email='admin@example.com',
                org='example',
                role='project_admin',
                approval_state=1
            )
            db.session.add(admin)
            
            db.session.commit()
            print("Default data initialized successfully")
    except Exception as e:
        print(f"Error initializing default data: {e}")
        db.session.rollback()


