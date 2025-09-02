#!/usr/bin/env python3
"""
Command-line interface for generating NVFlare provisioning configurations
"""

import sys
import os
import argparse

# Add the application directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application'))

def main():
    parser = argparse.ArgumentParser(description='Generate NVFlare provisioning configurations')
    parser.add_argument('--project-id', type=int, help='Generate config for specific project ID')
    parser.add_argument('--all', action='store_true', help='Generate configs for all projects')
    parser.add_argument('--deploy-script', action='store_true', help='Generate deployment script')
    parser.add_argument('--output-dir', default='config', help='Output directory for generated files')
    parser.add_argument('--validate', action='store_true', help='Validate generated configurations')
    
    args = parser.parse_args()
    
    try:
        # Import after setting up the path
        from application.provisioning_generator import ProvisioningConfigGenerator
        
        generator = ProvisioningConfigGenerator(output_dir=args.output_dir)
        
        if args.project_id:
            print(f"Generating configuration for project {args.project_id}...")
            config_path = generator.generate_project_config(args.project_id)
            
            if args.deploy_script:
                script_path = generator.generate_deployment_script(args.project_id)
                print(f"Generated deployment script: {script_path}")
            
            if args.validate:
                is_valid, message = generator.validate_config(config_path)
                print(f"Validation: {message}")
                
        elif args.all:
            print("Generating configurations for all projects...")
            config_paths = generator.generate_all_project_configs()
            
            if args.validate:
                for config_path in config_paths:
                    is_valid, message = generator.validate_config(config_path)
                    print(f"{os.path.basename(config_path)}: {message}")
                    
        else:
            print("Please specify --project-id or --all")
            parser.print_help()
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
