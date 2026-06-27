---
name: model-configuration
description: Add and configure new healthcare models in the test-case automation system
---

# Model Configuration Skill

## Purpose
Guide the process of adding new healthcare models to the automation system, including configuration setup, testing, and deployment.
### 1. model_1 Models
**Command Format:** `--model_1 --TS[XX]`
- Adding new model_1 models
- Updating existing model configurations
- Troubleshooting model discovery issues
## Model Categories and Formats

### 1. model_1 Models

# Test the new model
python main_processor.py --model_1 --[MODEL_ID]


# Single model
python main_processor.py --model_1 --TS01
python main_processor.py --model_1 --TS49
├── payloads/
│   ├── regression/
│   └── smoke/
└── (other model-specific files)
```

**Important:** Folders must end with `_sur` for source, `_dis` for destination.
# All models of a type
python main_processor.py --model_1 --all
#### Option B: Static Configuration
Add to `models_config.py` in `STATIC_MODELS_CONFIG`:
```python
'NEW_MODEL': {
    'category': 'model_1',  # or other category
    'ts_number': 'TS01',
    'display_name': 'New Model Display Name',
    'description': 'Model description',
    'special_features': [],  # e.g., ['header_footer_transform']
}
```

### Step 3: Test the Configuration
```bash
# List all models to verify discovery
python main_processor.py --list

# Test the new model
python main_processor.py --[category] --[MODEL_ID]
```

## Model-Specific Configurations

### model_1 Special Handling
```python
# In rename_files.py or model-specific handler
def apply_model_1_transformations(data):
    # Add KEY_CHK_DCN_NBR
    # Apply header/footer transformations
    # Handle special naming conventions
```

### RefDB Integration
For models supporting RefDB:
```python
# Add to model configuration
'REFDB_ENABLED': True,
'REFDB_CONFIG': {
    'endpoint': 'specific_endpoint',
    'auth_method': 'method'
}
```

## Testing New Models

### 1. Unit Testing
```bash
# Test model discovery
python -c "from dynamic_models import discover_models; print(discover_models())"

# Test configuration loading
python -c "from models_config import get_model_config; print(get_model_config('NEW_MODEL'))"
```

### 2. Integration Testing
```bash
# Test with sample data
python main_processor.py --[category] --[MODEL_ID] --dry-run

# Full processing test
python main_processor.py --[category] --[MODEL_ID]
```

### 3. Validation Checks
- Verify source files are discovered
- Check output files are generated correctly
- Validate Postman collection creation
- Review processing reports

## Troubleshooting Model Issues

### Issue: Model Not Discovered
**Checks:**
- Directory structure is correct
- Naming convention matches pattern
- Permissions on source directories
- Dynamic discovery is working

### Issue: Processing Fails
**Investigate:**
- Model configuration syntax
- Source file format validation
- Category-specific requirements
- Special feature implementations

### Issue: Wrong Command Format
**Verify:**
- Correct prefix usage (NYKTS vs TS)
- Proper category flag
- Model ID format matches expectations

## Configuration Files

### `models_config.py`
- Static model definitions
- Category configurations
- Global settings

### `dynamic_models.py`
- Auto-discovery logic
- Directory scanning
- Pattern matching

### `refdb_values.json`
- RefDB configuration values
- Model-specific settings
- Endpoint definitions

## Best Practices

### 1. Naming Conventions
- Use consistent TS numbering
- Follow category-specific prefixes
- Maintain descriptive display names

### 2. Documentation
- Document model purposes
- Include setup instructions
- Provide usage examples

### 3. Testing
- Test with sample data before deployment
- Validate all processing steps
- Check edge cases and error handling

### 4. Version Control
- Track configuration changes
- Document model additions
- Maintain change logs

## Advanced Configuration

### Custom Processing Logic
```python
# Add to rename_files.py or create model-specific module
def process_custom_model(model_config, source_files):
    # Custom processing logic
    pass
```

### Environment-Specific Settings
```python
# In .env or config files
CUSTOM_MODEL_ENABLED=true
CUSTOM_MODEL_ENDPOINT=https://api.example.com
```

## Commands for Model Management

```bash
# Discover all models
python main_processor.py --list

# Test specific model
python main_processor.py --model_1 --TS01

# Batch process all models
python main_processor.py --all

# Process with RefDB
python main_processor.py --model_1 --TS46 --refdb

# Generate reports only
python main_processor.py --model_1 --TS01 --reports-only
```
