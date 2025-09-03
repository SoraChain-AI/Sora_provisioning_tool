#!/usr/bin/env python3
"""
Database-based NVFlare Provisioner
Creates project configurations from database data and uses NVFlare provisioner directly
Following the same pattern as NVFlare's provision.py handle_provision() function
"""

import os
import tempfile
import json
import shutil
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any

from .models import Project, Server, Client, Admin

# Import NVFlare provisioner components
try:
    from nvflare.lighter.constants import PropKey
    from nvflare.lighter.entity import Project as ProvProject, participant_from_dict
    from nvflare.lighter.prov_utils import prepare_builders, prepare_packager
    from nvflare.lighter.provisioner import Provisioner
    from nvflare.lighter.utils import load_yaml
    NVFLARE_AVAILABLE = True
except ImportError:
    NVFLARE_AVAILABLE = False
    print("Warning: NVFlare not available, falling back to CLI approach")


class DatabaseProvisioner:
    """
    Database-based provisioner that creates NVFlare projects from database data
    Following the same pattern as NVFlare's provision.py
    """
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def provision_project(self, project_id: int, force_reprovision: bool = False) -> Optional[str]:
        """
        Provision a project using database data - main entry point
        Similar to handle_provision() in NVFlare's provision.py
        """
        print(f"🔍 Starting provision_project with project_id: {project_id}")
        
        if not NVFLARE_AVAILABLE:
            print("NVFlare not available, falling back to CLI approach")
            return self._provision_via_cli(project_id, force_reprovision)
        
        try:
            # Get project data from database
            project = Project.query.get(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            servers = Server.query.filter_by(project_id=project_id).all()
            clients = Client.query.filter_by(project_id=project_id).all()
            admins = Admin.query.filter_by(project_id=project_id).all()
            
            print(f"Provisioning project: {project.name}")
            print(f"Servers: {len(servers)}, Clients: {len(clients)}, Admins: {len(admins)}")
            
            # Validate project has required participants
            self._validate_project_data(project, servers, clients, admins)
            
            # Check if already provisioned
            if not force_reprovision:
                existing_workspace = self._get_existing_workspace(project_id)
                if existing_workspace:
                    print(f"Project {project_id} already provisioned, using existing workspace: {existing_workspace}")
                    return existing_workspace
            
            # Create temporary directory for provisioning
            with tempfile.TemporaryDirectory() as tmp_dir:
                print(f"✅ Using temporary directory: {tmp_dir}")
                
                # Create project configuration from database data
                project_dict = self._create_project_dict(project, servers, clients, admins)
                
                # Create temporary project.yml file in config folder
                config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
                temp_project_yml = os.path.join(config_dir, f'temp_project_{project_id}.yml')
                
                try:
                    # Write the project configuration to temporary YAML file
                    with open(temp_project_yml, 'w') as f:
                        yaml.dump(project_dict, f, default_flow_style=False, sort_keys=False)
                    
                    print(f"📝 Created temporary project.yml: {temp_project_yml}")
                    
                    # Use the same approach as provision.py - load from YAML file
                    project_dict_from_file = load_yaml(temp_project_yml)
                    
                    # Prepare project object - similar to prepare_project() in provision.py
                    prov_project = self._prepare_project(project_dict_from_file)
                    
                    # Prepare builders and packager - same as in provision.py
                    builders = prepare_builders(project_dict_from_file)
                    packager = prepare_packager(project_dict_from_file)
                    
                    # Create provisioner - same as in provision.py
                    provisioner = Provisioner(tmp_dir, builders, packager)
                    
                    # Provision the project - same as in provision.py
                    print("Calling provisioner.provision()...")
                    result_ctx = provisioner.provision(prov_project)
                    
                    # Extract result directory
                    result_dir = self._extract_result_directory(result_ctx, tmp_dir)
                    
                    # Copy to final workspace in the main workspace directory
                    main_workspace_dir = os.path.join(os.path.dirname(__file__), '..', 'workspace')
                    os.makedirs(main_workspace_dir, exist_ok=True)
                    
                    final_workspace = os.path.join(main_workspace_dir, f"project_{project_id}")
                    if os.path.exists(final_workspace):
                        shutil.rmtree(final_workspace)
                    
                    shutil.copytree(result_dir, final_workspace)
                    print(f"✅ Copied to final workspace: {final_workspace}")
                    
                    return final_workspace
                    
                finally:
                    # Don't clean up temporary YAML file for debugging
                    if os.path.exists(temp_project_yml):
                        print(f"🔍 Debug: Temporary project.yml saved at: {temp_project_yml}")
                        # Uncomment the next line to clean up
                        # os.unlink(temp_project_yml)
                
        except Exception as e:
            print(f"❌ Error provisioning project: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validate_project_data(self, project: Project, servers: List[Server], 
                              clients: List[Client], admins: List[Admin]) -> None:
        """Validate that project has required data"""
        if not servers:
            raise ValueError("No servers configured for this project. Please add at least one server before provisioning.")
        
        if not clients:
            raise ValueError("No clients configured for this project. Please add at least one client before provisioning.")
        
        # Validate server data
        for server in servers:
            if not server.name or server.name.strip() == '':
                raise ValueError(f"Server has empty name. Please set a valid server name.")
            if not server.org or server.org.strip() == '':
                raise ValueError(f"Server '{server.name}' has empty organization. Please set a valid organization.")
        
        # Validate client data
        for client in clients:
            if not client.name or client.name.strip() == '':
                raise ValueError(f"Client has empty name. Please set a valid client name.")
            if not client.org or client.org.strip() == '':
                raise ValueError(f"Client '{client.name}' has empty organization. Please set a valid organization.")
    
    def _create_project_dict(self, project: Project, servers: List[Server], 
                           clients: List[Client], admins: List[Admin]) -> Dict[str, Any]:
        """
        Create project dictionary from database data using base project.yml template
        """
        # Load base project.yml template (use the one with admin using fed_learn_port)
        base_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'project_admin_fed_learn_port.yml')
        if not os.path.exists(base_config_path):
            # Fallback to regular project.yml
            base_config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'project.yml')
            if not os.path.exists(base_config_path):
                raise FileNotFoundError(f"Base project.yml not found at {base_config_path}")
        
        with open(base_config_path, 'r') as f:
            project_dict = yaml.safe_load(f)
        
        print(f"📋 Loaded base project.yml template")
        
        # Update project metadata
        project_dict[PropKey.NAME] = getattr(project, 'short_name', project.name) or f"project_{project.id}"
        project_dict[PropKey.DESCRIPTION] = getattr(project, 'description', '') or f'Project {project.name}'
        
        # Add project-level properties if available
        if hasattr(project, 'project_props') and project.project_props:
            try:
                project_props = json.loads(project.project_props)
                project_dict.update(project_props)
            except:
                pass
        
        # Clear existing participants and add new ones from database
        project_dict['participants'] = []
        
        # Add servers as participants
        for server in servers:
            fed_learn_port = getattr(server, 'fed_learn_port', 8002)
            # Force admin_port to be the same as fed_learn_port
            admin_port = fed_learn_port
            
            server_participant = {
                'name': server.name,
                'host': server.name,
                'org': server.org or 'nvidia',
                'type': 'server',
                'fed_learn_port': fed_learn_port,
                'admin_port': 8003,  # Use admin port 8003 like working example
                'admin_host': 'FLAdmin.com'  # Add admin_host to server participant
            }
            
            # Add any additional server properties
            if hasattr(server, 'props') and server.props:
                try:
                    server_props = json.loads(server.props)
                    # Remove any conflicting admin properties
                    server_props.pop('admin_host', None)
                    server_props.pop('admin_port', None)
                    server_participant.update(server_props)
                except:
                    pass
            
            # FORCE the admin configuration to ensure it's not overridden
            server_participant['admin_host'] = 'FLAdmin.com'
            server_participant['admin_port'] = 8003
            print(f"🔧 FORCED admin_host=FLAdmin.com and admin_port=8003 for server {server.name}")
            
            project_dict['participants'].append(server_participant)
        
        # Add clients as participants
        for client in clients:
            client_participant = {
                'name': client.name,
                'host': client.name,
                'org': client.org or 'nvidia',
                'type': 'client'
            }
            
            # Add capacity if available
            if hasattr(client, 'capacity') and client.capacity:
                try:
                    capacity_data = json.loads(client.capacity)
                    client_participant['capacity'] = capacity_data
                except:
                    pass
            
            # Add any additional client properties
            if hasattr(client, 'props') and client.props:
                try:
                    client_props = json.loads(client.props)
                    client_participant.update(client_props)
                except:
                    pass
            
            project_dict['participants'].append(client_participant)
        
        # Add admins as participants
        for admin in admins:
            admin_role = getattr(admin, 'role', 'project_admin')
            print(f"🔍 Admin {admin.email} role: {admin_role}")
            
            # Admin should connect to the admin port (8003) using separate admin hostname
            admin_host = 'FLAdmin.com'  # Use separate admin hostname
            admin_port = 8003  # Use admin port 8003 like the working example
            # servers[0].fed_learn_port = admin_port
            
            admin_participant = {
                'name': admin.email,
                'host': admin_host,
                'org': admin.org or 'nvidia',
                'type': 'admin',
                'role': admin_role,
                'port': admin_port,  # Connect to admin port (8003)
                'admin_port': admin_port,  # Admin server runs on port 8003
                'fed_learn_port': servers[0].fed_learn_port if servers else 8002,  # Keep fed_learn_port separate (8002)
                'scheme': 'grpc'  # Use gRPC scheme for admin connection
            }
            
            # Add any additional admin properties
            if hasattr(admin, 'props') and admin.props:
                try:
                    admin_props = json.loads(admin.props)
                    # Remove any port-related props that might override our settings
                    admin_props.pop('port', None)
                    admin_props.pop('admin_port', None)
                    admin_props.pop('fed_learn_port', None)
                    admin_participant.update(admin_props)
                except:
                    pass
            
            # FORCE the admin to connect to admin port (8003) like the working example
            admin_participant['port'] = 8003
            admin_participant['admin_port'] = 8003  # Admin server runs on 8003
            print(f"🔧 FORCED admin to connect to admin port 8003 for {admin.email}")
            
            project_dict['participants'].append(admin_participant)
        
        # Update overseer agent configuration if servers exist
        if servers:
            primary_server = servers[0]
            fed_learn_port = getattr(primary_server, 'fed_learn_port', 8002)
            
            # Update overseer agent in builders to use actual server name and ports
            for builder in project_dict.get('builders', []):
                if builder.get('path') == 'nvflare.lighter.impl.static_file.StaticFileBuilder':
                    if 'args' in builder:
                        # Update the overseer agent sp_end_point with actual server details
                        if 'overseer_agent' in builder['args'] and 'args' in builder['args']['overseer_agent']:
                            # Use fed_learn_port for FL and admin_port (8003) for admin connections
                            admin_endpoint = f"{primary_server.name}:{fed_learn_port}:8003"
                            builder['args']['overseer_agent']['args']['sp_end_point'] = admin_endpoint
                            print(f"🔧 Updated overseer sp_end_point: {admin_endpoint}")
                        
                        # Ensure admin port is set to the actual admin port (8003)
                        builder['args']['admin_port'] = 8003
                        print(f"🔧 Set admin port to 8003")
                        
                        # Add server binding configuration to bind to all interfaces for remote access
                        builder['args']['server_binding'] = '0.0.0.0'
                        print(f"🔧 Set server binding to 0.0.0.0 for external connections")
                        
                        # Add admin server binding configuration to bind to all interfaces
                        builder['args']['admin_server_binding'] = '0.0.0.0'
                        print(f"🔧 Set admin server binding to 0.0.0.0 for external connections")
                        
                        # Add admin server configuration to bind to all interfaces (like working example)
                        builder['args']['admin_server'] = {
                            'host': '0.0.0.0',
                            'port': 8003
                        }
                        print(f"🔧 Set admin server to bind to 0.0.0.0:8003")
                        
                        # Add admin_host to server config (crucial for remote access)
                        builder['args']['admin_host'] = 'FLAdmin.com'
                        print(f"🔧 Set admin_host to FLAdmin.com")
                        
                        # Force admin configuration in server config
                        builder['args']['force_admin_config'] = {
                            'admin_host': 'FLAdmin.com',
                            'admin_port': 8003
                        }
                        print(f"🔧 Added force_admin_config to builder")
                        
                        # Ensure the server target uses the correct hostname for remote access
                        if 'server_target' not in builder['args']:
                            builder['args']['server_target'] = f"{primary_server.name}:{fed_learn_port}"
                            print(f"🔧 Set server target to {primary_server.name}:{fed_learn_port}")
        
        # Add admin configuration directly to server participants
        for participant in project_dict.get('participants', []):
            if participant.get('type') == 'server':
                participant['admin_host'] = 'FLAdmin.com'
                participant['admin_port'] = 8003
                print(f"🔧 Added admin_host=FLAdmin.com and admin_port=8003 to server participant {participant.get('name')}")
        
        # Add admin configuration to builders
        for builder in project_dict.get('builders', []):
            if builder.get('path') == 'nvflare.lighter.impl.static_file.StaticFileBuilder':
                if 'args' not in builder:
                    builder['args'] = {}
                builder['args']['admin_host'] = 'FLAdmin.com'
                builder['args']['admin_port'] = 8003
                print(f"🔧 Added admin_host=FLAdmin.com and admin_port=8003 to StaticFileBuilder")
        
        print(f"Created project dict with {len(project_dict['participants'])} participants")
        print(f"Using {len(project_dict.get('builders', []))} builders from template")
        print(f"Added fed_server template with admin_host=FLAdmin.com and admin_port=8003")
        return project_dict
    
    def _prepare_project(self, project_dict: Dict[str, Any]) -> ProvProject:
        """
        Prepare project object from project dictionary
        Similar to prepare_project() in NVFlare's provision.py
        """
        api_version = project_dict.get(PropKey.API_VERSION)
        if api_version not in [3]:
            raise ValueError(f"API version expected 3 but found {api_version}")
        
        project_name = project_dict.get(PropKey.NAME)
        if len(project_name) > 63:
            print(f"Project name {project_name} is longer than 63. Will truncate it to {project_name[:63]}.")
            project_name = project_name[:63]
            project_dict[PropKey.NAME] = project_name
        
        project_description = project_dict.get(PropKey.DESCRIPTION, "")
        project = ProvProject(name=project_name, description=project_description, props=project_dict)
        
        participant_defs = project_dict.get("participants", [])
        
        # Add participants to project - same as in provision.py
        for p in participant_defs:
            project.add_participant(participant_from_dict(p))
        
        return project
    
    def _extract_result_directory(self, result_ctx, tmp_dir: str) -> str:
        """Extract result directory from provisioner context"""
        if hasattr(result_ctx, 'get_result_location'):
            result_dir = result_ctx.get_result_location()
        elif hasattr(result_ctx, 'result_location'):
            result_dir = result_ctx.result_location
        else:
            # Try to find the result directory in the temporary directory
            result_dir = os.path.join(tmp_dir, "project_2", "prod_00")
            if not os.path.exists(result_dir):
                # Look for any directory that might contain the results
                for item in os.listdir(tmp_dir):
                    item_path = os.path.join(tmp_dir, item)
                    if os.path.isdir(item_path):
                        prod_dir = os.path.join(item_path, "prod_00")
                        if os.path.exists(prod_dir):
                            result_dir = prod_dir
                            break
        
        if not result_dir or not os.path.exists(result_dir):
            raise ValueError(f"Could not find result directory from provisioning")
        
        return result_dir
    
    def _add_admin_config_to_project(self, project_dict: Dict[str, Any], servers: List[Server]) -> None:
        """Add admin_host and admin_port to server configuration in project dict"""
        if not servers:
            return
        
        # Find server participants and add admin configuration
        for participant in project_dict.get('participants', []):
            if participant.get('type') == 'server':
                participant['admin_host'] = 'FLAdmin.com'
                participant['admin_port'] = 8003
                print(f"🔧 Added admin_host=FLAdmin.com and admin_port=8003 to server participant {participant.get('name')}")
        
        # Also add to builders configuration
        for builder in project_dict.get('builders', []):
            if builder.get('path') == 'nvflare.lighter.impl.static_file.StaticFileBuilder':
                if 'args' not in builder:
                    builder['args'] = {}
                builder['args']['admin_host'] = 'FLAdmin.com'
                builder['args']['admin_port'] = 8003
                print(f"🔧 Added admin_host=FLAdmin.com and admin_port=8003 to StaticFileBuilder")
    
    def _fix_admin_port_configuration(self, workspace_dir: str, servers: List[Server]) -> None:
        """Post-process admin configuration to use fed_learn_port instead of admin_port"""
        if not servers:
            return
        
        primary_server = servers[0]
        fed_learn_port = 5005
        
        # Find admin directories and fix their fed_admin.json files
        for item in os.listdir(workspace_dir):
            if '@' in item:  # Admin directory typically contains @ symbol
                admin_dir = os.path.join(workspace_dir, item)
                fed_admin_path = os.path.join(admin_dir, 'startup', 'fed_admin.json')
                
                if os.path.exists(fed_admin_path):
                    try:
                        with open(fed_admin_path, 'r') as f:
                            admin_config = json.load(f)
                        
                        # Update the port to use fed_learn_port
                        if 'admin' in admin_config and 'port' in admin_config['admin']:
                            old_port = admin_config['admin']['port']
                            admin_config['admin']['port'] = fed_learn_port
                            
                            with open(fed_admin_path, 'w') as f:
                                json.dump(admin_config, f, indent=2)
                            
                            print(f"🔧 Fixed admin {item} port: {old_port} -> {fed_learn_port}")
                        
                    except Exception as e:
                        print(f"⚠️  Error fixing admin config for {item}: {e}")
    
    def _get_existing_workspace(self, project_id: int) -> Optional[str]:
        """Get existing workspace if project is already provisioned"""
        # Look in the main workspace directory
        main_workspace_dir = os.path.join(os.path.dirname(__file__), '..', 'workspace')
        workspace = os.path.join(main_workspace_dir, f"project_{project_id}")
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
    
    def _provision_via_cli(self, project_id: int, force_reprovision: bool = False) -> Optional[str]:
        """Fallback to CLI provisioning if NVFlare is not available"""
        print("Using CLI fallback provisioning...")
        # This would call the existing CLI-based provisioning
        # For now, just return None to indicate fallback needed
        return None
    
    def generate_startup_kit(self, project_id: int, item_type: str, item_id: Optional[int] = None) -> tuple:
        """Generate startup kit for a specific item or the entire project"""
        workspace = self._get_existing_workspace(project_id)
        if not workspace:
            raise ValueError(f"Project {project_id} not provisioned")
        
        if item_type == 'all':
            return self._generate_all_startup_kits(workspace)
        else:
            return self._generate_item_startup_kit(workspace, item_type, item_id)
    
    def _generate_item_startup_kit(self, workspace: str, item_type: str, item_id: Optional[int]) -> tuple:
        """Generate startup kit for a specific item"""
        import zipfile
        import io
        
        # Find the appropriate directory based on item type
        target_dir = None
        
        for item in os.listdir(workspace):
            item_path = os.path.join(workspace, item)
            if os.path.isdir(item_path):
                if item_type == 'server' and (item.endswith('.com') or item.endswith('.org')):
                    target_dir = item_path
                    break
                elif item_type == 'client' and item.startswith('site-'):
                    target_dir = item_path
                    break
                elif item_type == 'admin' and '@' in item:
                    target_dir = item_path
                    break
        
        if not target_dir:
            raise ValueError(f"Could not find {item_type} directory in workspace")
        
        # Create zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, target_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        return zip_buffer, f"{os.path.basename(target_dir)}.zip"
    
    def _generate_all_startup_kits(self, workspace: str) -> Dict[str, tuple]:
        """Generate startup kits for all items"""
        all_kits = {}
        
        for item in os.listdir(workspace):
            item_path = os.path.join(workspace, item)
            if os.path.isdir(item_path):
                if item.endswith('.com') or item.endswith('.org'):
                    # Server
                    kit_buffer, kit_name = self._generate_item_startup_kit(workspace, 'server', None)
                    all_kits['server'] = (kit_buffer, kit_name)
                elif item.startswith('site-'):
                    # Client
                    kit_buffer, kit_name = self._generate_item_startup_kit(workspace, 'client', None)
                    all_kits['client'] = (kit_buffer, kit_name)
                elif '@' in item:
                    # Admin
                    kit_buffer, kit_name = self._generate_item_startup_kit(workspace, 'admin', None)
                    all_kits['admin'] = (kit_buffer, kit_name)
        
        return all_kits


# Convenience function for direct usage
def provision_project_from_database(project_id: int, workspace_dir: str = "workspace", 
                                  force_reprovision: bool = False) -> Optional[str]:
    """
    Convenience function to provision a project directly from database
    Similar to how provision.py can be called directly
    """
    provisioner = DatabaseProvisioner(workspace_dir)
    return provisioner.provision_project(project_id, force_reprovision)


if __name__ == "__main__":
    # Example usage - can be called directly like provision.py
    import sys
    if len(sys.argv) < 2:
        print("Usage: python database_provisioner.py <project_id> [workspace_dir] [force_reprovision]")
        sys.exit(1)
    
    project_id = int(sys.argv[1])
    workspace_dir = sys.argv[2] if len(sys.argv) > 2 else "workspace"
    force_reprovision = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    result = provision_project_from_database(project_id, workspace_dir, force_reprovision)
    if result:
        print(f"✅ Provisioning successful: {result}")
    else:
        print("❌ Provisioning failed")
        sys.exit(1)
