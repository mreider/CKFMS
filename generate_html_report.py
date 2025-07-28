#!/usr/bin/env python3
"""
Script to parse YAML metadata and facet structure files and generate an HTML report
showing current, suggested, and normalized structures across Dynatrace applications.
"""

import yaml
import os
from typing import Dict, Any, List

def load_yaml_file(filename: str) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing {filename}: {e}")
        return {}

def format_fields_as_bullets(fields: List[str], indent_level: int = 0) -> str:
    """Format a list of fields as HTML bullet points."""
    if not fields:
        return "<li>No fields</li>"
    
    indent = "&nbsp;" * (indent_level * 4)
    bullets = []
    for field in fields:
        bullets.append(f"{indent}<li>{field}</li>")
    return "\n".join(bullets)

def format_category_structure(categories: Dict[str, Any], data_type: str) -> str:
    """Format category structure as nested HTML bullets."""
    if not categories:
        return "<ul><li>No categories</li></ul>"
    
    html_parts = ["<ul>"]
    
    for category_key, category_data in categories.items():
        if isinstance(category_data, dict):
            display_name = category_data.get('display_name', category_key)
            html_parts.append(f"<li><strong>{display_name}</strong>")
            
            # Handle different structures based on data type
            if data_type == "metadata":
                fields = category_data.get('fields', [])
                if fields:
                    html_parts.append("<ul>")
                    html_parts.append(format_fields_as_bullets(fields))
                    html_parts.append("</ul>")
            elif data_type == "facets":
                facets = category_data.get('facets', [])
                if facets:
                    html_parts.append("<ul>")
                    
                    if isinstance(facets, list):
                        # Handle pure list format
                        html_parts.append(format_fields_as_bullets(facets))
                    elif isinstance(facets, dict):
                        # Handle mixed dictionary format (can contain both simple items and complex objects)
                        for facet_key, facet_data in facets.items():
                            if isinstance(facet_data, dict):
                                # Complex facet with display_name and values
                                facet_display = facet_data.get('display_name', facet_key)
                                html_parts.append(f"<li>{facet_display}")
                                values = facet_data.get('values', [])
                                if values:
                                    html_parts.append("<ul>")
                                    html_parts.append(format_fields_as_bullets(values))
                                    html_parts.append("</ul>")
                                html_parts.append("</li>")
                            else:
                                # Simple facet (just a string)
                                html_parts.append(f"<li>{facet_key}</li>")
                    else:
                        # Handle case where facets might be a mixed structure
                        # This handles the case where YAML parsing creates a mixed structure
                        html_parts.append(f"<li>Mixed structure: {facets}</li>")
                    
                    html_parts.append("</ul>")
            
            html_parts.append("</li>")
        else:
            # Handle simple list format at category level
            html_parts.append(f"<li>{category_key}")
            if isinstance(category_data, list):
                html_parts.append("<ul>")
                html_parts.append(format_fields_as_bullets(category_data))
                html_parts.append("</ul>")
            html_parts.append("</li>")
    
    html_parts.append("</ul>")
    return "\n".join(html_parts)

def format_normalized_structure(categories: Dict[str, Any], data_type: str) -> str:
    """Format normalized structure showing semantic keys and display names."""
    if not categories:
        return "<ul><li>No categories</li></ul>"
    
    html_parts = ["<ul>"]
    
    for category_key, category_data in categories.items():
        if isinstance(category_data, dict):
            display_name = category_data.get('display_name', category_key)
            html_parts.append(f"<li><strong>{display_name}</strong>")
            
            if data_type == "metadata":
                fields = category_data.get('fields', [])
                if fields:
                    html_parts.append("<ul>")
                    for field in fields:
                        if isinstance(field, dict):
                            semantic_key = field.get('semantic_key', '')
                            display_name_field = field.get('display_name', '')
                            current_key = field.get('current_key', '')
                            html_parts.append(f"<li><code>{semantic_key}</code> - {display_name_field}")
                            # Only show migration mapping if the current key is different from display name
                            if current_key and current_key != display_name_field:
                                html_parts.append(f" <em>(was: {current_key})</em>")
                            html_parts.append("</li>")
                        else:
                            html_parts.append(f"<li>{field}</li>")
                    html_parts.append("</ul>")
            elif data_type == "facets":
                facets = category_data.get('facets', [])
                if facets:
                    html_parts.append("<ul>")
                    for facet in facets:
                        if isinstance(facet, dict):
                            semantic_key = facet.get('semantic_key', '')
                            display_name_facet = facet.get('display_name', '')
                            current_key = facet.get('current_key', '')
                            html_parts.append(f"<li><code>{semantic_key}</code> - {display_name_facet}")
                            # Only show migration mapping if the current key is different from display name
                            if current_key and current_key != display_name_facet:
                                html_parts.append(f" <em>(was: {current_key})</em>")
                            
                            values = facet.get('values', [])
                            if values:
                                html_parts.append("<ul>")
                                html_parts.append(format_fields_as_bullets(values))
                                html_parts.append("</ul>")
                            html_parts.append("</li>")
                        else:
                            html_parts.append(f"<li>{facet}</li>")
                    html_parts.append("</ul>")
            
            html_parts.append("</li>")
    
    html_parts.append("</ul>")
    return "\n".join(html_parts)

def generate_table_row(apps: List[str], data: Dict[str, Any], data_type: str, is_normalized: bool = False) -> str:
    """Generate a table row for metadata or facets."""
    row_html = f"<tr><td><strong>{data_type.title()}</strong></td>"
    
    for app in apps:
        app_key = app.lower().replace(' ', '_').replace('&', 'and')
        app_data = data.get('applications', {}).get(app_key, {})
        categories = app_data.get('categories', {})
        
        if is_normalized:
            content = format_normalized_structure(categories, data_type)
        else:
            content = format_category_structure(categories, data_type)
        
        row_html += f"<td>{content}</td>"
    
    row_html += "</tr>"
    return row_html

def generate_official_categories_table(normalized_metadata: Dict[str, Any], normalized_facets: Dict[str, Any]) -> str:
    """Generate a table showing suggested universal categories and semantic keys (excluding app-specific Core categories)."""
    
    # Collect all unique categories and their semantic keys, excluding "Core" categories
    categories = {}
    
    # Track semantic keys to ensure each appears only once with the best display name
    semantic_key_registry = {}
    
    # Process metadata
    for app_key, app_data in normalized_metadata.get('applications', {}).items():
        for cat_key, cat_data in app_data.get('categories', {}).items():
            if isinstance(cat_data, dict):
                cat_name = cat_data.get('display_name', cat_key)
                # Skip "Core" categories as they are app-specific
                if cat_name.lower() == 'core':
                    continue
                    
                if cat_name not in categories:
                    categories[cat_name] = {
                        'description': cat_data.get('description', ''),
                        'semantic_keys': set()
                    }
                
                # Add semantic keys from metadata
                for field in cat_data.get('fields', []):
                    if isinstance(field, dict):
                        semantic_key = field.get('semantic_key', '')
                        display_name = field.get('display_name', '')
                        if semantic_key and display_name:
                            # Register the semantic key with its display name
                            if semantic_key not in semantic_key_registry:
                                semantic_key_registry[semantic_key] = display_name
                            # Use the registered display name to ensure consistency
                            canonical_display = semantic_key_registry[semantic_key]
                            categories[cat_name]['semantic_keys'].add(f"{semantic_key} - {canonical_display}")
    
    # Process facets
    for app_key, app_data in normalized_facets.get('applications', {}).items():
        for cat_key, cat_data in app_data.get('categories', {}).items():
            if isinstance(cat_data, dict):
                cat_name = cat_data.get('display_name', cat_key)
                # Skip "Core" categories as they are app-specific
                if cat_name.lower() == 'core':
                    continue
                    
                if cat_name not in categories:
                    categories[cat_name] = {
                        'description': cat_data.get('description', ''),
                        'semantic_keys': set()
                    }
                
                # Add semantic keys from facets
                for facet in cat_data.get('facets', []):
                    if isinstance(facet, dict):
                        semantic_key = facet.get('semantic_key', '')
                        display_name = facet.get('display_name', '')
                        if semantic_key and display_name:
                            # Register the semantic key with its display name
                            if semantic_key not in semantic_key_registry:
                                semantic_key_registry[semantic_key] = display_name
                            # Use the registered display name to ensure consistency
                            canonical_display = semantic_key_registry[semantic_key]
                            categories[cat_name]['semantic_keys'].add(f"{semantic_key} - {canonical_display}")
    
    # Generate HTML table
    html_parts = [
        '<table>',
        '<thead>',
        '<tr><th>Category</th><th>Description</th><th>Semantic Keys and Display Names</th></tr>',
        '</thead>',
        '<tbody>'
    ]
    
    # Sort categories alphabetically
    for cat_name in sorted(categories.keys()):
        cat_info = categories[cat_name]
        description = cat_info['description']
        semantic_keys = sorted(list(cat_info['semantic_keys']))
        
        # Format semantic keys as bullets
        if semantic_keys:
            keys_html = '<ul>' + ''.join([f'<li><strong>{key}</strong></li>' for key in semantic_keys]) + '</ul>'
        else:
            keys_html = '<ul><li>No semantic keys defined</li></ul>'
        
        html_parts.append(f'<tr>')
        html_parts.append(f'<td><strong>{cat_name}</strong></td>')
        html_parts.append(f'<td>{description}</td>')
        html_parts.append(f'<td>{keys_html}</td>')
        html_parts.append(f'</tr>')
    
    html_parts.extend(['</tbody>', '</table>'])
    return '\n'.join(html_parts)

def generate_html_report():
    """Generate the complete HTML report."""
    
    # Load all YAML files
    current_metadata = load_yaml_file('current_metadata_structure.yaml')
    current_facets = load_yaml_file('current_facets_structure.yaml')
    suggested_metadata = load_yaml_file('suggested_metadata_structure.yaml')
    suggested_facets = load_yaml_file('suggested_facets_structure.yaml')
    normalized_metadata = load_yaml_file('normalized_metadata_structure.yaml')
    normalized_facets = load_yaml_file('normalized_facets_structure.yaml')
    
    # Application names
    apps = ['Clouds', 'Database', 'Infra and Operations', 'Kubernetes', 'Logs', 'Services', 'Tracing']
    
    # Generate official categories table
    official_categories_table = generate_official_categories_table(normalized_metadata, normalized_facets)
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Metadata and Facets Structure Analysis</title>
    <style>
        table {{
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            font-weight: bold;
        }}
        ul {{
            margin: 0;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 2px;
        }}
    </style>
</head>
<body>
    <h2>1. Suggested Categories and Semantics</h2>
    <p>These are the categories for facets and metadata with semantic names and display names</p>
    
    {official_categories_table}

    <h2>⚠️ 2. Current Existing Structure</h2>
    <p>Shows the existing inconsistent metadata and facet categories as they currently exist across applications</p>
    
    <table>
        <thead>
            <tr>
                <th>Type</th>
                {' '.join([f'<th>{app}</th>' for app in apps])}
            </tr>
        </thead>
        <tbody>
            {generate_table_row(apps, current_metadata, 'metadata')}
            {generate_table_row(apps, current_facets, 'facets')}
        </tbody>
    </table>

    <h2>✨ 3. New Structure with Semantic Dictionary</h2>
    <p>Improved structure with semantic dictionary keys, English display names, and migration mapping from current field names</p>
    
    <table>
        <thead>
            <tr>
                <th>Type</th>
                {' '.join([f'<th>{app}</th>' for app in apps])}
            </tr>
        </thead>
        <tbody>
            {generate_table_row(apps, normalized_metadata, 'metadata', is_normalized=True)}
            {generate_table_row(apps, normalized_facets, 'facets', is_normalized=True)}
        </tbody>
    </table>

    <p><strong>Legend:</strong></p>
    <ul>
        <li><strong>semantic.key</strong> - Official semantic dictionary field name</li>
        <li><strong>Display Name</strong> - Human-readable English name for UI</li>
        <li><em>(was: current_name)</em> - Original field name for migration mapping</li>
    </ul>
</body>
</html>
"""
    
    # Write HTML file
    output_file = 'dynatrace_structure_analysis.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated successfully: {output_file}")
    return output_file

if __name__ == "__main__":
    generate_html_report()
