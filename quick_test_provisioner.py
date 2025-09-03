#!/usr/bin/env python3
"""
Quick test script for DatabaseProvisioner
Simple test to provision project 2 and verify the results
"""

import os
import sys
import shutil

# Add the application directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application'))

from application import create_app, db
from application.models import Project, Server, Client, Admin
from application.database_provisioner import DatabaseProvisioner

def quick_test():
    """Quick test of the DatabaseProvisioner"""
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        
        project_id = 2
        print(f"🚀 Quick test of DatabaseProvisioner for project {project_id}")
        
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"❌ Project {project_id} not found in database")
            return False
        
        print(f"✅ Found project: {project.name}")
        
        # Get participants
        servers = Server.query.filter_by(project_id=project_id).all()
        clients = Client.query.filter_by(project_id=project_id).all()
        admins = Admin.query.filter_by(project_id=project_id).all()
        
        print(f"📊 Participants: {len(servers)} servers, {len(clients)} clients, {len(admins)} admins")
        
        if not servers:
            print(f"❌ No servers found for project {project_id}")
            return False
        
        if not clients:
            print(f"❌ No clients found for project {project_id}")
            return False
        
        # Test provisioning
        try:
            provisioner = DatabaseProvisioner(workspace_dir="quick_test_workspace")
            
            print(f"🔧 Starting provisioning...")
            result = provisioner.provision_project(project_id, force_reprovision=True)
            
            if result and os.path.exists(result):
                print(f"✅ Provisioning successful!")
                print(f"📁 Workspace: {result}")
                
                # Quick verification
                contents = os.listdir(result)
                print(f"📁 Generated directories: {contents}")
                
                # Check for key files
                has_server = any(item.endswith('.com') or item.endswith('.org') for item in contents)
                has_client = any(item.startswith('site-') for item in contents)
                has_admin = any('@' in item for item in contents)
                
                print(f"✅ Server directory: {'Yes' if has_server else 'No'}")
                print(f"✅ Client directory: {'Yes' if has_client else 'No'}")
                print(f"✅ Admin directory: {'Yes' if has_admin else 'No'}")
                
                return True
            else:
                print(f"❌ Provisioning failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during provisioning: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Don't clean up - keep the workspace for inspection
            print(f"📁 Final workspace preserved for inspection")

if __name__ == "__main__":
    success = quick_test()
    if success:
        print(f"\n🎉 Quick test completed successfully!")
    else:
        print(f"\n❌ Quick test failed!")
        sys.exit(1)
