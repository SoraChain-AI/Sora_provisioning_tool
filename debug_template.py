#!/usr/bin/env python3
"""
Debug script to test template replacement
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nvflare.lighter.constants import TemplateSectionKey, ProvFileName
    from nvflare.lighter.impl.static_file import StaticFileBuilder
    from nvflare.lighter.spec import ProvisionContext
    from nvflare.lighter.entity import Participant
    
    print("✅ Successfully imported NVFlare components")
    
    # Test template replacement
    print(f"TemplateSectionKey.FED_SERVER = {TemplateSectionKey.FED_SERVER}")
    print(f"ProvFileName.FED_SERVER_JSON = {ProvFileName.FED_SERVER_JSON}")
    
    # Try to find the template file
    import nvflare
    nvflare_path = os.path.dirname(nvflare.__file__)
    template_path = os.path.join(nvflare_path, 'lighter', 'impl', 'templates')
    print(f"Template path: {template_path}")
    
    if os.path.exists(template_path):
        print("Template directory exists")
        for file in os.listdir(template_path):
            if 'fed_server' in file:
                print(f"Found template file: {file}")
                with open(os.path.join(template_path, file), 'r') as f:
                    content = f.read()
                    print(f"Template content (first 500 chars): {content[:500]}")
                    if 'target' in content:
                        print("✅ Template contains 'target' variable")
                    else:
                        print("❌ Template does not contain 'target' variable")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()


