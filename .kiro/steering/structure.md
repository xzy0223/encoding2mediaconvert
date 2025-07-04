# Project Structure

## Root Directory Layout
```
e2mc_assistant/
├── src/e2mc_assistant/          # Main package source code
├── utils/                       # Utility modules and tools
├── setup.py                     # Package configuration
├── MANIFEST.in                  # Package manifest
└── README.md                    # Project documentation
```

## Core Package Structure (`src/e2mc_assistant/`)

### Main Components
- **`converter/`** - Configuration conversion engine
  - `config_converter_enhanced.py` - Main converter implementation
  - `rules/e2mc_rules.yaml` - Transformation mapping rules
  - `templates/` - MediaConvert job templates (MP4, HLS, etc.)
  - `README.md` - Converter-specific documentation

- **`analyzer/`** - Video analysis and comparison
  - `video_analyzer.py` - Video analysis using AWS Bedrock
  - `README.md` - Analyzer documentation

- **`requester/`** - AWS MediaConvert job management
  - `mediaconvert_job_submitter.py` - Job submission and tracking
  - `README.md` - Job submission documentation

- **`workflow/`** - End-to-end workflow orchestration
  - `e2mc_workflow.py` - Complete conversion and analysis pipeline

## Utilities (`utils/`)
- **`mc_config_validator/`** - Configuration validation tools
  - `validator.py` - JSON schema validation
  - `mc_setting_schema.json` - MediaConvert configuration schema
  - `mc_template.json` - Base template for validation

## File Naming Conventions
- **Configuration files**: `{id}.xml` (input), `{id}.json` (output)
- **Log files**: `{id}_conversion.log`, `{id}_job_submission.log`
- **Error files**: `{id}.err`, `{id}_job_execution.err`
- **Templates**: `{format}_template.json` (e.g., `mp4_template.json`)
- **Rules**: `{purpose}_rules.yaml` (e.g., `e2mc_rules.yaml`)

## Module Organization Patterns
- Each major component has its own subdirectory with `__init__.py`
- README files provide component-specific documentation
- Templates and configuration files are co-located with their processors
- Validation utilities are separated into dedicated utility modules

## Import Conventions
- Use relative imports within package components
- Absolute imports for cross-component dependencies
- Utility modules imported via sys.path manipulation when needed
- AWS SDK clients initialized per-component as needed