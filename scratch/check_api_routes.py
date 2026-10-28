# -*- coding: utf-8 -*-
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in app.py: {len(lines)}")
for i, l in enumerate(lines):
    if l.strip().startswith("@app.route"):
        if i > len(lines) - 80:
            print(f"{i+1}: {l.strip()}")

print("\nLast 30 lines of app.py:")
for l in lines[-30:]:
    print(l, end='')

