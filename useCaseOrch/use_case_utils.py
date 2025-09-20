import numpy as np
import pandas as pd
import ollama

IMPACT_LEVELS = {
    'team': 0.0,
    'department': 0.166,
    'division': 0.333,
    'unit': 0.5,
    'tno': 0.666,
    'industry': 0.833,
    'society': 1.0
}

SOLUTION_CATEGORIES_GEN_AI = [
    "GEN AI INDEXING",
    "GEN AI ASSISTANTS",
    "GEN AI AGENTS",
    "GEN AI COPILOTS",
    "GEN AI PRE-PROCESSING",
    "GEN AI MODELER",
]

def extract_person_months(entry):
    try:
        return float(entry.split()[0])
    except:
        return np.nan  # or use a default value like 0

def get_impact_score_LLM(text, llm_model="llama3.1:8b"):
    prompt = f"""
    Given the following impact description: "{text}"
    Map it to a numerical score between 0 and 1 based on these levels:
    team (0.0), department (0.166), division (0.333), unit (0.5), TNO (0.666), industry (0.833), society (1.0).
    If the description is unclear and cannot be classified in any of the levels, return 0.0.
    Return only the number.
    """
    resp = ollama.generate(
        model=llm_model,
        prompt=prompt
    )
    return float(resp['response'])

def get_impact_score(text):
    """
    Maps an impact description to a numerical score based on all matching keywords.
    Returns the average score based on keywords found, or 0.0 if none found.
    """
    matches = [score for key, score in IMPACT_LEVELS.items() if key in text.lower()]
    if matches:
        return np.mean(matches)
    return 0.0 

def assign_solution_category(text_solution, text_solution_subcategory, llm_model="llama3.1:8b"):
    prompt = f"""
    Given the solution description: "{text_solution}"
    and the subcategory description: "{text_solution_subcategory}"
    Assign the most appropriate category from the following list:
    {SOLUTION_CATEGORIES_GEN_AI}.
    Return the names of the categories exactly as in the list, separated by commas.
    If none of the categories fit, return and empty string.
    """
    resp = ollama.generate(
        model=llm_model,
        prompt=prompt
    )
    return [cat.strip() for cat in resp['response'].split(',') if cat.strip()]

def extract_subcategory_cluster(series):
    """
    Assigns a unique cluster number to each unique subcategory found in a comma-separated string.
    Returns a Series of cluster numbers (for the first subcategory in each entry).
    """
    subcat_lists = series.fillna('').apply(lambda x: [s.strip() for s in str(x).split(',') if s.strip()])
    unique_subcats = sorted(set(s for sublist in subcat_lists for s in sublist))
    subcat_to_cluster = {subcat: i for i, subcat in enumerate(unique_subcats)}
    return subcat_lists.apply(lambda lst: subcat_to_cluster[lst[0]] if lst else -1)

def get_connections_by_subcategory(df, subcat_row='Solution subcategory'):
    """
    Returns a list of (id_miro1, id_miro2, subcategory) tuples for all pairs sharing at least one subcategory.
    Each pair appears only once.
    """
    from collections import defaultdict
    subcat_to_use_cases = defaultdict(list)
    for use_case, entry in df.loc[subcat_row].items():
        subcats = [s.strip() for s in str(entry).split(',') if s.strip()]
        for subcat in subcats:
            subcat_to_use_cases[subcat].append(use_case)
    connections = []
    for subcat, use_cases in subcat_to_use_cases.items():
        for i in range(len(use_cases)):
            for j in range(i + 1, len(use_cases)):
                id1 = df.at['id_miro', use_cases[i]]
                id2 = df.at['id_miro', use_cases[j]]
                if pd.notna(id1) and pd.notna(id2) and id1 != id2:
                    u1, u2 = sorted([id1, id2])
                    connections.append((u1, u2, subcat))
    connections = list(set(connections))
    return connections
