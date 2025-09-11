import numpy as np
import pandas as pd
import os

from collections import defaultdict

import miro

# --- CONFIG ---
EXCEL_FILE = "Use case collection template.xlsx"
SHEET = 'New Template GenAI'
IMPACT_LEVELS = {
    'team': 0.0,
    'department': 0.166,
    'division': 0.333,
    'unit': 0.5,
    'tno': 0.666,
    'industry': 0.833,
    'society': 1.0
}
COLORS_STICKY_NOTES_MIRO = ['gray', 'light_yellow', 'yellow', 'orange', 'light_green', 'green', 'dark_green', 'cyan', 'light_pink', 'pink', 'violet', 'red', 'light_blue', 'blue', 'dark_blue', 'black']
COLORS_HEX = [
    '#f0f8ff', '#faebd7', '#00ffff', '#7fffd4', '#f0ffff', '#f5f5dc', '#ffe4c4',
    '#000000', '#ffebcd', '#0000ff', '#8a2be2', '#a52a2a', '#deb887', '#5f9ea0',
    '#7fff00', '#d2691e', '#ff7f50', '#6495ed', '#fff8dc', '#dc143c', '#00ffff',
    '#00008b', '#008b8b', '#b8860b', '#a9a9a9', '#006400', '#a9a9a9', '#bdb76b',
    '#8b008b', '#556b2f', '#ff8c00', '#9932cc', '#8b0000', '#e9967a', '#8fbc8f',
    '#483d8b', '#2f4f4f', '#2f4f4f', '#00ced1', '#9400d3', '#ff1493', '#00bfff',
    '#696969', '#696969', '#1e90ff', '#b22222', '#fffaf0', '#228b22', '#ff00ff',
    '#dcdcdc'
]


# --- STEP 1: Load Data ---
df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET)
df = df.drop(df.columns[0], axis=1) # drop first merged colum
df.index = df.iloc[:, 0] # index will be the now first column
df = df.drop(df.columns[0], axis=1)

# pre-processing Impact and Effort
df = df.rename(index={
        'Impact (team-department-division-unit-TNO-Industry-Society)': 'impact',
        'Effort (total time)': 'effort' 
        })
def extract_person_months(entry):
    try:
        return float(entry.split()[0])
    except:
        return np.nan  # or use a default value like 0

#df['effort'] = df['effort'].apply(extract_person_months)
df.loc['effort'] = df.loc['effort'].map(extract_person_months)

def get_impact_score(text):
    prompt = f"""
    Given the following impact description: "{text}"
    Map it to a numerical score between 0 and 1 based on these levels:
    team (0.0), department (0.166), division (0.333), unit (0.5), TNO (0.666), industry (0.833), society (1.0).
    Return only the number.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return float(response['choices'][0]['message']['content'])

#df['impact'] = df['impact'].apply(get_impact_score)
# mocking test
df.loc['impact', :] = [0.0, 0.0, 0.333, 0.833, 0.833, 0.9165, 0.5, 0.5, 0.166, 0.0]

# --- STEP 2: Clustering by projects (marked with colors) ---
def extract_subcategory_cluster(series):
    """
    Assigns a unique cluster number to each unique subcategory found in a comma-separated string.
    Returns a Series of cluster numbers (for the first subcategory in each entry).
    """
    # Split and strip whitespace
    subcat_lists = series.fillna('').apply(lambda x: [s.strip() for s in str(x).split(',') if s.strip()])
    # Find all unique subcategories
    unique_subcats = sorted(set(s for sublist in subcat_lists for s in sublist))
    subcat_to_cluster = {subcat: i for i, subcat in enumerate(unique_subcats)}
    # Assign cluster number for the first subcategory (or -1 if empty)
    return subcat_lists.apply(lambda lst: subcat_to_cluster[lst[0]] if lst else -1)

# Assign colors per cluster
df.loc['Color'] = extract_subcategory_cluster(df.loc['Project'])
df.loc['Color'] = df.loc['Color'].map(lambda x: COLORS_STICKY_NOTES_MIRO[x % len(COLORS_STICKY_NOTES_MIRO)])

# --- STEP 3: Positioning for Impact vs Effort ---
# Scale positions for Miro canvas
effort = df.loc['effort']
effort_min = effort.min()
effort_max = effort.max()
df.loc['x'] = ((effort - effort_min) / (effort_max - effort_min)) * 500
df.loc['y'] = df.loc['impact'] * 500  # impact [0, 1] scale to [0, 500]

# --- STEP 4: Create sticky notes in Miro ---
for i, (use_case, col) in enumerate(df.items()):
    x  = col.at['x']
    y  = col.at['y']
    if pd.isna(x) or pd.isna(y):
        continue  # skip creating the note
    print(f"Creating sticky note for '{use_case}' at ({x}, {y})")
    df.at['id_miro', use_case] = miro.create_sticky_note(str(i), col.at['Color'], x, y, width=20)
    # miro.create_shape(x , y, shape="rectangle", width=10, height=10,
    #     fill_color=col.at['Color'], border_color="#1a1a1a",
    #     content=str(i)
    # )

print(df.loc['id_miro'])

# --- STEP 5: Add Connectors based on 'Solution subcategory' ---
def get_connections_by_subcategory(df, subcat_row='Solution subcategory'):
    """
    Returns a list of (use_case1, use_case2, subcategory) tuples for all pairs sharing at least one subcategory.
    Each pair appears only once (use_case1 < use_case2).
    """
    # Map subcategory to list of use cases
    subcat_to_use_cases = defaultdict(list)
    for use_case, entry in df.loc[subcat_row].items():
        subcats = [s.strip() for s in str(entry).split(',') if s.strip()]
        for subcat in subcats:
            subcat_to_use_cases[subcat].append(use_case)
    # Build unique connections
    connections = []
    for subcat, use_cases in subcat_to_use_cases.items():
        for i in range(len(use_cases)):
            for j in range(i + 1, len(use_cases)):
                #u1, u2 = sorted([use_cases[i], use_cases[j]]) # use case name
                id1 = df.at['id_miro', use_cases[i]]
                id2 = df.at['id_miro', use_cases[j]]
                # Only add if both IDs are present and not nan
                if pd.notna(id1) and pd.notna(id2) and id1 != id2:
                    u1, u2 = sorted([id1, id2])
                    connections.append((u1, u2, subcat))
    # Remove duplicates (if any)
    connections = list(set(connections))
    return connections

connections = get_connections_by_subcategory(df, subcat_row='Solution subcategory')
for u1, u2, subcat in connections:
    print(f"{u1} <-> {u2} via '{subcat}'")
    id_connector = miro.create_connector(u1, u2, caption=subcat, font_size=10)

