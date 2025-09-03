#!/usr/bin/env python3
"""
Database Models for Sorachain Provisioning Dashboard
"""

from datetime import datetime
from . import db

class CommonMixin(object):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), default="")
    description = db.Column(db.String(512), default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def asdict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Organization(CommonMixin, db.Model):
    def asdict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in ("name",)}

class Role(CommonMixin, db.Model):
    pass

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
    props = db.Column(db.String(1048), default="")  # additional properties - JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Additional attributes from NVFlare models
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    organization_rel = db.relationship("Organization", backref="users")
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    role_rel = db.relationship("Role", backref="users")

class Project(db.Model):
    """Project configuration model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    short_name = db.Column(db.String(128), default="")
    title = db.Column(db.String(512), default="")
    description = db.Column(db.String(2048), default="")
    api_version = db.Column(db.Integer, default=3)
    scheme = db.Column(db.String(64), default='agrpc')
    server_name = db.Column(db.String(128), nullable=False, default='')
    server1 = db.Column(db.String(128), default="")
    server2 = db.Column(db.String(128), default="")
    app_location = db.Column(db.String(2048), default="")
    overseer = db.Column(db.String(128), default="")
    overseer_agent_path = db.Column(db.String(512), default="nvflare.ha.dummy_overseer_agent.DummyOverseerAgent")
    overseer_agent_args = db.Column(db.String(2048), default='{"sp_end_point": "FLServer.com:8002:8003"}')
    root_cert = db.Column(db.String(4096), default="")
    root_key = db.Column(db.String(4096), default="")
    project_props = db.Column(db.String(2048), default="")  # additional project properties - JSON string
    server_props = db.Column(db.String(2048), default="")  # additional server properties - JSON string
    cc_mode = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ha_mode = db.Column(db.Boolean, default=False)
    frozen = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    starting_date = db.Column(db.String(128), default="")
    end_date = db.Column(db.String(128), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional attributes from NVFlare models
    # overseer_agent_path and overseer_agent_args already defined above

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
    
    # Additional attributes from NVFlare models
    props = db.Column(db.String(2048), default="")  # additional properties - JSON string

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
    capacity = db.Column(db.String(2048), default="")  # JSON string for capacity info
    props = db.Column(db.String(2048), default="")  # additional properties - JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional attributes from NVFlare models
    organization_id = db.Column(db.Integer, db.ForeignKey("organization.id"), nullable=False)
    organization = db.relationship("Organization", backref="clients")
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

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
            # Create default organization and role first
            default_org = Organization(name='example', description='Default Organization')
            db.session.add(default_org)
            db.session.flush()
            
            default_role = Role(name='admin', description='Administrator Role')
            db.session.add(default_role)
            db.session.flush()
            
            # Create default admin user
            from werkzeug.security import generate_password_hash
            admin_user = User(
                email='admin@example.com',
                name='Admin User',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                organization='example',
                approval_state=1,
                organization_id=default_org.id,
                role_id=default_role.id
            )
            db.session.add(admin_user)
            db.session.flush()  # Get the admin user ID first
            
            # Create default project
            project = Project(
                name='Example Sorachain Project',
                short_name='example',
                title='Example Sorachain Project',
                description='Default Sorachain project',
                scheme='agrpc',
                        server_name='',
        server1='',
                app_location='nvflare/nvflare',
                overseer_agent_path='nvflare.ha.dummy_overseer_agent.DummyOverseerAgent',
                overseer_agent_args='{"sp_end_point": "server:8002:8003"}',
                created_by=admin_user.id
            )
            db.session.add(project)
            db.session.flush()  # Get the project ID
            
            # Create default server
            server = Server(
                project_id=project.id,
                name='default-server',
                org='example',
                fed_learn_port=8002,
                admin_port=8003,
                connection_security='mtls',
                approval_state=1
            )
            db.session.add(server)
            
            # Create default client
            client = Client(
                project_id=project.id,
                name='site-1',
                org='example',
                description='Default client',
                num_gpus=1,
                gpu_memory=16,
                approval_state=1,
                organization_id=default_org.id,
                creator_id=admin_user.id
            )
            db.session.add(client)
            
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


