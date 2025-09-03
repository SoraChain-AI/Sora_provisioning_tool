#!/usr/bin/env python3
"""
Example usage of the DatabaseProvisioner
Demonstrates how to use the new database-based provisioner
"""

import os
import sys
from database_provisioner import DatabaseProvisioner, provision_project_from_database

def example_usage():
    """Example of how to use the DatabaseProvisioner"""
    
    # Example 1: Using the class directly
    print("=== Example 1: Using DatabaseProvisioner class ===")
    provisioner = DatabaseProvisioner(workspace_dir="example_workspace")
    
    # Provision project with ID 1
    project_id = 1
    result = provisioner.provision_project(project_id, force_reprovision=False)
    
    if result:
        print(f"✅ Project {project_id} provisioned successfully: {result}")
        
        # Generate startup kit for server
        try:
            kit_buffer, filename = provisioner.generate_startup_kit(project_id, 'server')
            print(f"✅ Generated server startup kit: {filename}")
        except Exception as e:
            print(f"❌ Error generating server kit: {e}")
    else:
        print(f"❌ Failed to provision project {project_id}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Using the convenience function
    print("=== Example 2: Using convenience function ===")
    result = provision_project_from_database(
        project_id=1, 
        workspace_dir="example_workspace_2", 
        force_reprovision=True
    )
    
    if result:
        print(f"✅ Project provisioned successfully: {result}")
    else:
        print("❌ Project provisioning failed")

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <project_id> [workspace_dir] [force_reprovision]")
        print("Example: python example_usage.py 1 my_workspace true")
        sys.exit(1)
    
    project_id = int(sys.argv[1])
    workspace_dir = sys.argv[2] if len(sys.argv) > 2 else "workspace"
    force_reprovision = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    print(f"Provisioning project {project_id}...")
    print(f"Workspace: {workspace_dir}")
    print(f"Force reprovision: {force_reprovision}")
    
    result = provision_project_from_database(project_id, workspace_dir, force_reprovision)
    
    if result:
        print(f"✅ Provisioning successful: {result}")
    else:
        print("❌ Provisioning failed")
        sys.exit(1)

if __name__ == "__main__":
    # Run example if no command line arguments
    if len(sys.argv) == 1:
        example_usage()
    else:
        main()
