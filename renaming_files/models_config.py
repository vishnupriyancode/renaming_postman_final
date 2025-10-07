# Configuration file for multiple models
# This file now supports both static configurations and dynamic discovery

import os
from dynamic_models import discover_ts_folders, get_model_by_ts_number, get_all_models

# Static model configurations (for backward compatibility)
STATIC_MODELS_CONFIG = {
    "wgs_csbd": [
    {
        "ts_number": "01",
        "edit_id": "RULEEM000001",
        "code": "W04",
        "source_dir": "source_folder/WGS_CSBD/TS_01_Covid_WGS_CSBD_RULEEM000001_W04_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_01_Covid_WGS_CSBD_RULEEM000001_W04_dis/regression",
        "postman_collection_name": "TS_01_Covid_Collection",
        "postman_file_name": "covid_wgs_csbd_RULEEM000001_w04.json"
    },
    {
        "ts_number": "02",
        "edit_id": "RULELATE000001",
        "code": "00W17",
        "source_dir": "source_folder/WGS_CSBD/TS_02_Laterality Policy-Disgnosis to Diagnosis_WGS_CSBD_RULELATE000001_00W17_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_02_Laterality Policy-Disgnosis to Diagnosis_WGS_CSBD_RULELATE000001_00W17_dis/regression",
        "postman_collection_name": "TS_02_Laterality_Collection",
        "postman_file_name": "laterality_wgs_csbd_RULELATE000001_00w17.json"
    },
    {
        "ts_number": "03",
        "edit_id": "RULEREVE000005",
        "code": "00W28",
        "source_dir": "source_folder/WGS_CSBD/TS_03_Revenue_SubEdit5_WGS_CSBD_RULEREVE000005_00W28_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_03_Revenue_SubEdit5_WGS_RULEREVE000005_00W28/regression",
        "postman_collection_name": "TS_03_Revenue_SubEdit5_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULEREVE000005_00w28.json"
    },
    {
        "ts_number": "04",
        "edit_id": "RULEREVE000004",
        "code": "00W28",
        "source_dir": "source_folder/WGS_CSBD/TS_04_Revenue_SubEdit4_WGS_CSBD_RULEREVE000004_00W28_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_04_Revenue_SubEdit4_WGS_RULEREVE000004_00W28/regression",
        "postman_collection_name": "TS_04_Revenue_SubEdit4_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULEREVE000004_00w28.json"
    },
    {
        "ts_number": "05",
        "edit_id": "RULEREVE000003",
        "code": "00W28",
        "source_dir": "source_folder/WGS_CSBD/TS_05_Revenue_SubEdit3_WGS_CSBD_RULEREVE000003_00W28_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_05_Revenue_SubEdit3_WGS_RULEREVE000003_00W28/regression",
        "postman_collection_name": "TS_05_Revenue_SubEdit3_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULEREVE000003_00w28.json"
    },
    {
        "ts_number": "06",
        "edit_id": "RULEREVE000002",
        "code": "00W28",
        "source_dir": "source_folder/WGS_CSBD/TS_06_Revenue_SubEdit2_WGS_CSBD_RULEREVE000002_00W28_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_06_Revenue_SubEdit2_WGS_RULEREVE000002_00W28/regression",
        "postman_collection_name": "TS_06_Revenue_SubEdit2_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULEREVE000002_00w28.json"
    },
    {
        "ts_number": "07",
        "edit_id": "RULEREVE000001",
        "code": "00W28",
        "source_dir": "source_folder/WGS_CSBD/TS_07_Revenue_SubEdit1_WGS_CSBD_RULEREVE000001_00W28_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_07_Revenue_SubEdit1_WGS_RULEREVE000001_00W28/regression",
        "postman_collection_name": "TS_07_Revenue_SubEdit1_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULEREVE000001_00w28.json"
    },
    {
        "ts_number": "08",
        "edit_id": "RULELAB0000009",
        "code": "00W13",
        "source_dir": "source_folder/WGS_CSBD/TS_08_LabPanel_WGS_CSBD_RULELAB0000009_00W13_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_08_LabPanel_WGS_RULELAB0000009_00W13/regression",
        "postman_collection_name": "TS_08_LabPanel_Collection",
        "postman_file_name": "lab_wgs_csbd_RULELAB0000009_00w13.json"
    },
    {
        "ts_number": "09",
        "edit_id": "RULEDEVI000003",
        "code": "00W13",
        "source_dir": "source_folder/WGS_CSBD/TS_09_DeviceDependent_WGS_CSBD_RULEDEVI000003_00W13_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_09_DeviceDependent_WGS_RULEDEVI000003_00W13/regression",
        "postman_collection_name": "TS_09_DeviceDependent_Collection",
        "postman_file_name": "device_wgs_csbd_RULEDEVI000003_00w13.json"
    },
    {
        "ts_number": "10",
        "edit_id": "RULERECO000001",
        "code": "00W34",
        "source_dir": "source_folder/WGS_CSBD/TS_10_RecoveryRoom_WGS_CSBD_RULERECO000001_00W34_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_10_RecoveryRoom_WGS_RULERECO000001_00W34/regression",
        "postman_collection_name": "TS_10_RecoveryRoom_Collection",
        "postman_file_name": "recovery_wgs_csbd_RULERECO000001_00w34.json"
    },
    {
        "ts_number": "11",
        "edit_id": "RULERECO000003",
        "code": "00W26",
        "source_dir": "source_folder/WGS_CSBD/TS_11_RevenueHCPCS_WGS_CSBD_RULERECO000003_00W26_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_11_RevenueHCPCS_WGS_RULERECO000003_00W26/regression",
        "postman_collection_name": "TS_11_RevenueHCPCS_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULERECO000003_00w26.json"
    },
    {
        "ts_number": "12",
        "edit_id": "RULEINCI000001",
        "code": "00W34",
        "source_dir": "source_folder/WGS_CSBD/TS_12_Incidental_WGS_CSBD_RULEINCI000001_00W34_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_12_Incidental_WGS_RULEINCI000001_00W34/regression",
        "postman_collection_name": "TS_12_Incidental_Collection",
        "postman_file_name": "incidentcal_wgs_csbd_RULEINCI000001_00w34.json"
    },
    {
        "ts_number": "13",
        "edit_id": "RULERCE0000006",
        "code": "00W06",
        "source_dir": "source_folder/WGS_CSBD/TS_13_RevenueModel_v3_WGS_CSBD_RULERCE0000006_00W06_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_13_RevenueModel_v3_WGS_RULERCE0000006_00W06/regression",
        "postman_collection_name": "TS_13_RevenueModel_v3_Collection",
        "postman_file_name": "revenue_model_wgs_csbd_RULERCE0000006_00w06.json"
    },
    {
        "ts_number": "14",
        "edit_id": "RULERCE000001",
        "code": "00W26",
        "source_dir": "source_folder/WGS_CSBD/TS_14_HCPCSRevenue_WGS_CSBD_RULERCE000001_00W26_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_14_HCPCSRevenue_WGS_RULERCE000001_00W26/regression",
        "postman_collection_name": "TS_14_HCPCSRevenue_Collection",
        "postman_file_name": "hcpcs_wgs_csbd_RULERCE000001_00w26.json"
    },
    {
        "ts_number": "15",
        "edit_id": "RULERCE000005",
        "code": "00W06",
        "source_dir": "source_folder/WGS_CSBD/TS_15_RevenueModel_WGS_CSBD_RULERCE000005_00W06_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_15_RevenueModel_WGS_RULERCE000005_00W06/regression",
        "postman_collection_name": "TS_15_RevenueModel_Collection",
        "postman_file_name": "revenue_wgs_csbd_RULERCE000005_00w06.json"
    },
    {
        "ts_number": "46",
        "edit_id": "RULEEM000046",
        "code": "00W46",
        "source_dir": "source_folder/WGS_CSBD/TS_46_MultipleEM_WGS_CSBD_RULEEM000046_00W46_sur/regression",
        "dest_dir": "renaming_jsons/WGS_CSBD/TS_46_MultipleEM_WGS_RULEEM000046_00W46/regression",
        "postman_collection_name": "TS_46_MultipleEM_Collection",
        "postman_file_name": "multiple_em_wgs_csbd_RULEEM000046_00w46.json"
    }
    ],
    "gbdf": [
        {
            "ts_number": "01",
            "edit_id": "RULEEM000001",
            "code": "v04",
            "source_dir": "source_folder/GBDF/TS_47_Covid_gbdf_mcr_RULEEM000001_v04_sur/regression",
            "dest_dir": "renaming_jsons/GBDF/TS_47_Covid_gbdf_mcr_RULEEM000001_v04_dis/regression",
            "postman_collection_name": "TS_47_Covid_gbdf_mcr_Collection",
            "postman_file_name": "covid_gbdf_mcr_RULEEM000001_v04.json"
        }
    ]
}

# Dynamic model discovery
def get_models_config(use_dynamic=True, use_wgs_csbd_destination=False, use_gbdf_mcr=False):
    """
    Get model configurations using dynamic discovery or static config.
    
    Args:
        use_dynamic: If True, use dynamic discovery; if False, use static config
        use_wgs_csbd_destination: If True, use WGS_CSBD as destination folder instead of renaming_jsons
        use_gbdf_mcr: If True, use GBDF MCR models instead of WGS_CSBD
        
    Returns:
        List of model configurations
    """
    if use_dynamic:
        try:
            if use_gbdf_mcr:
                # Use dynamic discovery for GBDF MCR
                discovered_models = discover_ts_folders("source_folder/GBDF", False)
                if discovered_models:
                    print(f"Dynamic discovery found {len(discovered_models)} GBDF MCR models")
                    return discovered_models
                else:
                    print("No GBDF MCR models found via dynamic discovery, falling back to static config")
                    return STATIC_MODELS_CONFIG.get("gbdf", [])
            else:
                # Use dynamic discovery for WGS_CSBD
                discovered_models = discover_ts_folders("source_folder/WGS_CSBD", use_wgs_csbd_destination)
                if discovered_models:
                    print(f"Dynamic discovery found {len(discovered_models)} WGS_CSBD models")
                    return discovered_models
                else:
                    print("No WGS_CSBD models found via dynamic discovery, falling back to static config")
                    return STATIC_MODELS_CONFIG.get("wgs_csbd", [])
        except Exception as e:
            print(f"Dynamic discovery failed: {e}, falling back to static config")
            if use_gbdf_mcr:
                return STATIC_MODELS_CONFIG.get("gbdf", [])
            else:
                return STATIC_MODELS_CONFIG.get("wgs_csbd", [])
    else:
        if use_gbdf_mcr:
            return STATIC_MODELS_CONFIG.get("gbdf", [])
        else:
            return STATIC_MODELS_CONFIG.get("wgs_csbd", [])

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

# For backward compatibility, keep MODELS_CONFIG as a property
MODELS_CONFIG = get_models_config(use_dynamic=True)

# Global settings
GENERATE_POSTMAN_COLLECTIONS = True
VERBOSE_OUTPUT = True
