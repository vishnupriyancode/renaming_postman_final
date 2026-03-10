# Configuration file for multiple models
# This file now supports both static configurations and dynamic discovery

import os
import json
from dynamic_models import discover_ts_folders, get_model_by_ts_number, get_all_models

# Static model configurations (for backward compatibility)
STATIC_MODELS_CONFIG = {
    "wgs_csbd": [
        {
            "ts_number": "01",
            "edit_id": "01",
            "code": "00",
            "source_dir": "source_folder/WGS_CSBD/CSBDTS_01_sample_WGS_CSBD_M000001_00W04_sur/payloads/regression",
            "dest_dir": "renaming_jsons/CSBDTS/CSBDTS_01_sample_WGS_CSBD_M000001_00W04_dis/payloads/regression",
            "postman_collection_name": "TS_01_sample_Collection",
            "postman_file_name": "sample_wgs_csbd_M000001_00W04.json"
        }
    ],
    "gbdf_mcr": 
    [    {
        "ts_number": "46",
        "edit_id": "RULEEM000001",
        "code": "v04",
        "source_dir": "source_folder/GBDF/GBDTS_46_Covid_gbd_mcr_RULEEM000001_v04_sur/payloads/regression",
        "dest_dir": "renaming_jsons/GBDTS/GBDTS_46_Covid_gbd_mcr_RULEEM000001_v04_dis/payloads/regression",
        "postman_collection_name": "GBDTS_46_Covid_Collection",
        "postman_file_name": "covid_model_gbdf_mcr_RULEEM000001_v04.json"
    }
],
"gbdf_grs": [    
    {
        "ts_number": "47",
        "edit_id": "RULEEM000001",
        "code": "v04",
        "source_dir": "source_folder/GBDF/TS_47_Covid_gbd_grs_RULEEM000001_v04_sur/payloads/regression",
        "dest_dir": "renaming_jsons/GBDTS/TS_47_sample_sampple_RULEEM000001_v04_dis/payloads/regression",
        "postman_collection_name": "TS_47_Covid_Collection",
        "postman_file_name": "sample_model_gbdf_grs_RULEEM000001_v04.json"
    }
    ],
    "gbdf_mmp": [   
        {
        "ts_number": "64",
        "edit_id": "Ambulance Mileage without Base Transport Paid IPREP 192",
        "code": "v37",
        "source_dir": "source_folder/GBDF/sample Mileage without Base Transport Paid IPREP 192_v37_sur/payloads/regression",
        "dest_dir": "renaming_jsons/GBDTS/GBDTS_64_Gbdf_gbd_mmp_Ambulance Mileage without Base Transport Paid IPREP 192_v37_dis/payloads/regression",
        "postman_collection_name": "GBDTS_64_Gbdf_Collection",
        "postman_file_name": "gbdf_mmp_shadow_ruleambu000001_grs_v37_edits_group9_Ambulance Mileage without Base Transport Paid IPREP 192_v37.json"
    }
    ],
    "wgs_kernal": [
        {
            "ts_number": "100",
            "edit_id": "RULEPREV000001",
            "code": "00W28",
            "source_dir": "source_folder/WGS_Kernal/sample_100_Preventative_WGS_NYK_RULEPREV000001_00W28_sur/payloads/regression",
            "dest_dir": "renaming_jsons/NYKTS/sample_100_Preventative_WGS_NYK_RULEPREV000001_00W28_dis/payloads/regression",
            "postman_collection_name": "sample_100_Preventative_Collection",
            "postman_file_name": "preventative_medicine_and_screening_iprep_362_wgs_nyk_RULEPREV000001_00W28.json"
        }
    ]
}


def _expand_config_list_with_smoke(config_list):
    """
    For each config whose source_dir/dest_dir point to .../payloads/regression,
    if .../payloads/smoke exists on disk, add a matching smoke config so smoke
    collections are renamed for GBDF (MCR/GRS/MMP) and other payloads-based models.
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
def get_models_config(use_dynamic=True, use_wgs_csbd_destination=False, use_gbd_mcr=False, use_gbd_grs=False, use_gbd_mmp=False, use_wgs_nyk=False):
    """
    Get model configurations using dynamic discovery or static config.
    When using dynamic discovery, static config (e.g. models added from Excel) is
    merged in so that python main_processor.py --wgs_csbd --CSBDTSxx etc. work
    for any model in the config list.

    Args:
        use_dynamic: If True, use dynamic discovery; if False, use static config
        use_wgs_csbd_destination: If True, use WGS_CSBD as destination folder instead of renaming_jsons
        use_gbd_mcr: If True, use GBDF MCR models instead of WGS_CSBD
        use_gbd_grs: If True, use GBDF GRS models instead of WGS_CSBD
        use_gbd_mmp: If True, use GBDF MMP models instead of WGS_CSBD
        use_wgs_nyk: If True, use WGS_NYK models instead of WGS_CSBD

    Returns:
        List of model configurations
    """
    if use_dynamic:
        try:
            if use_wgs_nyk:
                # Use dynamic discovery for WGS_NYK
                discovered_models = discover_ts_folders("source_folder/WGS_Kernal", False)
                merged = _merge_static_models(discovered_models, "wgs_kernal")
                if discovered_models:
                    print(f"Dynamic discovery found {len(discovered_models)} WGS_NYK models")
                if not discovered_models:
                    print("No WGS_NYK models found via dynamic discovery, using static config")
                return merged
            elif use_gbd_mcr:
                # Use dynamic discovery for GBDF MCR
                discovered_models = discover_ts_folders("source_folder/GBDF", False)
                # Filter for MCR models only (exclude GRS)
                mcr_models = [
                    m for m in discovered_models 
                    if ("gbdf_mcr" in m.get("source_dir", "").lower() or "gbd_mcr" in m.get("source_dir", "").lower()
                        or "gbdf_mcr" in m.get("folder_name", "").lower() or "gbd_mcr" in m.get("folder_name", "").lower())
                    and "gbdf_grs" not in m.get("source_dir", "").lower()
                    and "gbd_grs" not in m.get("source_dir", "").lower()
                    and "gbdf_grs" not in m.get("folder_name", "").lower()
                    and "gbd_grs" not in m.get("folder_name", "").lower()
                ]
                merged = _merge_static_models(mcr_models, "gbdf_mcr")
                if mcr_models:
                    print(f"Dynamic discovery found {len(mcr_models)} GBDF MCR models")
                if not mcr_models:
                    print("No GBDF MCR models found via dynamic discovery, using static config")
                return merged
            elif use_gbd_grs:
                # Use dynamic discovery for GBDF GRS
                discovered_models = discover_ts_folders("source_folder/GBDF", False)
                grs_models = [
                    m for m in discovered_models 
                    if "gbdf_grs" in m.get("source_dir", "").lower() or "gbd_grs" in m.get("source_dir", "").lower()
                    or "gbdf_grs" in m.get("folder_name", "").lower() or "gbd_grs" in m.get("folder_name", "").lower()
                ]
                merged = _merge_static_models(grs_models, "gbdf_grs")
                if grs_models:
                    print(f"Dynamic discovery found {len(grs_models)} GBDF GRS models")
                if not grs_models:
                    print("No GBDF GRS models found via dynamic discovery, using static config")
                return merged
            elif use_gbd_mmp:
                # Use dynamic discovery for GBDF MMP
                discovered_models = discover_ts_folders("source_folder/GBDF", False)
                mmp_models = [
                    m for m in discovered_models
                    if ("gbdf_mmp" in m.get("source_dir", "").lower() or "gbd_mmp" in m.get("source_dir", "").lower()
                        or "gbdf_mmp" in m.get("folder_name", "").lower() or "gbd_mmp" in m.get("folder_name", "").lower())
                ]
                merged = _merge_static_models(mmp_models, "gbdf_mmp")
                if mmp_models:
                    print(f"Dynamic discovery found {len(mmp_models)} GBDF MMP models")
                if not mmp_models:
                    print("No GBDF MMP models found via dynamic discovery, using static config")
                return merged
            else:
                # Use dynamic discovery for WGS_CSBD
                discovered_models = discover_ts_folders("source_folder/WGS_CSBD", True)
                merged = _merge_static_models(discovered_models, "wgs_csbd")
                if discovered_models:
                    print(f"Dynamic discovery found {len(discovered_models)} WGS_CSBD models")
                if not discovered_models:
                    print("No WGS_CSBD models found via dynamic discovery, using static config")
                return merged
        except Exception as e:
            print(f"Dynamic discovery failed: {e}, falling back to static config")
            if use_wgs_nyk:
                return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("wgs_kernal", []))
            elif use_gbd_mcr:
                return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_mcr", []))
            elif use_gbd_grs:
                return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_grs", []))
            elif use_gbd_mmp:
                return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_mmp", []))
            else:
                return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("wgs_csbd", []))
    else:
        if use_wgs_nyk:
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("wgs_kernal", []))
        elif use_gbd_mcr:
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_mcr", []))
        elif use_gbd_grs:
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_grs", []))
        elif use_gbd_mmp:
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("gbdf_mmp", []))
        else:
            return _expand_config_list_with_smoke(STATIC_MODELS_CONFIG.get("wgs_csbd", []))

def get_model_by_ts(ts_number):
    """
    Get a specific model by TS number using dynamic discovery.
    
    Args:
        ts_number: TS number (e.g., "01", "02", "03")
        
    Returns:
        Model configuration dict or None if not found
    """
    try:
        return get_model_by_ts_number(ts_number, "source_folder/WGS_CSBD")
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


def apply_header_footer_to_json(file_path, is_wgs_kernal=False):
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
    - meta-transid: WGS_Kernal uses "20240705012036TMBLMMY437A003580999CS90TIMBER01",
                   WGS_CSBD uses "20220117181853TMBL20359Cl893580999"
    - protegrity / Protigrity: "false" (for WGS_Kernal and WGS_CSBD models)
    
    Args:
        file_path: Path to the JSON file to transform
        is_wgs_kernal: If True, use WGS_Kernal meta-transid; else use WGS_CSBD meta-transid
        
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
        
        # meta-transid: WGS_Kernal uses dedicated value; WGS_CSBD uses legacy value
        meta_transid = "20240705012036TMBLMMY437A003580999CS90TIMBER01" if is_wgs_kernal else "20220117181853TMBL20359Cl893580999"
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
    for WGS_CSBD and WGS_Kernal models.
    
    This function recursively finds all JSON files in:
    - renaming_jsons/CSBDTS/**
    - renaming_jsons/NYKTS/**
    
    and applies the header/footer structure to each file.
    
    Returns:
        dict: Statistics about processed files
    """
    base_dir = "renaming_jsons"
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Directories to process
    target_dirs = [
        os.path.join(base_dir, "WGS_CSBD"),
        os.path.join(base_dir, "WGS_KERNAL")
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
        is_wgs_kernal = "WGS_KERNAL" in target_dir.upper()
        for root, dirs, files in os.walk(target_dir):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    
                    # Apply header/footer (function will handle both new and existing structures)
                    if apply_header_footer_to_json(file_path, is_wgs_kernal=is_wgs_kernal):
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
    print("Header/Footer Application for WGS_CSBD and WGS_Kernal Models")
    print("=" * 60)
    print("\nThis script will apply header and footer structure to all JSON files")
    print("in renaming_jsons/WGS_CSBD and renaming_jsons/WGS_KERNAL directories.\n")
    
    # Apply header/footer to all JSON files
    stats = apply_header_footer_to_renaming_jsons()
    
    print(f"\n✓ Process completed successfully!")
    print(f"  - Processed: {stats['processed']} files")
    print(f"  - Skipped: {stats['skipped']} files")
    print(f"  - Errors: {stats['errors']} files")
