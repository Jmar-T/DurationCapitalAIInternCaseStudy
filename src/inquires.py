import os
import re
import pandas as pd

# Import the cleaning functions from your clean data module
from clean_data import clean_client_names, clean_input_client_name

def check_delivery_status(file_name: str):
    # 1. Establish data pathing
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "..", "data", file_name)
    
    if not os.path.exists(input_path):
        print("Error: Database file not found.")
        return
        
    # Load raw dataframe
    raw_df = pd.read_csv(input_path)
    
    # Run background data cleaning step using your module
    # This generates the 'client_name_clean' column using acronym_map
    df = clean_client_names(raw_df)

    # Column mappings updated to match your exact CSV headers
    
    print("\n=========================================")
    print("DURATION CAPITAL CLIENT PORTAL (BETA) ")
    print("=========================================\n")
    
    # 2. Collect & normalize Client Name
    raw_client_input = input("Enter Client Name: ")
    cleaned_client_input = clean_input_client_name(raw_client_input)
    
    # 3. Collect & validate Order Number format (Strictly matching 'ORD-XXXXX')
    while True:
        input_order = input(" Enter Order ID (e.g., ORD-25000): ").strip()
        
        # Regex check: Matches 'ORD-' or 'ord-' followed by exactly 5 digits
        if re.match(r"^[Oo][Rr][Dd]-\d{5}$", input_order):
            # Standardize casing to uppercase to ensure perfect matching
            input_order = input_order.upper()
            break
        else:
            print(" Invalid format. Please ensure your Order ID follows the 'ORD-XXXXX' layout.")
    
    print(f"\n Authenticating credentials for '{cleaned_client_input}'...")
    
    # 4. Query and filter the DataFrame
    match = df[
        (df['client_name_clean'].astype(str).str.lower() == cleaned_client_input.lower()) & 
        (df['order_id'].astype(str) == input_order)
    ]

    # 5. Verification Check
    if match.empty:
        print("\n Access Denied: No matching record found for that Client/Order combination.")
        print("Please verify your credentials or contact dispatch support.")
        return
        
    # Extract the most recent tracking row context
    row = match.iloc[-1]
    driver = row.get('driver_id', 'Unassigned')
    note = row.get('exception_notes', '')
    
    # Extract operational milestones
    dispatched = row.get('dispatch_time')
    picked_up = row.get('pickup_time')
    delivered = row.get('delivery_time')

    # 6. Final Order Output Telemetry Display
    print("\n Verification Successful! Fetching real-time updates...")
    print("----------------------------------------------------------------------")
    print(f"ORDER SUMMARY FOR TRACKING ID: {input_order}")
    print(f"Client Group: {cleaned_client_input}")
    print(f" Assigned Driver: {driver}")
    print("----------------------------------------------------------------------")
    
    # 7. Step-Based Milestone Status Routing Logic
    # Check if delivery timestamp is populated
    if pd.notna(delivered) and str(delivered).strip():
        print(f"CURRENT STATUS: DELIVERED")
        print(f"Drop-off completed successfully at {delivered}.")
    
    # Check if picked up but not delivered yet
    elif pd.notna(picked_up) and str(picked_up).strip():
        print(f" CURRENT STATUS: EN ROUTE")
        print(f"Driver {driver} departed the facility at {picked_up} and is tracking toward you.")
        if pd.notna(row.get('promised_eta')):
            print(f"Promised Delivery Window: {row.get('promised_eta')}")
            
    # Check if dispatched but not yet picked up
    elif pd.notna(dispatched) and str(dispatched).strip():
        print(f"CURRENT STATUS: DISPATCHED")
        print(f"Driver {driver} was assigned at {dispatched} and is heading to the pickup point.")
        
    else:
        print(f"CURRENT STATUS: ORDER RECEIVED")
        print("Your order parameters are processing securely in our system matrix.")

    # 8. Dynamic Exception Overlay
    # If the tracking row contains an active exception, surface it directly to the customer!
    if pd.notna(note) and str(note).strip():
        print("\nACTIVE OPERATIONAL NOTE:")
        print(f"  \"{note}\"")
        
    print("----------------------------------------------------------------------\n")

if __name__ == "__main__":
    check_delivery_status("dispatch_log_q1(in).csv")