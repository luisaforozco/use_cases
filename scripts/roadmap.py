# Script to create a roadmap in Miro based on use case data from an Excel file.
# Each use case is represented as a sticky note positioned in effort vs impact, 
# colored by project and connected to other use cases sharing the same solution subcategory.

import pandas as pd

from useCaseOrch import miro
from useCaseOrch.use_case_utils import extract_person_months, get_impact_score, extract_subcategory_cluster, get_connections_by_subcategory, get_impact_score_LLM

# --- CONFIG ---
EXCEL_FILE = "Use case collection template.xlsx"
SHEET = 'New Template GenAI'
COLORS_STICKY_NOTES_MIRO = ['gray', 'light_yellow', 'yellow', 'orange', 'light_green', 'green', 'dark_green', 'cyan', 'light_pink', 'pink', 'violet', 'red', 'light_blue', 'blue', 'dark_blue', 'black']
COLORS_HEX = [
    '#000000', '#0000ff', '#8a2be2', '#a52a2a', '#5f9ea0', '#d2691e', '#4b0082',
    '#ff7f50', '#6495ed', '#dc143c', '#00008b', '#008b8b', '#b8860b', '#cd5c5c',
    '#a9a9a9', '#006400', '#bdb76b', '#8b008b', '#556b2f', '#ff8c00', '#9932cc',
    '#8b0000', '#e9967a', '#8fbc8f', '#483d8b', '#2f4f4f', '#00ced1', '#9400d3',
    '#ff1493', '#00bfff', '#696969', '#1e90ff', '#b22222', '#228b22', '#ff00ff',
    '#ff0000', '#800000', '#191970', '#808000', '#ffa500', '#800080', '#008000',
    '#ff69b4'
]
SCALE = 1000

def load_and_preprocess_data():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET)
    df = df.drop(df.columns[0], axis=1) # drop first merged colum
    df.index = df.iloc[:, 0] # index will be the now first column
    df = df.drop(df.columns[0], axis=1)

    # --- Pre-processing impact & effort --- 
    df = df.rename(index={
            'Impact (team-department-division-unit-TNO-Industry-Society)': 'impact',
            'Effort (total time)': 'effort' 
            })
    df.loc['effort'] = df.loc['effort'].map(extract_person_months)
    df.loc['impact'] = df.loc['impact'].map(get_impact_score_LLM)

    # export processed data for future use
    df.to_pickle(f"data/{EXCEL_FILE}_{SHEET}.pkl")
    return df

if __name__ == "__main__":
    # --- Load Data ---
    try: # if there is a previously processed file, load it
        df = pd.read_pickle(f"data/{EXCEL_FILE}_{SHEET}.pkl")
        print(f"Loaded processed data from {EXCEL_FILE}_{SHEET}.pkl")
    except:
        df = load_and_preprocess_data()

    # Positioning in Miro board
    effort = df.loc['effort']
    effort_min = effort.min()
    effort_max = effort.max()
    df.loc['x'] = ((effort - effort_min) / (effort_max - effort_min)) * SCALE
    df.loc['y'] = df.loc['impact'] * SCALE  # impact [0, 1] scale to [0, SCALE]

    # --- Coloring use cases by projects ---
    df.loc['Color'] = extract_subcategory_cluster(df.loc['Project'])
    df.loc['Color'] = df.loc['Color'].map(lambda x: COLORS_STICKY_NOTES_MIRO[x % len(COLORS_STICKY_NOTES_MIRO)])

    # --- Create sticky notes in Miro ---
    for i, (use_case, col) in enumerate(df.items()):
        x  = col.at['x']
        y  = col.at['y']
        if pd.isna(x) or pd.isna(y): continue  # skip creating the note
        print(f"Creating sticky note for '{use_case}' at ({x}, {y})")
        df.at['id_miro', use_case] = miro.create_sticky_note(str(i), col.at['Color'], x, y, width=SCALE/20)
        # Alternatively, create a shape:
        # df.at['id_miro', use_case] = miro.create_shape(x , y, shape="rectangle", width=10, height=10,
        #     fill_color=col.at['Color'], border_color="#1a1a1a",
        #     content=str(i)
        # )

    # --- Add Connectors based on 'Solution subcategory' ---
    connections = get_connections_by_subcategory(df, subcat_row='Solution subcategory')
    for idx, (u1, u2, subcat) in enumerate(connections):
        #print(f"{u1} <-> {u2} via '{subcat}'") # uncomment to debug
        id_connector = miro.create_connector(u1, u2, caption=subcat, font_size=10, color=COLORS_HEX[idx % len(COLORS_HEX)])
