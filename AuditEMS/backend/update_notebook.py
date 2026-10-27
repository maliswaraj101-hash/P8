import json
import os

notebook_path = '/home/swaraj/projects/AuditEMS/backend/server.ipynb'

if not os.path.exists(notebook_path):
    print(f"Error: {notebook_path} not found.")
    exit(1)

with open(notebook_path, 'r', encoding='utf-8') as f:
    try:
        nb = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        exit(1)

changed = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        new_source = []
        skip_next = False
        for i, line in enumerate(source):
            if skip_next:
                skip_next = False
                continue
            
            # Update ChatState
            if 'document : str' in line:
                new_source.append(line.replace('document : str', 'document : bytes'))
                changed = True
            
            # Update ocr_node
            elif "with open(state['document'] , \"rb\") as f:" in line:
                new_source.append("        file_bytes = state['document']\n")
                # Look ahead to see if the next line is file_bytes = f.read()
                if i + 1 < len(source) and 'f.read()' in source[i+1]:
                    skip_next = True
                changed = True
            else:
                new_source.append(line)
        cell['source'] = new_source

if changed:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook updated successfully.")
else:
    print("No changes were necessary or patterns not found.")
