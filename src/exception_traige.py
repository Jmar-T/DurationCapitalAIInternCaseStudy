import os
import pandas as pd
from transformers import pipeline
from datetime import datetime
from clean_data import clean_client_names

def triage_dispatch_exceptions(file_name: str):
    # 1. Absolute pathing relative to the location of this script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.abspath(os.path.join(script_dir, "..", "data", file_name))
    
    # Paths for all 3 output buckets anchored perfectly to the project root
    results_dir = os.path.abspath(os.path.join(script_dir, "..", "results"))
    os.makedirs(results_dir, exist_ok=True)

    # Time string like: "2026-05-23_13-05" (Year-Month-Day_Hour-Minute)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    urgent_path = os.path.join(results_dir, f"urgent_actions_{timestamp}.txt")
    deferred_path = os.path.join(results_dir, f"deferred_actions_{timestamp}.txt")
    log_only_path = os.path.join(results_dir, f"log_only_records_{timestamp}.txt")
    
    # 2. Load the log dataset
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    
    # Run client cleaning pipeline to maintain name consistency across output files
    df = clean_client_names(df)
    
    # 3. Optimize ML execution: Extract unique, non-null exception text
    print("Extracting unique exceptions for optimization...")
    unique_notes = df['exception_notes'].dropna().unique()
    unique_notes = [str(note).strip() for note in unique_notes if str(note).strip()]
    
    if not unique_notes:
        print("No exceptions found in the log file! Exiting pipeline smoothly.")
        return

    model_name = "valhalla/distilbart-mnli-12-1"
    local_model_dir = os.path.join(script_dir, "..", "models", "distilbart_zero_shot")
    
    print("Initializing ML engine...")
    if not os.path.exists(local_model_dir):
        print("First run detected: Downloading and saving model locally to models/ directory...")
        pipe = pipeline("zero-shot-classification", model=model_name)
        pipe.save_pretrained(local_model_dir)
    else:
        print("Local copy found! Loading model directly from project folder...")
        pipe = pipeline("zero-shot-classification", model=local_model_dir)
        
    # Core classification buckets
    candidate_labels = ["URGENT", "DEFERRABLE", "LOG_ONLY"]
    
    # 5. Batch-process unique values through the model to maximize speed
    print(f"Triaging {len(unique_notes)} unique operational anomalies...")
    predictions = pipe(unique_notes, candidate_labels=candidate_labels)
    
    # map: { "raw text exception": "WINNING_LABEL" }
    triage_map = {}
    for pred in predictions:
        triage_map[pred['sequence']] = pred['labels'][0]
        
    # 6. Open all 3 target files concurrently and stream row-by-row data
    print("Directing incident vectors to target files...")
    with open(urgent_path, "w") as f_urgent, \
         open(deferred_path, "w") as f_deferred, \
         open(log_only_path, "w") as f_log:
         
        # Headers to the files
        f_urgent.write("=== URGENT EXCEPTIONS (IMMEDIATE ACTION REQUIRED) ===\n\n")
        f_deferred.write("=== DEFERRED EXCEPTIONS (FOLLOW-UP REQUIRED TODAY) ===\n\n")
        f_log.write("=== LOG-ONLY RECORDS (INFORMATIONAL / SUCCESS UPDATES) ===\n\n")
        
        # Loop through the master DataFrame
        for index, row in df.iterrows():
            note = row['exception_notes']
            
            # Assumes no exception note implies a clean run and no reporting required
            if pd.isna(note) or not str(note).strip():
                continue
                
            # Extract row meta-data metrics safely (using the cleaned name variant)
            order_num = row.get('order_id', 'UNKNOWN_ID')
            client = row.get('client_name_clean', 'UNKNOWN_CLIENT')
            
            # Lookup the assigned priority classification
            priority = triage_map.get(str(note).strip(), "LOG_ONLY")
            
            # Build your clean, scannable text message layout
            message = f"{priority}: Order {order_num} - {client} - Exception Note: {note}\n"
            
            # Route strictly into the correct physical text storage file
            if priority == "URGENT":
                f_urgent.write(message)
            elif priority == "DEFERRABLE":
                f_deferred.write(message)
            elif priority == "LOG_ONLY":
                f_log.write(message)
                
    print("Local AI Triage Pipeline completed successfully!")

if __name__ == "__main__":
    triage_dispatch_exceptions("dispatch_log_q1(in).csv")