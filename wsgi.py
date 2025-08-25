#!/usr/bin/env python3
"""
NVFlare Provisioning Dashboard - WSGI Entry Point
This dashboard integrates with the NVFlare CLI provisioning tool
"""

import os
import sys
from flask import Flask
from application import create_app

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, debug=True)





