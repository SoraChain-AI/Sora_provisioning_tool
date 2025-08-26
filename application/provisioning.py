#!/usr/bin/env python3
"""
NVFlare Provisioning Service
Integrates with the NVFlare CLI provisioning tool
"""

import os
import tempfile
import subprocess
import yaml
import json
import zipfile
import io
from pathlib import Path
from .models import Project, Server, Client, Admin

class NVFlareProvisioningService:
    """Service for generating NVFlare project configurations and calling the CLI"""
    
    def __init__(self, workspace_dir="workspace"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def generate_project_yml(self, project_id):
        """Generate project.yml file from database configuration"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        # NVFlare only supports one server per project, so we'll use the first server
        if not servers:
            raise ValueError(f"Project {project_id} must have at least one server")
        
        primary_server = servers[0]  # Use the first server as primary
        
        # Build project configuration with only the primary server
        project_config = {
            'api_version': project.api_version,
            'name': project.name,
            'description': project.description,
            'participants': [
                {
                    'name': project.server_name,
                    'type': 'server',
                    'org': primary_server.org,
                    'fed_learn_port': primary_server.fed_learn_port,
                    'admin_port': primary_server.admin_port
                }
            ],
            'builders': [
                {
                    'path': 'nvflare.lighter.impl.workspace.WorkspaceBuilder',
                    'args': {
                        'template_file': ['master_template.yml']  # Use only master template
                    }
                },
                {
                    'path': 'nvflare.lighter.impl.static_file.StaticFileBuilder',
                    'args': {
                        'config_folder': 'config',
                        'scheme': project.scheme,
                        'overseer_agent': {
                            'path': 'nvflare.ha.dummy_overseer_agent.DummyOverseerAgent',
                            'overseer_exists': False,
                            'args': {
                                'sp_end_point': f"{project.server_name}:8002:8003"
                            }
                        }
                    }
                },
                {
                    'path': 'nvflare.lighter.impl.cert.CertBuilder',
                    'args': {}
                },
                {
                    'path': 'nvflare.lighter.impl.signature.SignatureBuilder',
                    'args': {}
                }
            ]
        }
        
        return project_config, {
            'additional_servers': servers[1:] if len(servers) > 1 else [],
            'clients': clients,
            'admins': admins
        }
    
    def call_nvflare_provision(self, project_id, custom_workspace=None):
        """Call the NVFlare CLI provision command"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Generate project.yml with primary server only
        project_config, additional_participants = self.generate_project_yml(project_id)
        print(f"Generated project config: {project_config}")
        
        # Create temporary project.yml file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(project_config, f, default_flow_style=False)
            project_file = f.name
        
        print(f"Created temporary project file: {project_file}")
        
        try:
            # Determine workspace directory
            workspace = custom_workspace or os.path.join(self.workspace_dir, f"project_{project_id}")
            print(f"Target workspace: {workspace}")
            
            # Call nvflare provision command for the primary server
            cmd = [
                '/home/franky/FL/bin/nvflare', 'provision',
                '-p', project_file,
                '-w', workspace
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Environment PATH: {os.environ.get('PATH', 'Not set')}")
            
            # Ensure the virtual environment is in the PATH
            env = os.environ.copy()
            if '/home/franky/FL/bin' not in env.get('PATH', ''):
                env['PATH'] = '/home/franky/FL/bin:' + env.get('PATH', '')
                print(f"Updated PATH: {env['PATH']}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                env=env
            )
            
            print(f"Command return code: {result.returncode}")
            print(f"Command stdout: {result.stdout}")
            print(f"Command stderr: {result.stderr}")
            
            if result.returncode != 0:
                raise RuntimeError(f"NVFlare provision failed: {result.stderr}")
            
            print(f"Provisioning successful. Workspace: {workspace}")
            
            # Check if workspace directory exists
            if not os.path.exists(workspace):
                print(f"Warning: Workspace directory {workspace} does not exist after command execution")
                # List contents of parent directory
                parent_dir = os.path.dirname(workspace)
                if os.path.exists(parent_dir):
                    print(f"Contents of {parent_dir}: {os.listdir(parent_dir)}")
                return workspace
            
            # Find the actual workspace directory created by NVFlare
            # NVFlare creates a nested structure: workspace/Project Name/prod_00/
            actual_workspace = None
            print(f"Searching for generated workspace in: {workspace}")
            if os.path.exists(workspace):
                print(f"Workspace directory exists, contents: {os.listdir(workspace)}")
                for item in os.listdir(workspace):
                    project_dir = os.path.join(workspace, item)
                    print(f"Checking item: {item} -> {project_dir}")
                    if os.path.isdir(project_dir):
                        prod_dir = os.path.join(project_dir, 'prod_00')
                        print(f"Checking for prod_00: {prod_dir}")
                        if os.path.exists(prod_dir):
                            actual_workspace = prod_dir
                            print(f"Found prod_00 directory: {actual_workspace}")
                            break
            else:
                print(f"Workspace directory {workspace} does not exist")
            
            if not actual_workspace:
                print(f"Could not find generated workspace in {workspace}")
                # Return the base workspace for now
                return workspace
            
            print(f"Actual workspace found: {actual_workspace}")
            
            # Now add additional participants using the appropriate flags
            self._add_additional_participants(actual_workspace, additional_participants)
            
            return actual_workspace
            
        finally:
            # Clean up temporary file
            os.unlink(project_file)
            print(f"Cleaned up temporary file: {project_file}")
    
    def _add_additional_participants(self, workspace, additional_participants):
        """Add additional participants to the provisioned workspace"""
        print(f"Adding additional participants to {workspace}")
        
        # Add additional clients
        for client in additional_participants['clients']:
            self._add_client(workspace, client)
        
        # Add additional admins
        for admin in additional_participants['admins']:
            self._add_user(workspace, admin)
        
        # Note: Additional servers are not supported by NVFlare
        if additional_participants['additional_servers']:
            print(f"Warning: {len(additional_participants['additional_servers'])} additional servers cannot be added (NVFlare limitation)")
    
    def _add_client(self, workspace, client):
        """Add a client to the provisioned workspace"""
        try:
            # Create client configuration
            client_config = {
                'name': client.name,
                'type': 'client',
                'org': client.org
            }
            if client.description:
                client_config['description'] = client.description
            
            # Create temporary client file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                yaml.dump(client_config, f, default_flow_style=False)
                client_file = f.name
            
            try:
                # Add client using NVFlare
                cmd = [
                    '/home/franky/FL/bin/nvflare', 'provision',
                    '--add_client', client_file,
                    '-w', workspace
                ]
                
                print(f"Adding client {client.name}: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=os.environ.copy()
                )
                
                if result.returncode == 0:
                    print(f"Successfully added client {client.name}")
                else:
                    print(f"Failed to add client {client.name}: {result.stderr}")
                    
            finally:
                os.unlink(client_file)
                
        except Exception as e:
            print(f"Error adding client {client.name}: {e}")
    
    def _add_user(self, workspace, admin):
        """Add an admin user to the provisioned workspace"""
        try:
            # Create user configuration
            user_config = {
                'name': admin.email.split('@')[0],
                'type': 'admin',
                'org': admin.org,
                'role': admin.role
            }
            
            # Create temporary user file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                yaml.dump(user_config, f, default_flow_style=False)
                user_file = f.name
            
            try:
                # Add user using NVFlare
                cmd = [
                    '/home/franky/FL/bin/nvflare', 'provision',
                    '--add_user', user_file,
                    '-w', workspace
                ]
                
                print(f"Adding user {admin.email}: {' '.join(cmd)}")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd(),
                    env=os.environ.copy()
                )
                
                if result.returncode == 0:
                    print(f"Successfully added user {admin.email}")
                else:
                    print(f"Failed to add user {admin.email}: {result.stderr}")
                    
            finally:
                os.unlink(user_file)
                
        except Exception as e:
            print(f"Error adding user {admin.email}: {e}")
    
    def generate_startup_kit(self, project_id, target_type='server'):
        """Generate startup kit for server, client, or admin"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Call provisioning first
        workspace = self.call_nvflare_provision(project_id)
        
        # Find the target directory
        if target_type == 'server':
            # Look for server directory (usually named after the server)
            for item in os.listdir(workspace):
                if os.path.isdir(os.path.join(workspace, item)) and not item.startswith('site-') and not item.endswith('@'):
                    # This should be the server directory
                    target_dir = os.path.join(workspace, item)
                    break
            else:
                raise RuntimeError("No server directory found")
        elif target_type == 'client':
            # Find client directory (usually starts with 'site-')
            for item in os.listdir(workspace):
                if item.startswith('site-'):
                    target_dir = os.path.join(workspace, item)
                    break
            else:
                raise RuntimeError("No client directory found")
        elif target_type == 'admin':
            # Find admin directory (usually ends with '@')
            for item in os.listdir(workspace):
                if item.endswith('@'):
                    target_dir = os.path.join(workspace, item)
                    break
            else:
                raise RuntimeError("No admin directory found")
        else:
            raise ValueError(f"Invalid target type: {target_type}")
        
        if not os.path.exists(target_dir):
            raise RuntimeError(f"Target directory {target_dir} not found")
        
        print(f"Creating startup kit for {target_type} from {target_dir}")
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, target_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer, f"{target_type}_startup_kit.zip"
    
    def get_project_status(self, project_id):
        """Get the status of a project provisioning"""
        project = Project.query.get(project_id)
        if not project:
            return None
        
        workspace = os.path.join(self.workspace_dir, f"project_{project_id}")
        
        if not os.path.exists(workspace):
            return {'status': 'not_provisioned'}
        
        # Check what's in the workspace
        items = os.listdir(workspace)
        
        return {
            'status': 'provisioned',
            'workspace': workspace,
            'items': items,
            'last_updated': project.updated_at.isoformat()
        }


