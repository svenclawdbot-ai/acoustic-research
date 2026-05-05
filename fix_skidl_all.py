#!/usr/bin/env python3
# Fix circular import in SKiDL - all kicad versions

import re

files = [
    '/home/james/.openclaw/workspace/skidl/src/skidl/tools/kicad6/lib.py',
    '/home/james/.openclaw/workspace/skidl/src/skidl/tools/kicad7/lib.py',
    '/home/james/.openclaw/workspace/skidl/src/skidl/tools/kicad8/lib.py',
    '/home/james/.openclaw/workspace/skidl/src/skidl/tools/kicad9/lib.py',
]

old_code = '''    from skidl import get_default_tool

    kicad_version = get_default_tool()[len("kicad"):]'''

new_code = '''    # Avoid circular import - get version from environment
    import os
    kicad_version = os.environ.get('SKIDL_KICAD_VERSION', '8')'''

for file_path in files:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
        else:
            print(f"Already fixed or different: {file_path}")
    except Exception as e:
        print(f"Error with {file_path}: {e}")

print("Done!")
