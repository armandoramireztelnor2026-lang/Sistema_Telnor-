with open('rutas_reportes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import re, unicodedata at top
old_imports = '''from flask import Blueprint, request, jsonify, session
import os'''
new_imports = '''from flask import Blueprint, request, jsonify, session
import os
import re
import unicodedata'''

if old_imports in content:
    content = content.replace(old_imports, new_imports, 1)
    print("Added imports at top of rutas_reportes.py")
else:
    print("old_imports not found")

with open('rutas_reportes.py', 'w', encoding='utf-8') as f:
    f.write(content)

