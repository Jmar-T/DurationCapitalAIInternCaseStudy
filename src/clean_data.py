import pandas as pd

# Hardcoded Alias Map for client name variations (Keys must be fully normalized)
acronym_map = {
    "boston med ctr": "Boston Medical Center",
    "boston medical center": "Boston Medical Center",
    "brigham & womens": "Brigham and Womens",
    "brigham and womens": "Brigham and Womens",
    "mgh": "Mass General Hospital",
    "mass general hospital": "Mass General Hospital",
    "childrens hospital": "Childrens Hospital",
    "ne labs": "Northeast Laboratory",
    "northeast labs": "Northeast Laboratory",
    "northeast laboratory": "Northeast Laboratory",
    "quest diag": "Quest Diagnostics",
    "quest diagnostics": "Quest Diagnostics",
    "tufts med center": "Tufts Medical",
    "tufts medical": "Tufts Medical",
    "labcorp inc": "LabCorp",
    "labcorp": "LabCorp",
    "bio_reference_labs": "BioReference Labs",
    "bioreference labs": "BioReference Labs"
}

def _normalize_string(text: str) -> str:
    """Helper utility to ensure input matching across dataframes and user prompts."""
    if pd.isna(text):
        return ""
    # Strip spaces, punctuation, dashes, and underscores for  matching 
    return str(text).lower().replace("'", "").replace(".", "").replace("-", " ").replace("_", " ").strip()

def clean_client_names(df):
    df = df.copy()
    dirty_unique_count = df['client_name'].nunique()
    print(f"Total unique dirty client names found in raw data: {dirty_unique_count}")
    
    # Apply normalized mapping
    df['client_name_clean'] = df['client_name'].apply(
        lambda x: acronym_map.get(_normalize_string(x), str(x).strip().title())
    )
    
    clean_unique_count = df['client_name_clean'].nunique()
    print(f"Standardized down to {clean_unique_count} clean client groups.\n")
    
    return df

def clean_input_client_name(name: str) -> str:
    """
    Standardizes interactive user input to match the database dictionary keys.
    Returns the cleaned name or a title-cased fallback if not explicitly mapped.
    """
    normalized_input = _normalize_string(name)
    
    # If it matches an alias, return the standardized corporate entity name.
    # Otherwise, return a title-case variation instead of an error message.
    return acronym_map.get(normalized_input, name.strip().title())