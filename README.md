# Model Configuration

## Static Models Configuration

```python
STATIC_MODELS_CONFIG = {
    "model_1": [
        {
            "ts_number": "01",
            "id": "01",
            "code": "00",
            "source_dir": "source_folder/Model/Model_01_sample_model_1_M000001_00W04_sur/payloads",
            "dest_dir": "renaming_jsons/Model/Model_01_sample_model_1_M000001_00W04_dis/payload",
            "postman_collection_name": "TS_01_sample_Collection",
            "postman_file_name": "sample_model_1_M000001_00W04.json"
        }
    ]
}
```

## Key Functions

### Dynamic Discovery
- `get_models_config(use_dynamic=True, use_model_1_destination=False)` - Get model configurations using dynamic discovery or static config
- `get_model_by_ts(ts_number)` - Get a specific model by TS number using dynamic discovery
- `discover_ts_folders()` - Automatically discover TS folders from source directory

### Configuration Management
- `_expand_config_list_with_smoke(config_list)` - Expand config to include smoke payloads when they exist
- `_merge_static_models(discovered_models, static_key)` - Merge static config entries into discovered list

### Header/Footer Transformation
- `apply_header_footer_to_json(file_path, is_model_4=False)` - Apply header and footer structure to JSON files
- `apply_header_footer_to_renaming_jsons()` - Apply header/footer to all JSON files in renaming_jsons folder

## Global Settings

```python
GENERATE_POSTMAN_COLLECTIONS = True
VERBOSE_OUTPUT = True
```

## Model Types

- **model_1** - WGS_CSBD healthcare claims processing
- **model_2** - GBDF MCR medical claims research
- **model_3** - GBDF GRS global research services
- **model_4** - WGS_NYK observation services