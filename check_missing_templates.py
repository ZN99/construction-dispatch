#!/usr/bin/env python3
"""
Script to find all missing templates referenced in Django views
"""
import os
import re
import json
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent

def find_template_references():
    """Find all template references in Python view files"""
    template_refs = []

    # Patterns to find template references
    template_name_pattern = r"template_name\s*=\s*['\"]([^'\"]+)['\"]"
    render_pattern = r"render\([^,]+,\s*['\"]([^'\"]+)['\"]"
    get_template_pattern = r"get_template\(['\"]([^'\"]+)['\"]"

    # Find all Python files in the project (excluding venv)
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if "venv" in str(py_file) or "migrations" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find template_name assignments
            matches = re.findall(template_name_pattern, content)
            for match in matches:
                template_refs.append({
                    'template': match,
                    'file': str(py_file),
                    'type': 'template_name'
                })

            # Find render() calls
            matches = re.findall(render_pattern, content)
            for match in matches:
                template_refs.append({
                    'template': match,
                    'file': str(py_file),
                    'type': 'render'
                })

            # Find get_template() calls
            matches = re.findall(get_template_pattern, content)
            for match in matches:
                template_refs.append({
                    'template': match,
                    'file': str(py_file),
                    'type': 'get_template'
                })

        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    return template_refs

def find_existing_templates():
    """Find all existing template files"""
    templates = []

    # Find all template directories
    for template_dir in PROJECT_ROOT.rglob("templates"):
        if "venv" in str(template_dir):
            continue

        for html_file in template_dir.rglob("*.html"):
            # Get relative path from template directory
            rel_path = html_file.relative_to(template_dir)
            templates.append(str(rel_path))

    return templates

def main():
    print("Django Template Missing Analysis")
    print("=" * 50)

    # Find all template references
    template_refs = find_template_references()
    print(f"Found {len(template_refs)} template references")

    # Find all existing templates
    existing_templates = find_existing_templates()
    print(f"Found {len(existing_templates)} existing templates")

    # Find missing templates
    referenced_templates = set(ref['template'] for ref in template_refs)
    missing_templates = referenced_templates - set(existing_templates)

    print(f"\nMISSING TEMPLATES ({len(missing_templates)}):")
    print("-" * 30)

    missing_list = []
    for template in sorted(missing_templates):
        # Find which files reference this template
        referencing_files = [ref['file'] for ref in template_refs if ref['template'] == template]

        print(f"\n❌ {template}")
        for ref_file in set(referencing_files):
            print(f"   Referenced in: {ref_file}")

        missing_list.append({
            'template': template,
            'referenced_in': list(set(referencing_files))
        })

    # Check for schedule-related templates specifically
    print(f"\nSCHEDULE-RELATED MISSING TEMPLATES:")
    print("-" * 40)

    schedule_related = []
    for template in missing_templates:
        if any(keyword in template.lower() for keyword in ['schedule', 'calendar', 'appointment', 'booking']):
            schedule_related.append(template)
            print(f"📅 {template}")

    # Summary by app
    print(f"\nMISSING TEMPLATES BY APP:")
    print("-" * 30)

    by_app = {}
    for template in missing_templates:
        app = template.split('/')[0] if '/' in template else 'root'
        if app not in by_app:
            by_app[app] = []
        by_app[app].append(template)

    for app, templates in sorted(by_app.items()):
        print(f"\n{app.upper()} ({len(templates)} missing):")
        for template in sorted(templates):
            print(f"  - {template}")

    # Write detailed report to JSON
    report = {
        'total_references': len(template_refs),
        'total_existing': len(existing_templates),
        'total_missing': len(missing_templates),
        'missing_templates': missing_list,
        'schedule_related_missing': schedule_related,
        'by_app': by_app,
        'existing_templates': sorted(existing_templates),
        'all_references': template_refs
    }

    with open('missing_templates_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 SUMMARY:")
    print(f"Total template references: {len(template_refs)}")
    print(f"Existing templates: {len(existing_templates)}")
    print(f"Missing templates: {len(missing_templates)}")
    print(f"Schedule-related missing: {len(schedule_related)}")
    print(f"\nDetailed report saved to: missing_templates_report.json")

if __name__ == "__main__":
    main()