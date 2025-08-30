#!/usr/bin/env python3
"""
Fix Jupyter Notebook Widget Metadata

This utility helps fix invalid Jupyter notebook metadata that causes rendering errors,
specifically missing "state" keys inside metadata.widgets entries.

Usage:
    python fix_notebook_metadata.py [notebook_files...]
    python fix_notebook_metadata.py --help
    python fix_notebook_metadata.py --check notebook.ipynb
    python fix_notebook_metadata.py --fix notebook.ipynb
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Tuple, Any, Optional


def check_notebook_widgets(notebook_path: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Check a notebook for widget metadata issues.
    
    Args:
        notebook_path: Path to the notebook file
        
    Returns:
        Tuple of (has_issues, issue_details)
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        return True, {'error': f'Failed to read notebook: {e}'}
    
    metadata = nb.get('metadata', {})
    widgets = metadata.get('widgets', {})
    
    if not widgets:
        return False, {'message': 'No widget metadata found'}
    
    widget_state = widgets.get('application/vnd.jupyter.widget-state+json', {})
    
    if not widget_state:
        return True, {'issue': 'Missing application/vnd.jupyter.widget-state+json key'}
    
    missing_state_widgets = []
    total_widgets = len(widget_state)
    
    for widget_id, widget_data in widget_state.items():
        if not isinstance(widget_data, dict):
            missing_state_widgets.append(widget_id)
            continue
            
        if 'state' not in widget_data:
            missing_state_widgets.append(widget_id)
    
    has_issues = len(missing_state_widgets) > 0
    
    details = {
        'total_widgets': total_widgets,
        'missing_state_count': len(missing_state_widgets),
        'missing_state_widgets': missing_state_widgets
    }
    
    if has_issues:
        details['issue'] = f'{len(missing_state_widgets)} widgets missing "state" key'
    else:
        details['message'] = 'All widgets have required "state" keys'
    
    return has_issues, details


def fix_notebook_widgets(notebook_path: str, backup: bool = True) -> bool:
    """
    Fix widget metadata issues in a notebook.
    
    Args:
        notebook_path: Path to the notebook file
        backup: Whether to create a backup before fixing
        
    Returns:
        True if fixes were made, False otherwise
    """
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"Error reading {notebook_path}: {e}")
        return False
    
    metadata = nb.get('metadata', {})
    widgets = metadata.get('widgets', {})
    
    if not widgets:
        print(f"No widget metadata found in {notebook_path}")
        return False
    
    widget_state = widgets.get('application/vnd.jupyter.widget-state+json', {})
    
    if not widget_state:
        print(f"No widget state data found in {notebook_path}")
        return False
    
    fixed_count = 0
    
    for widget_id, widget_data in widget_state.items():
        if not isinstance(widget_data, dict):
            continue
            
        if 'state' not in widget_data:
            # Add a minimal state object with commonly required fields
            widget_data['state'] = {
                '_model_module': widget_data.get('model_module', ''),
                '_model_module_version': widget_data.get('model_module_version', ''),
                '_model_name': widget_data.get('model_name', ''),
                '_view_count': None,
                '_view_module': widget_data.get('model_module', '').replace('controls', 'base') if 'controls' in widget_data.get('model_module', '') else widget_data.get('model_module', ''),
                '_view_module_version': widget_data.get('model_module_version', ''),
                '_view_name': widget_data.get('model_name', '').replace('Model', 'View') if widget_data.get('model_name', '').endswith('Model') else widget_data.get('model_name', '') + 'View'
            }
            fixed_count += 1
            print(f"  Fixed widget {widget_id}")
    
    if fixed_count == 0:
        print(f"No fixes needed for {notebook_path}")
        return False
    
    # Create backup if requested
    if backup:
        backup_path = notebook_path + '.bak'
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(nb, f, indent=2)
            print(f"  Created backup: {backup_path}")
        except Exception as e:
            print(f"  Warning: Failed to create backup: {e}")
    
    # Write the fixed notebook
    try:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=2)
        print(f"  Fixed {fixed_count} widgets in {notebook_path}")
        return True
    except Exception as e:
        print(f"Error writing fixed notebook {notebook_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Fix invalid Jupyter notebook widget metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Check a notebook for issues:
    python fix_notebook_metadata.py --check notebook.ipynb
  
  Fix issues in a notebook:
    python fix_notebook_metadata.py --fix notebook.ipynb
  
  Fix multiple notebooks:
    python fix_notebook_metadata.py --fix *.ipynb
  
  Fix without creating backups:
    python fix_notebook_metadata.py --fix --no-backup notebook.ipynb
        """
    )
    
    parser.add_argument('files', nargs='*', help='Notebook files to process')
    parser.add_argument('--check', action='store_true', 
                       help='Check for issues without fixing')
    parser.add_argument('--fix', action='store_true',
                       help='Fix issues in the notebooks')
    parser.add_argument('--no-backup', action='store_true',
                       help="Don't create backup files when fixing")
    
    args = parser.parse_args()
    
    if not args.files:
        parser.print_help()
        return 1
    
    if not args.check and not args.fix:
        print("Please specify either --check or --fix")
        return 1
    
    if args.check and args.fix:
        print("Please specify either --check OR --fix, not both")
        return 1
    
    total_files = 0
    files_with_issues = 0
    files_fixed = 0
    
    for file_pattern in args.files:
        if '*' in file_pattern:
            import glob
            files = glob.glob(file_pattern)
        else:
            files = [file_pattern]
        
        for notebook_path in files:
            if not os.path.exists(notebook_path):
                print(f"Warning: File not found: {notebook_path}")
                continue
                
            if not notebook_path.endswith('.ipynb'):
                print(f"Warning: Skipping non-notebook file: {notebook_path}")
                continue
            
            total_files += 1
            print(f"\nProcessing: {notebook_path}")
            
            has_issues, details = check_notebook_widgets(notebook_path)
            
            if 'error' in details:
                print(f"  Error: {details['error']}")
                continue
            
            if has_issues:
                files_with_issues += 1
                print(f"  Issues found: {details.get('issue', 'Unknown issue')}")
                if 'missing_state_widgets' in details:
                    print(f"  Affected widgets: {', '.join(details['missing_state_widgets'])}")
                
                if args.fix:
                    if fix_notebook_widgets(notebook_path, backup=not args.no_backup):
                        files_fixed += 1
            else:
                print(f"  ✓ {details.get('message', 'No issues found')}")
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    
    if args.fix:
        print(f"Files fixed: {files_fixed}")
    
    return 0 if files_with_issues == 0 else 1


if __name__ == '__main__':
    sys.exit(main())