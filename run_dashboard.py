#!/usr/bin/env python3
"""
NVFlare Provisioning Dashboard Runner
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='NVFlare Provisioning Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8443, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--workspace', default='workspace', help='Sorachain workspace directory')
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['NVFLARE_WORKSPACE'] = args.workspace
    
    try:
        # Create the app
        from application import create_app, init_database
        app = create_app()
        
        # Initialize database separately
        print("Initializing database...")
        init_database(app)
        print("Database initialization completed")
        
        print(f"Starting Sorachain Provisioning Dashboard on {args.host}:{args.port}")
        print(f"Workspace directory: {args.workspace}")
        print(f"Debug mode: {args.debug}")
        print("Press Ctrl+C to stop")
        
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=False  # Disable reloader to avoid duplicate processes
        )
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()


