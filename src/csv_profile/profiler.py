import csv
from typing import Dict, Any, List

def analyze_csv(file_path: str) -> Dict[str, Any]:
    """Parses a CSV file and calculates structural metrics and per-column profiles."""
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        # Detect delimiter automatically (comma, tab, semicolon)
        try:
            sample = f.read(2048)
            dialect = csv.Sniffer().sniff(sample)
            f.seek(0)
        except Exception:
            f.seek(0)
            dialect = csv.get_dialect('excel') # fallback

        reader = csv.reader(f, dialect)
        headers = next(reader, None)
        
        if not headers:
            raise ValueError("The provided file appears to be empty or lacks headers.")

        num_columns = len(headers)
        rows = list(reader)
        num_rows = len(rows)

        # Initialize profile metrics per column
        col_profiles = {
            header: {"missing": 0, "types": set(), "min_len": float('inf'), "max_len": 0} 
            for header in headers
        }

        for row in rows:
            # Handle malformed rows gracefully
            for i, header in enumerate(headers):
                val = row[i].strip() if i < len(row) else ""
                
                if val == "":
                    col_profiles[header]["missing"] += 1
                else:
                    col_profiles[header]["min_len"] = min(col_profiles[header]["min_len"], len(val))
                    col_profiles[header]["max_len"] = max(col_profiles[header]["max_len"], len(val))
                    # Basic type inference
                    col_profiles[header]["types"].add(infer_type(val))

        # Finalize and format output metadata
        column_summaries = []
        for header in headers:
            prof = col_profiles[header]
            missing_pct = (prof["missing"] / num_rows * 100) if num_rows > 0 else 0
            
            # Determine dominant broad type
            types = prof["types"]
            primary_type = "Empty"
            if "string" in types: primary_type = "String"
            elif "float" in types: primary_type = "Float"
            elif "int" in types: primary_type = "Integer"

            column_summaries.append({
                "column": header,
                "type": primary_type,
                "missing_count": prof["missing"],
                "missing_percentage": round(missing_pct, 1),
                "min_length": prof["min_len"] if prof["min_len"] != float('inf') else 0,
                "max_length": prof["max_len"]
            })

        return {
            "summary": {
                "file_name": file_path.split("/")[-1],
                "rows": num_rows,
                "columns": num_columns,
            },
            "columns": column_summaries
        }

def infer_type(val: str) -> str:
    """Helper to broadly infer basic data types from string values."""
    if val.isdigit() or (val.startswith('-') and val[1:].isdigit()):
        return "int"
    try:
        float(val)
        return "float"
    except ValueError:
        return "string"
