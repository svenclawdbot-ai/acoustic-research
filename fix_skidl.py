#!/usr/bin/env python3
# Fix circular import in SKiDL

import re

file_path = '/home/james/.openclaw/workspace/skidl/src/skidl/tools/kicad8/lib.py'

with open(file_path, 'r') as f:
    content = f.read()

# Replace the circular import pattern
old_code = '''    from skidl import get_default_tool

    kicad_version = get_default_tool()[len("kicad"):]'''

new_code = '''    # Avoid circular import - get version from environment
    import os
    kicad_version = os.environ.get('SKIDL_KICAD_VERSION', '8')'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w') as f:
        f.write(content)
    print("Fixed circular import in kicad8/lib.py")
else:
    print("Pattern not found - already fixed or different version")
