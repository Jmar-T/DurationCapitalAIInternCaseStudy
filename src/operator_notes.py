import os
import re
import pandas as pd

# Paths to the local data files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DRIVER_NOTES_PATH = os.path.join(SCRIPT_DIR, "..", "data", "local_driver_notes.csv")
CLIENT_NOTES_PATH = os.path.join(SCRIPT_DIR, "..", "data", "local_client_notes.csv")

def initialize_notes_files():
    """Creates empty template CSVs with correct headers if they don't exist."""
    os.makedirs(os.path.dirname(DRIVER_NOTES_PATH), exist_ok=True)
    
    if not os.path.exists(DRIVER_NOTES_PATH):
        df = pd.DataFrame(columns=["driver_id", "driver_name", "general_notes"])
        # Seed with a placeholder row for Marcus as a quick reference
        df.loc[0] = ["D035", "Marcus", "Avoids North Side on Monday mornings."]
        df.to_csv(DRIVER_NOTES_PATH, index=False)
        print("Initialized local_driver_notes.csv with sample configuration.")
        
    if not os.path.exists(CLIENT_NOTES_PATH):
        df = pd.DataFrame(columns=["client_clean_name", "general_notes"])
        df.to_csv(CLIENT_NOTES_PATH, index=False)
        print("Initialized local_client_notes.csv template.")

def _determine_routing(query: str):
    """
    Internal helper using Regular Expressions and local records to determine 
    if an input targets a driver (via DXXX ID or name match) or a client.
    """
    query_clean = query.strip()
    
    # 1. Regex check: Matches 'D' or 'd' followed by exactly 3 digits (e.g., D035)
    if re.match(r"^[Dd]\d{3}$", query_clean):
        return "driver", query_clean.upper()
        
    # 2. Database check: If it's not a DXXX ID, check if the name exists in driver records
    if os.path.exists(DRIVER_NOTES_PATH):
        try:
            driver_df = pd.read_csv(DRIVER_NOTES_PATH)
            known_drivers = driver_df['driver_name'].astype(str).str.lower().str.strip().tolist()
            
            if query_clean.lower() in known_drivers:
                return "driver", query_clean
        except Exception:
            pass # Fallback safely if file is empty or corrupted during read

    # 3. Client Fallback: Clean string using corporate map logic
    try:
        from clean_data import clean_input_client_name
        lookup_key = clean_input_client_name(query_clean)
    except ImportError:
        lookup_key = query_clean
        
    return "client", lookup_key

def add_or_update_note():
    """
    Interactive utility to add or update operator notes for a driver or client.
    Pulls existing notes if they exist before accepting modifications.
    """
    initialize_notes_files()
    
    print("\n=========================================")
    print("ADD / UPDATE OPERATOR NOTES")
    print("=========================================\n")
    
    user_query = input("Enter Driver ID/Name or Client Name to edit: ").strip()
    if not user_query:
        print("Entry target cannot be empty.")
        return

    entity_type, standard_key = _determine_routing(user_query)

    if entity_type == "driver":
        df = pd.read_csv(DRIVER_NOTES_PATH)
        match = df[
            (df['driver_id'].astype(str).str.lower() == standard_key.lower()) | 
            (df['driver_name'].astype(str).str.lower() == standard_key.lower())
        ]
        
        if not match.empty:
            idx = match.index[0]
            current_notes = df.loc[idx, 'general_notes']
            driver_id = df.loc[idx, 'driver_id']
            driver_name = df.loc[idx, 'driver_name']
            print(f"\nFound existing profile for {driver_name} [{driver_id}].")
            print(f"Current Notes: \"{current_notes}\"")
        else:
            idx = len(df)
            is_id = bool(re.match(r"^[Dd]\d{3}$", standard_key))
            driver_id = standard_key.upper() if is_id else "UNKNOWN"
            
            if is_id:
                driver_name = input(f"Creating profile for ID {driver_id}. Enter Driver Name: ").strip().title()
                if not driver_name:
                    driver_name = "Unknown Driver"
            else:
                driver_name = standard_key.title()
                
            print(f"\nCreating a brand new local note profile for Driver: '{driver_name}'.")
            current_notes = ""

        new_notes = input("Enter updated notes (Press Enter to keep current/blank): ").strip()
        
        if new_notes:
            df.loc[idx, 'general_notes'] = new_notes
        elif not current_notes:
            df.loc[idx, 'general_notes'] = ""
            
        df.loc[idx, 'driver_id'] = driver_id
        df.loc[idx, 'driver_name'] = driver_name
        df.to_csv(DRIVER_NOTES_PATH, index=False)
        print("Driver notes updated and written to local database safely.")

    elif entity_type == "client":
        df = pd.read_csv(CLIENT_NOTES_PATH)
        match = df[df['client_clean_name'].astype(str).str.lower() == standard_key.lower()]
        
        if not match.empty:
            idx = match.index[0]
            current_notes = df.loc[idx, 'general_notes']
            print(f"\nFound existing profile for Client group: '{standard_key}'.")
            print(f"Current Notes: \"{current_notes}\"")
        else:
            idx = len(df)
            print(f"\nCreating a brand new local note profile for Client group: '{standard_key}'.")
            current_notes = ""

        new_notes = input("Enter updated notes (Press Enter to keep current/blank): ").strip()
        
        if new_notes:
            df.loc[idx, 'general_notes'] = new_notes
        elif not current_notes:
            df.loc[idx, 'general_notes'] = ""
            
        df.loc[idx, 'client_clean_name'] = standard_key
        df.to_csv(CLIENT_NOTES_PATH, index=False)
        print("Client notes updated and written to local database safely.")

def get_profile_notes():
    """
    Interactive utility to query local dispatcher knowledge files.
    """
    initialize_notes_files()
    
    print("\n=========================================")
    print("RETRIEVE OPERATOR NOTES")
    print("=========================================\n")
    
    user_query = input("Enter Search Target (Driver ID/Name or Client Name): ").strip()
    if not user_query:
        print("Search string cannot be empty.")
        return

    entity_type, standard_key = _determine_routing(user_query)

    if entity_type == "driver":
        df = pd.read_csv(DRIVER_NOTES_PATH)
        match = df[
            (df['driver_id'].astype(str).str.lower() == standard_key.lower()) | 
            (df['driver_name'].astype(str).str.lower() == standard_key.lower())
        ]
        
        if match.empty:
            print(f"\nNo operational notes logged for Driver matching: '{user_query}'")
            return
            
        row = match.iloc[0]
        print("\n----------------------------------------------------------------------")
        print(f"DRIVER CONTEXT PROFILE: {row['driver_name']} [{row['driver_id']}]")
        print("----------------------------------------------------------------------")
        print(f"Operator Notes: {row['general_notes']}")
        print("----------------------------------------------------------------------\n")

    elif entity_type == "client":
        df = pd.read_csv(CLIENT_NOTES_PATH)
        match = df[df['client_clean_name'].astype(str).str.lower() == standard_key.lower()]
        
        if match.empty:
            print(f"\nNo operational notes logged for Client matching: '{user_query}'")
            return
            
        row = match.iloc[0]
        print("\n----------------------------------------------------------------------")
        print(f"CLIENT CONTEXT PROFILE: {row['client_clean_name']}")
        print("----------------------------------------------------------------------")
        print(f"Operator Notes: {row['general_notes']}")
        print("----------------------------------------------------------------------\n")

if __name__ == "__main__":
    while True:
        print("\n=== OPERATOR LOGISTICS NOTE MANAGEMENT ===")
        print("1. Add / Update Notes")
        print("2. Search / Retrieve Notes")
        print("3. Exit System")
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            add_or_update_note()
        elif choice == "2":
            get_profile_notes()
        elif choice == "3":
            print("Shutting down note interface pipeline.")
            break
        else:
            print("Invalid selection. Choose options 1, 2, or 3.")