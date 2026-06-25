# Configuration file for multiple models
# This file now supports both static configurations and dynamic discovery

import os
import json
from dynamic_models import discover_ts_folders, get_model_by_ts_number, get_all_models


# Static model configurations (for backward compatibility)
STATIC_MODELS_CONFIG = {
    "model_1": [
        {
            "ts_number": "01",
            "edit_id": "M000001",
            "code": "00W04",
            "source_dir": "source_folder/Model/Model_01_sample_model_1_M000001_00W04_sur/payloads",
            "dest_dir": "renaming_jsons/Model/Model_01_sample_model_1_M000001_00W04_dis/payload",
            "postman_collection_name": "TS_01_sample_Collection",
            "postman_file_name": "sample_model_1_M000001_00W04.json"
        },
        {
            "ts_number": "02",
            "edit_id": "00001",
            "code": "00W00",
            "source_dir": "source_folder/model_1/Model_02_Model_model_1_00001_00W00_sur/payloads/regression",
            "dest_dir": "renaming_jsons/model_1/Model_02_Model_model_1_00001_00W00_dis/payloads/regression",
            "postman_collection_name": "Model_02_Model_Collection",
            "postman_file_name": "model_1_sample_model_cba_dfg_m1_001_00001_00W00.json"
        }
    ]
}




def _expand_config_list_with_smoke(config_list):
    """
    For each config whose source_dir/dest_dir point to .../payloads/regression,
    if .../payloads/smoke exists on disk, add a matching smoke config so smoke
    collections are renamed for payloads-based models.
    """
    if not config_list:
        return config_list
    result = []
    for m in config_list:
        result.append(m)
        src = m.get("source_dir") or ""
        dest = m.get("dest_dir") or ""
        if "/payloads/regression" not in src or "/payloads/regression" not in dest:
            continue
        smoke_src = src.replace("/payloads/regression", "/payloads/smoke")
        smoke_dest = dest.replace("/payloads/regression", "/payloads/smoke")
        if not os.path.exists(smoke_src):
            continue
        smoke_config = dict(m)
        smoke_config["source_dir"] = smoke_src
        smoke_config["dest_dir"] = smoke_dest
        smoke_config["folder_type"] = "smoke"
        pname = (m.get("postman_file_name") or "collection.json").replace(".json", "").rstrip("_regression")
        smoke_config["postman_file_name"] = f"{pname}_smoke.json"
        result.append(smoke_config)
    return result


def _merge_static_models(discovered_models, static_key):
    """
    Merge static config entries (e.g. from Excel) into discovered list so that
    models added to STATIC_MODELS_CONFIG are available for main_processor.py CLI.
    Static entries whose ts_number is not already in discovered are appended.
    Static-only entries are expanded to include smoke config when payloads/smoke exists.
    """
    if not discovered_models:
        static_list = list(STATIC_MODELS_CONFIG.get(static_key, []))
        return _expand_config_list_with_smoke(static_list)
    static_list = STATIC_MODELS_CONFIG.get(static_key, [])
    if not static_list:
        return discovered_models
    discovered_ts = {m.get("ts_number") for m in discovered_models if m.get("ts_number")}
    extra = [m for m in static_list if m.get("ts_number") and m.get("ts_number") not in discovered_ts]
    if extra:
        extra = _expand_config_list_with_smoke(extra)
        ts_list = ", ".join(f"TS_{m.get('ts_number')}" for m in extra if m.get("ts_number"))
        num_ts = len(set(m.get("ts_number") for m in extra if m.get("ts_number")))
        print(f"Merged {num_ts} model(s) from config (e.g. from Excel) not yet on disk: {ts_list}")
    return list(discovered_models) + extra


# Dynamic model discovery
def get_models_config(use_dynamic=True, use_model_1_destination=False):
    """
    Get model configurations using dynamic discovery or static config.
    When using dynamic discovery, static config (e.g. models added from Excel) is
    merged in so that python main_processor.py --model_1 --TSxx etc. work
    for any model in the config list.

    Args:
        use_dynamic: If True, use dynamic discovery; if False, use static config
        use_model_1_destination: If True, use model_1 as destination folder instead of renaming_jsons

    Returns:
        List of model configurations
    """
    # Only support model_1. Dynamic discovery
    # looks for TS folders under "source_folder/model_1" and merges any static
    # config entries for "model_1".
    if use_dynamic:
        try:
            discovered_models = discover_ts_folders("source_folder/model_1", True)
            merged = _merge_static_models(discovered_models, "model_1")
            if discovered_models:
                print(f"Dynamic discovery found {len(discovered_models)} model_1 models")
            if not discovered_models:
                print("No model_1 models found via dynamic discovery, using static config")
            return merged
        except Exception as e:
            print(f"Dynamic discovery failed: {e}, falling back to static config")
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("model_1", []))
    else:
        return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("model_1", []))

def get_model_by_ts(ts_number):
    """
    Get a specific model by TS number using dynamic discovery.
    
    Args:
        ts_number: TS number (e.g., "01", "02", "03")
        
    Returns:
        Model configuration dict or None if not found
    """
    try:
        return get_model_by_ts_number(ts_number, "source_folder/model_1")
    except Exception as e:
        print(f"Error getting model for TS_{ts_number}: {e}")
        return None

# For backward compatibility, lazily resolve MODELS_CONFIG on access
def __getattr__(name):
    if name == "MODELS_CONFIG":
        return get_models_config(use_dynamic=True)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Global settings
GENERATE_POSTMAN_COLLECTIONS = True
VERBOSE_OUTPUT = True


def apply_header_footer_to_json(file_path, is_model_4=False):
    """
    Apply header and footer structure to JSON files.
    Wraps the existing JSON content with header and footer metadata.
    
    This function ALWAYS ensures the header/footer structure is present,
    even if the file already has it (to ensure consistency).
    
    Header structure:
    - adhoc: "true"
    - analyticId: " "
    - hints: ["congnitive_claims_async"]
    - payload: {existing JSON content}
    
    Footer structure:
    - responseRequired: "false"
    - meta-src-envrmt: "IMST"
    - meta-transid: "20220117181853TMBL20359Cl893580999" for model_1
    
    Args:
        file_path: Path to the JSON file to transform
        is_model_4: Unused; kept for backward compatibility
        
    Returns:
        bool: True if transformation was successful, False otherwise
    """
    try:
        # Read the existing JSON content
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Check if the file already has the correct structure
        has_correct_structure = (isinstance(existing_data, dict) and 
                                "adhoc" in existing_data and 
                                "payload" in existing_data and 
                                "responseRequired" in existing_data and
                                "meta-src-envrmt" in existing_data and
                                "meta-transid" in existing_data)
        
        meta_transid = "20220117181853TMBL20359Cl893580999"
        # Header and footer structure (always use these values)
        header_footer = {
            "adhoc": "true",
            "analyticId": " ",
            "hints": ["congnitive_claims_async"],
            "responseRequired": "false",
            "meta-src-envrmt": "IMST",
            "meta-transid": meta_transid,
            "protegrity": "false",
            "Protigrity": "false"
        }
        
        # Always ensure header/footer structure is correct
        if has_correct_structure:
            # File has structure, but ensure all header/footer fields are correct
            new_structure = {
                "adhoc": header_footer["adhoc"],
                "analyticId": header_footer["analyticId"],
                "hints": header_footer["hints"],
                "payload": existing_data.get("payload", existing_data),  # Use existing payload or entire data
                "responseRequired": header_footer["responseRequired"],
                "meta-src-envrmt": header_footer["meta-src-envrmt"],
                "meta-transid": header_footer["meta-transid"],
                "protegrity": header_footer["protegrity"],
                "Protigrity": header_footer["Protigrity"]
            }
            
            # Preserve any additional fields that might exist
            for key, value in existing_data.items():
                if key not in ["adhoc", "analyticId", "hints", "payload", "responseRequired", "meta-src-envrmt", "meta-transid", "protegrity", "Protigrity"]:
                    new_structure[key] = value
            
            # Write the updated structure back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Updated header/footer structure in: {file_path}")
        else:
            # File doesn't have correct structure, wrap existing data in payload
            new_structure = {
                "adhoc": header_footer["adhoc"],
                "analyticId": header_footer["analyticId"],
                "hints": header_footer["hints"],
                "payload": existing_data,  # The existing JSON becomes the payload
                "responseRequired": header_footer["responseRequired"],
                "meta-src-envrmt": header_footer["meta-src-envrmt"],
                "meta-transid": header_footer["meta-transid"],
                "protegrity": header_footer["protegrity"],
                "Protigrity": header_footer["Protigrity"]
            }
            
            # Write the transformed JSON back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_structure, f, indent=2, ensure_ascii=False)
            print(f"[SUCCESS] Applied header/footer to: {file_path}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error parsing JSON in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Error applying header/footer to {file_path}: {e}")
        return False


def apply_header_footer_to_renaming_jsons():
    """
    Apply header and footer to all JSON files in renaming_jsons folder
    for model_1.
    
    This function recursively finds all JSON files in:
    - renaming_jsons/model_1/**
    
    and applies the header/footer structure to each file.
    
    Returns:
        dict: Statistics about processed files
    """
    base_dir = "renaming_jsons"
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Directories to process (model_1 only)
    target_dirs = [
        os.path.join(base_dir, "model_1")
    ]
    
    print("=" * 60)
    print("Applying header/footer to JSON files")
    print("=" * 60)
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            print(f"[WARNING] Directory not found: {target_dir}")
            continue
        
        print(f"\nProcessing directory: {target_dir}")
        print("-" * 60)
        
        # Recursively find all JSON files
        for root, dirs, files in os.walk(target_dir):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    
                    # Apply header/footer (function will handle both new and existing structures)
                    if apply_header_footer_to_json(file_path):
                        processed_count += 1
                    else:
                        error_count += 1
    
    print("\n" + "=" * 60)
    print("Header/Footer Application Summary")
    print("=" * 60)
    print(f"Processed: {processed_count} files")
    print(f"Skipped (already correct): {skipped_count} files")
    print(f"Errors: {error_count} files")
    print("=" * 60)
    
    return {
        "processed": processed_count,
        "skipped": skipped_count,
        "errors": error_count
    }


# Main section - allows running this script directly to apply header/footer
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Header/Footer Application for model_1")
    print("=" * 60)
    print("\nThis script will apply header and footer structure to all JSON files")
    print("in renaming_jsons/model_1 directories.\n")
    
    # Apply header/footer to all JSON files
    stats = apply_header_footer_to_renaming_jsons()
    
    print(f"\n✓ Process completed successfully!")
    print(f"  - Processed: {stats['processed']} files")
    print(f"  - Skipped: {stats['skipped']} files")
    print(f"  - Errors: {stats['errors']} files")
