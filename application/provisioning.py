#!/usr/bin/env python3
"""
NVFlare Provisioning Service
Integrates with the NVFlare CLI provisioning tool using proper workflow
"""

import os
import tempfile
import subprocess
import yaml
import json
import zipfile
import io
import shutil
from pathlib import Path
from .models import Project, Server, Client, Admin

class NVFlareProvisioningService:
    """Service for generating NVFlare project configurations and calling the CLI"""
    
    def __init__(self, workspace_dir="workspace"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def _load_base_config(self):
        """Load the base project.yml configuration"""
        base_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'project.yml')
        if not os.path.exists(base_config_path):
            # Fallback to creating a basic config
            return self._create_basic_config()
        
        with open(base_config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_basic_config(self):
        """Create a basic NVFlare configuration if base config doesn't exist"""
        return {
            'api_version': 3,
            'name': 'sorachain_project',
            'description': 'Sorachain Federated Learning Project',
            'participants': [],
            'builders': [
                {
                    'path': 'nvflare.lighter.impl.workspace.WorkspaceBuilder',
                    'args': {
                        'template_file': ['master_template.yml']
                    }
                },
                {
                    'path': 'nvflare.lighter.impl.static_file.StaticFileBuilder',
                    'args': {
                        'config_folder': 'config',
                        'scheme': 'grpc',
                        'overseer_agent': {
                            'path': 'nvflare.ha.dummy_overseer_agent.DummyOverseerAgent',
                            'overseer_exists': False,
                            'args': {
                                'sp_end_point': 'FLServer:8002:8003'
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
    
    def _update_base_config(self, base_config, project, servers, clients, admins):
        """Update base configuration with project-specific details"""
        # Update project metadata
        base_config['name'] = project.name
        base_config['description'] = project.description
        
        # Clear existing participants and add new ones
        base_config['participants'] = []
        
        # Add servers
        for server in servers:
            base_config['participants'].append({
                'name': server.name,
                'host': server.name,
                'type': 'server',
                'org': server.org,
                'fed_learn_port': server.fed_learn_port,
                'admin_port': server.admin_port
            })
        
        # Add clients
        for client in clients:
            base_config['participants'].append({
                'name': client.name,
                'host': client.name,
                'type': 'client',
                'org': client.org
            })
        
        # Add admins
        for admin in admins:
            base_config['participants'].append({
                'name': admin.email,
                'host': servers[0].name if servers else 'FLServer',
                'type': 'admin',
                'org': admin.org,
                'role': admin.role
            })
        
        # Update overseer agent endpoint if servers exist
        if servers:
            primary_server = servers[0]
            for builder in base_config['builders']:
                if builder.get('path') == 'nvflare.lighter.impl.static_file.StaticFileBuilder':
                    if 'overseer_agent' in builder.get('args', {}):
                        builder['args']['overseer_agent']['args']['sp_end_point'] = f"{primary_server.name}:{primary_server.fed_learn_port}:{primary_server.admin_port}"
        
        return base_config
    
    def call_nvflare_provision(self, project_id, custom_workspace=None, force_reprovision=False):
        """Call the NVFlare CLI provision command using base config + updates"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Check if already provisioned and not forcing reprovision
        if not force_reprovision:
            existing_workspace = self._get_existing_workspace(project_id)
            if existing_workspace:
                print(f"Project {project_id} already provisioned, using existing workspace: {existing_workspace}")
                return existing_workspace
        
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        if not servers:
            raise ValueError(f"Project {project_id} must have at least one server")
        
        # Load base configuration
        base_config = self._load_base_config()
        print(f"Loaded base config: {base_config['name']}")
        
        # Update with project-specific details
        project_config = self._update_base_config(base_config, project, servers, clients, admins)
        print(f"Updated project config: {project_config['name']}")
        print(f"Participants: {len(project_config['participants'])} total")
        
        # Create temporary project.yml file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(project_config, f, default_flow_style=False)
            project_file = f.name
        
        print(f"Created temporary project file: {project_file}")
        
        try:
            # Determine workspace directory
            workspace = custom_workspace or os.path.join(self.workspace_dir, f"project_{project_id}")
            print(f"Target workspace: {workspace}")
            
            # Call nvflare provision command - this will generate ALL configs together
            cmd = [
                '/home/franky/FL/bin/nvflare', 'provision',
                '-p', project_file,
                '-w', workspace
            ]
            
            print(f"Executing: {' '.join(cmd)}")
            print(f"Current working directory: {os.getcwd()}")
            
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
            print(f"Workspace contents: {os.listdir(actual_workspace)}")
            return actual_workspace
            
        finally:
            # Clean up temporary file
            os.unlink(project_file)
            print(f"Cleaned up temporary file: {project_file}")
    
    def _get_existing_workspace(self, project_id):
        """Get existing workspace if project is already provisioned"""
        workspace = os.path.join(self.workspace_dir, f"project_{project_id}")
        if not os.path.exists(workspace):
            return None
        
        # Look for the prod_00 directory
        for item in os.listdir(workspace):
            project_dir = os.path.join(workspace, item)
            if os.path.isdir(project_dir):
                prod_dir = os.path.join(project_dir, 'prod_00')
                if os.path.exists(prod_dir):
                    return prod_dir
        
        return None
    
    def generate_startup_kit(self, project_id, target_type='server'):
        """Generate startup kit for server, client, or admin"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Call provisioning first (use existing if available)
        workspace = self.call_nvflare_provision(project_id, force_reprovision=False)
        
        # Find the target directory based on actual NVFlare output structure
        if target_type == 'server':
            # Look for server directory - usually ends with .com or .org
            for item in os.listdir(workspace):
                item_path = os.path.join(workspace, item)
                if (os.path.isdir(item_path) and 
                    (item.endswith('.com') or item.endswith('.org'))):
                    target_dir = item_path
                    break
            else:
                # Fallback: look for any directory that might be the server
                for item in os.listdir(workspace):
                    item_path = os.path.join(workspace, item)
                    if (os.path.isdir(item_path) and 
                        not item.startswith('site-') and 
                        not '@' in item):
                        target_dir = item_path
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
            # Find admin directory (usually contains @ symbol)
            for item in os.listdir(workspace):
                if '@' in item:
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
    
    def generate_item_startup_kit(self, project_id, target_type, item_id):
        """Generate startup kit for a specific server, client, or admin"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Call provisioning first if not already done (use existing if available)
        workspace = self.call_nvflare_provision(project_id, force_reprovision=False)
        
        # Find the specific item directory based on actual NVFlare output structure
        if target_type == 'server':
            server = Server.query.get(item_id)
            if not server or server.project_id != project_id:
                raise ValueError(f"Server {item_id} not found in project {project_id}")
            
            # Look for server directory - usually ends with .com or .org
            for item in os.listdir(workspace):
                item_path = os.path.join(workspace, item)
                if (os.path.isdir(item_path) and 
                    (item.endswith('.com') or item.endswith('.org'))):
                    target_dir = item_path
                    break
            else:
                # Fallback: look for any directory that might be the server
                for item in os.listdir(workspace):
                    item_path = os.path.join(workspace, item)
                    if (os.path.isdir(item_path) and 
                        not item.startswith('site-') and 
                        not '@' in item):
                        target_dir = item_path
                        break
                else:
                    raise RuntimeError("No server directory found")
                
        elif target_type == 'client':
            client = Client.query.get(item_id)
            if not client or client.project_id != project_id:
                raise ValueError(f"Client {item_id} not found in project {project_id}")
            
            # Find client directory (usually starts with 'site-')
            for item in os.listdir(workspace):
                if item.startswith('site-'):
                    target_dir = os.path.join(workspace, item)
                    break
            else:
                raise RuntimeError("No client directory found")
                
        elif target_type == 'admin':
            admin = Admin.query.get(item_id)
            if not admin or admin.project_id != project_id:
                raise ValueError(f"Admin {item_id} not found in project {project_id}")
            
            # Find admin directory (usually contains @ symbol)
            for item in os.listdir(workspace):
                if '@' in item:
                    target_dir = os.path.join(workspace, item)
                    break
            else:
                raise RuntimeError("No admin directory found")
        else:
            raise ValueError(f"Invalid target type: {target_type}")
        
        if not os.path.exists(target_dir):
            raise RuntimeError(f"Target directory {target_dir} not found")
        
        print(f"Creating startup kit for {target_type} {item_id} from {target_dir}")
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, target_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer, f"{target_type}_{item_id}_startup_kit.zip"
    
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
    
    def force_reprovision(self, project_id):
        """Force reprovisioning of a project (useful when participants change)"""
        try:
            # Remove existing workspace
            workspace = os.path.join(self.workspace_dir, f"project_{project_id}")
            if os.path.exists(workspace):
                shutil.rmtree(workspace)
                print(f"Removed existing workspace: {workspace}")
            
            # Provision again
            return self.call_nvflare_provision(project_id, force_reprovision=True)
        except Exception as e:
            print(f"Error during force reprovision: {e}")
            raise

    def generate_all_startup_kits(self, project_id):
        """Generate startup kits for all participants in a project"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Ensure project is provisioned
        workspace = self.call_nvflare_provision(project_id, force_reprovision=False)
        
        print(f"Generating all startup kits for project {project_id} from workspace: {workspace}")
        print(f"Workspace contents: {os.listdir(workspace)}")
        
        # Get all participants
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        print(f"Found {len(servers)} servers, {len(clients)} clients, {len(admins)} admins")
        
        startup_kits = {}
        
        # Generate server startup kits
        for server in servers:
            try:
                print(f"Generating server kit for {server.name} (ID: {server.id})")
                server_kit, filename = self.generate_item_startup_kit(project_id, 'server', server.id)
                startup_kits[f'server_{server.id}'] = {
                    'name': server.name,
                    'filename': filename,
                    'data': server_kit
                }
                print(f"Successfully generated server kit for {server.name}")
            except Exception as e:
                print(f"Error generating server kit for {server.name}: {e}")
                # Continue with other kits instead of failing completely
        
        # Generate client startup kits
        for client in clients:
            try:
                print(f"Generating client kit for {client.name} (ID: {client.id})")
                client_kit, filename = self.generate_item_startup_kit(project_id, 'client', client.id)
                startup_kits[f'client_{client.id}'] = {
                    'name': client.name,
                    'filename': filename,
                    'data': client_kit
                }
                print(f"Successfully generated client kit for {client.name}")
            except Exception as e:
                print(f"Error generating client kit for {client.name}: {e}")
                # Continue with other kits instead of failing completely
        
        # Generate admin startup kits
        for admin in admins:
            try:
                print(f"Generating admin kit for {admin.email} (ID: {admin.id})")
                admin_kit, filename = self.generate_item_startup_kit(project_id, 'admin', admin.id)
                startup_kits[f'admin_{admin.id}'] = {
                    'name': admin.email,
                    'filename': filename,
                    'data': admin_kit
                }
                print(f"Successfully generated admin kit for {admin.email}")
            except Exception as e:
                print(f"Error generating admin kit for {admin.email}: {e}")
                # Continue with other kits instead of failing completely
        
        print(f"Generated {len(startup_kits)} startup kits successfully")
        
        if not startup_kits:
            raise RuntimeError("No startup kits could be generated")
        
        return startup_kits


