#!/usr/bin/env python3
"""
NVFlare Provisioning Configuration Generator
Generates project.yml files dynamically based on dashboard project data
"""

import yaml
import json
import os
from datetime import datetime
from .models import Project, Server, Client, Admin, User, Organization

class ProvisioningConfigGenerator:
    """Generates SoraChain provisioning configuration files"""
    
    def __init__(self, output_dir="config"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_project_config(self, project_id, output_filename=None):
        """Generate a complete project.yml configuration for a given project"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get all participants for this project
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        if not servers:
            raise ValueError(f"Project {project_id} must have at least one server")
        
        # Build the configuration
        config = self._build_base_config(project)
        config['participants'] = self._build_participants(servers, clients, admins)
        config['builders'] = self._build_builders(project, servers[0])
        
        # Add project-specific properties
        if project.project_props:
            try:
                project_props = json.loads(project.project_props)
                config['project_props'] = project_props
            except json.JSONDecodeError:
                config['project_props'] = {}
        
        # Add server-specific properties
        if project.server_props:
            try:
                server_props = json.loads(project.server_props)
                config['server_props'] = server_props
            except json.JSONDecodeError:
                config['server_props'] = {}
        
        # Determine output filename
        if not output_filename:
            safe_name = project.short_name or project.name.replace(' ', '_').lower()
            output_filename = f"{safe_name}_project.yml"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Write the configuration file
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated provisioning configuration: {output_path}")
        return output_path
    
    def _build_base_config(self, project):
        """Build the base configuration structure"""
        return {
            'api_version': getattr(project, 'api_version', 3),
            'name': project.name,
            'description': project.description or f"Federated Learning Project: {project.name}",
            'created_at': project.created_at.isoformat() if project.created_at else datetime.utcnow().isoformat(),
            'scheme': project.scheme or 'grpc',
            'ha_mode': getattr(project, 'ha_mode', False),
            'cc_mode': getattr(project, 'cc_mode', False),
            'frozen': getattr(project, 'frozen', False),
            'public': getattr(project, 'public', False),
        }
    
    def _build_participants(self, servers, clients, admins):
        """Build the participants section"""
        participants = []
        
        # Add servers
        for server in servers:
            server_config = {
                'name': server.name,
                'host': server.name,
                'type': 'server',
                'org': server.org,
                'fed_learn_port': server.fed_learn_port,
                'admin_port': server.admin_port,
            }
            
            # Add server properties
            if hasattr(server, 'props') and server.props:
                try:
                    server_config['props'] = json.loads(server.props)
                except json.JSONDecodeError:
                    server_config['props'] = {}
            
            # Add connection security
            if hasattr(server, 'connection_security'):
                if 'props' not in server_config:
                    server_config['props'] = {}
                server_config['props']['connection_security'] = server.connection_security
            
            participants.append(server_config)
        
        # Add clients
        for client in clients:
            client_config = {
                'name': client.name,
                'type': 'client',
                'org': client.org,
            }
            
            # Add client properties
            if client.props:
                try:
                    client_config['props'] = json.loads(client.props)
                except json.JSONDecodeError:
                    client_config['props'] = {}
            
            # Add capacity information
            if client.capacity:
                try:
                    capacity = json.loads(client.capacity)
                    if 'props' not in client_config:
                        client_config['props'] = {}
                    client_config['props']['capacity'] = capacity
                except json.JSONDecodeError:
                    pass
            
            # Add description
            if client.description:
                if 'props' not in client_config:
                    client_config['props'] = {}
                client_config['props']['description'] = client.description
            
            participants.append(client_config)
        
        # Add admins
        for admin in admins:
            admin_config = {
                'name': admin.email,
                'host': servers[0].name if servers else 'FLServer.com',
                'type': 'admin',
                'org': admin.org,
                'role': admin.role,
            }
            
            participants.append(admin_config)
        
        return participants
    
    def _build_builders(self, project, primary_server):
        """Build the builders configuration"""
        builders = [
            {
                'path': 'nvflare.lighter.impl.workspace.WorkspaceBuilder',
                'args': {
                    'template_file': ['master_template.yml']
                }
            },
            {
                'path': 'nvflare.lighter.impl.template.TemplateBuilder'
            },
            {
                'path': 'nvflare.lighter.impl.static_file.StaticFileBuilder',
                'args': {
                    'config_folder': 'config',
                    'scheme': project.scheme or 'grpc',
                    'docker_image': project.app_location or 'nvflare/nvflare',
                    'overseer_agent': {
                        'path': project.overseer_agent_path or 'nvflare.ha.dummy_overseer_agent.DummyOverseerAgent',
                        'overseer_exists': False,
                        'args': {
                            'sp_end_point': f"{primary_server.name}:{primary_server.fed_learn_port}:{primary_server.admin_port}"
                        }
                    }
                }
            },
            {
                'path': 'nvflare.lighter.impl.cert.CertBuilder'
            },
            {
                'path': 'nvflare.lighter.impl.signature.SignatureBuilder'
            }
        ]
        
        # Add Docker builder if app_location is specified
        if project.app_location and 'docker' in project.app_location.lower():
            builders.insert(3, {
                'path': 'nvflare.lighter.impl.docker.DockerBuilder',
                'args': {
                    'base_image': 'python:3.10',
                    'requirements_file': 'requirements.txt'
                }
            })
        
        return builders
    
    def generate_template_config(self, template_name="sorachain_template"):
        """Generate a template configuration file"""
        template_config = {
            'name': template_name,
            'description': f'Sorachain {template_name} configuration',
            'variables': {
                'project_name': '${project.name}',
                'project_description': '${project.description}',
                'server_name': '${server.name}',
                'client_name': '${client.name}',
                'admin_email': '${admin.email}',
                'org_name': '${org.name}'
            },
            'files': [
                {
                    'src': 'templates/server/fed_server.json',
                    'dest': '${server.name}/fed_server.json'
                },
                {
                    'src': 'templates/client/fed_client.json',
                    'dest': '${client.name}/fed_client.json'
                },
                {
                    'src': 'templates/admin/fed_admin.json',
                    'dest': '${admin.email}/fed_admin.json'
                }
            ]
        }
        
        output_path = os.path.join(self.output_dir, f"{template_name}.yml")
        with open(output_path, 'w') as f:
            yaml.dump(template_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Generated template configuration: {output_path}")
        return output_path
    
    def generate_all_project_configs(self):
        """Generate configurations for all projects in the database"""
        projects = Project.query.all()
        generated_files = []
        
        for project in projects:
            try:
                output_path = self.generate_project_config(project.id)
                generated_files.append(output_path)
            except Exception as e:
                print(f"Error generating config for project {project.id}: {e}")
        
        print(f"Generated {len(generated_files)} configuration files")
        return generated_files
    
    def validate_config(self, config_path):
        """Validate a generated configuration file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Basic validation
            required_fields = ['api_version', 'name', 'participants', 'builders']
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"
            
            # Validate participants
            if not config['participants']:
                return False, "No participants defined"
            
            # Validate builders
            if not config['builders']:
                return False, "No builders defined"
            
            return True, "Configuration is valid"
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def generate_deployment_script(self, project_id, output_filename=None):
        """Generate a deployment script for the project"""
        project = Project.query.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        if not output_filename:
            safe_name = project.short_name or project.name.replace(' ', '_').lower()
            output_filename = f"deploy_{safe_name}.sh"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        script_content = f"""#!/bin/bash
# Deployment script for {project.name}
# Generated on {datetime.utcnow().isoformat()}

set -e

echo "Deploying {project.name}..."

# Check if NVFlare is available
if ! command -v nvflare &> /dev/null; then
    echo "Error: NVFlare CLI not found. Please install NVFlare first."
    exit 1
fi

# Set project configuration file
PROJECT_CONFIG="{os.path.basename(self.generate_project_config(project_id))}"
WORKSPACE_DIR="workspace/project_{project_id}"

echo "Using project configuration: $PROJECT_CONFIG"
echo "Target workspace: $WORKSPACE_DIR"

# Create workspace directory
mkdir -p "$WORKSPACE_DIR"

# Run NVFlare provision
echo "Running NVFlare provision..."
nvflare provision -p "$PROJECT_CONFIG" -w "$WORKSPACE_DIR"

if [ $? -eq 0 ]; then
    echo "Provisioning completed successfully!"
    echo "Workspace location: $WORKSPACE_DIR"
    
    # List generated files
    echo "Generated files:"
    find "$WORKSPACE_DIR" -type f -name "*.json" -o -name "*.sh" | head -10
    
else
    echo "Provisioning failed!"
    exit 1
fi

echo "Deployment completed!"
"""
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod(output_path, 0o755)
        
        print(f"Generated deployment script: {output_path}")
        return output_path

# Example usage functions
def generate_config_for_project(project_id):
    """Generate configuration for a specific project"""
    generator = ProvisioningConfigGenerator()
    return generator.generate_project_config(project_id)

def generate_all_configs():
    """Generate configurations for all projects"""
    generator = ProvisioningConfigGenerator()
    return generator.generate_all_project_configs()

def generate_deployment_script_for_project(project_id):
    """Generate deployment script for a specific project"""
    generator = ProvisioningConfigGenerator()
    return generator.generate_deployment_script(project_id)
