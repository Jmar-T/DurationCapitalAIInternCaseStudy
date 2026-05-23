import os
import pandas as pd

def clean_client_names(df):
    # 1. Print how many unique dirty client names exist before cleaning
    dirty_unique_count = df['client_name'].nunique()
    # print(f"📊 Total unique dirty client names found in raw data: {dirty_unique_count}")
    
    # 2. Hardcoded Alias Map for client name variations
    acronym_map = {
        "boston med ctr": "Boston Medical Center",
        "boston medical center": "Boston Medical Center",
        "brigham & womens": "Brigham and Womens",
        "brigham and womens": "Brigham and Womens",
        "mgh": "Mass General Hospital",
        "mass general hospital": "Mass General Hospital",
        "childrens hospital": "Childrens Hospital",
        "children's hospital": "Childrens Hospital",
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
    
    # 3. Normalize the text safely and apply the mapping dictionary
    def normalize_and_map(raw_name):
        if pd.isna(raw_name):
            return raw_name
        # Lowercase and remove punctuation to prevent spacing or casing misses
        clean_key = str(raw_name).lower().replace("'", "").replace(".", "").strip()
        return acronym_map.get(clean_key, raw_name)
    
    df['client_name_clean'] = df['client_name'].apply(normalize_and_map)
    
    # 4. Print clean confirmation
    clean_unique_count = df['client_name_clean'].nunique()
    # print(f"🔄 Standardized down to {clean_unique_count} clean client groups.\n")
    
    return df

def group_weeks(file_name:str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, "..", "data", file_name)
    
    df = pd.read_csv(full_path)
    
    # Run client cleaning pipeline
    df = clean_client_names(df)
    df['service_type'] = df['service_type'].str.lower()

    # Converting time column date/time to a time date/time objects
    df['order_time'] = pd.to_datetime(df['order_time'])

    # Create a 'week' column (e.g., 2026-05-18/2026-05-24)
    df['week'] = df['order_time'].dt.to_period('W')

    # Groups order by week
    weekly_groups = df.groupby('week')
    return weekly_groups

def get_monday_report(weekly_groups):
    """
    Accepts the weekly_groups object, processes weekly metrics,
    and writes out individual text reports to the 'results' folder.
    """
    # 1. Establish where the script is, and step back one folder to the project root
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    output_dir = os.path.abspath(os.path.join(script_dir, "results"))
    
    
    # 2. Create the folder automatically if it doesn't exist yet
    os.makedirs(output_dir, exist_ok=True)

    for week_key, week_df in weekly_groups:
        # Convert the week key into a safe string filename
        start_date = str(week_key.start_time.date())
        end_date = str(week_key.end_time.date())
        filename = f"report_{start_date}_to_{end_date}.txt"

        full_output_path = os.path.join(output_dir, filename)

        # Open the text file for writing
        with open(full_output_path, mode='w', encoding='utf-8') as file:
            file.write(f"=== REPORT FOR WEEK: {start_date} to {end_date} ===\n")

            # --- Calculate Core Statistics ---
            redelivery_count = (week_df['redelivery_flag'] == 1).sum()
            total_orders = len(week_df)
            redelivery_rate = (redelivery_count / total_orders) * 100 if total_orders > 0 else 0

            exception_volume = week_df['exception_notes'].dropna().astype(str).str.strip().ne("").sum()

            file.write(f"Redelivery rate: {redelivery_rate:.2f}%\n")
            file.write(f"Exception volume: {exception_volume}\n\n")
            
            # --- Service Types  ---
            file.write("--- SERVICE TYPE PERFORMANCE ---\n")
            service_types = week_df.groupby("service_type")
            for service_type, service_types_df in service_types:
                on_time_count = (service_types_df['on_time'] == "Y").sum()
                total_ops = len(service_types_df)
                on_time_rate = (on_time_count / total_ops) * 100 if total_ops > 0 else 0
                file.write(f"{service_type} on time rate: {on_time_rate:.1f}%\n")
                
            # --- Clients  ---
            file.write("\n--- CLIENT PERFORMANCE ---\n")
            clients = week_df.groupby("client_name_clean")
            for client, client_df in clients:
                on_time_count = (client_df['on_time'] == "Y").sum()
                total_ops = len(client_df)
                on_time_rate = (on_time_count / total_ops) * 100 if total_ops > 0 else 0
                file.write(f"{client} on time rate: {on_time_rate:.1f}%\n")

            # --- Drivers  ---
            file.write("\n--- DRIVER PERFORMANCE ---\n")
            drivers = week_df.groupby('driver_id')
            for driver, driver_df in drivers:
                on_time_count = (driver_df['on_time'] == "Y").sum()
                total_ops = len(driver_df)
                on_time_rate = (on_time_count / total_ops) * 100 if total_ops > 0 else 0
                file.write(f"{driver} on time rate: {on_time_rate:.1f}%\n")

        print(f"💾 Saved text report to: {full_output_path}")


    print(f"\n✅ Execution complete. Created reports inside: {output_dir}")
            
weekly_groups = group_weeks("dispatch_log_q1(in).csv")
get_monday_report(weekly_groups)