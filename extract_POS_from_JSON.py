import json
import pandas as pd
import ast
import sys
# === Step 1: Load JSON file ===
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    content = f.read()
    json_data = ast.literal_eval(content)

id_to_pos = {}
for entry in json_data:
    sentence_id = entry.get("sentence_id")
    pos_list = entry.get("result", [{}])[0].get("pos", [])
    id_to_pos[sentence_id] = pos_list  # or ' '.join(pos_list) if you want string

# === Step 2: Load Excel file ===
excel_path = sys.argv[2]
df = pd.read_excel(excel_path)

# === Step 3: Map POS to each row based on sentence_id ===
df['pos'] = df['Sentence_id'].map(id_to_pos)

# === Step 4: Save new Excel with "_pos_added" ===
new_path = excel_path.replace('.xlsx', '_pos_added.xlsx')
df.to_excel(new_path, index=False)

print(f"✅ POS added and saved to: {new_path}")