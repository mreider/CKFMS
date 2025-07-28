# CKFMS
Categories Keys Facets Metadata Semantics

## File Structure

### Input Files
- `MetadataConsistencyWorksheet.csv` - Raw data showing current inconsistent structure across Dynatrace apps
- `resource_fields/` - Semantic dictionary for resource metadata
- `signal_fields/` - Semantic dictionary for signal/span data

### Generated Structure Files
- `current_metadata_structure.yaml` - Current inconsistent metadata categories (from CSV)
- `current_facets_structure.yaml` - Current inconsistent facet categories (from CSV)
- `suggested_metadata_structure.yaml` - Standardized categories with current field names
- `suggested_facets_structure.yaml` - Standardized categories with current field names
- `normalized_metadata_structure.yaml` - Final structure with semantic dictionary keys
- `normalized_facets_structure.yaml` - Final structure with semantic dictionary keys

### Report Generation
- `generate_html_report.py` - Creates HTML report with three tables:
  1. **Suggested Categories** - Universal semantic categories (excludes app-specific Core)
  2. **Current Structure** (⚠️) - Shows existing inconsistent state
  3. **New Structure** (✨) - Final semantic structure with migration mapping

### Output
- `dynatrace_structure_analysis.html` - Complete analysis showing transformation from current mess to clean semantic structure

## Key Principles
- **Core categories**: App-specific, contain most important fields for each app
- **Tags & Labels**: Consolidated location for all tags/labels/annotations
- **Category ordering**: Core → Tags & Labels → Alphabetical
- **Cloud semantics**: Only `cloud.provider` + provider-specific keys (aws.*, azure.*, gcp.*)
- **Migration mapping**: Shows "(was: old_name)" only when field names actually change
