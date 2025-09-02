# Fix Notebook Metadata Utility

This utility helps fix invalid Jupyter notebook metadata that causes rendering errors, specifically missing "state" keys inside `metadata.widgets` entries.

## Problem

Some Jupyter notebooks may have widget metadata where individual widget entries are missing the required "state" key. This can cause rendering errors when the notebook is opened in environments that expect complete widget metadata.

The problematic structure looks like this:

```json
{
  "metadata": {
    "widgets": {
      "application/vnd.jupyter.widget-state+json": {
        "widget_id": {
          "model_module": "@jupyter-widgets/controls",
          "model_name": "HBoxModel",
          "model_module_version": "1.5.0"
          // Missing "state" key!
        }
      }
    }
  }
}
```

The correct structure should include a "state" key with widget state data:

```json
{
  "metadata": {
    "widgets": {
      "application/vnd.jupyter.widget-state+json": {
        "widget_id": {
          "model_module": "@jupyter-widgets/controls",
          "model_name": "HBoxModel", 
          "model_module_version": "1.5.0",
          "state": {
            "_model_module": "@jupyter-widgets/controls",
            "_model_module_version": "1.5.0",
            "_model_name": "HBoxModel",
            "_view_count": null,
            // ... other state properties
          }
        }
      }
    }
  }
}
```

## Usage

### Check for Issues

To check a notebook for widget metadata issues without making changes:

```bash
python fix_notebook_metadata.py --check notebook.ipynb
```

### Fix Issues

To fix issues in a notebook (creates a backup by default):

```bash
python fix_notebook_metadata.py --fix notebook.ipynb
```

### Fix Multiple Notebooks

To fix issues in multiple notebooks:

```bash
python fix_notebook_metadata.py --fix *.ipynb
```

### Fix Without Backup

To fix issues without creating backup files:

```bash
python fix_notebook_metadata.py --fix --no-backup notebook.ipynb
```

### Help

To see all available options:

```bash
python fix_notebook_metadata.py --help
```

## What the Script Does

1. **Detection**: Scans notebook files for widget metadata and identifies widgets missing the "state" key
2. **Fixing**: Adds minimal but valid "state" objects to widgets that are missing them
3. **Backup**: Creates backup files (`.ipynb.bak`) before making changes (unless `--no-backup` is used)
4. **Reporting**: Provides detailed output about what was found and fixed

## Requirements

- Python 3.6 or higher
- No additional dependencies required (uses only standard library)

## Exit Codes

- `0`: Success (no issues found or all issues fixed successfully)
- `1`: Issues found (in check mode) or errors occurred

## Example Output

```
$ python fix_notebook_metadata.py --check problematic_notebook.ipynb

Processing: problematic_notebook.ipynb
  Issues found: 2 widgets missing "state" key
  Affected widgets: broken_widget_1, broken_widget_2

=== Summary ===
Files processed: 1
Files with issues: 1
```

```
$ python fix_notebook_metadata.py --fix problematic_notebook.ipynb

Processing: problematic_notebook.ipynb
  Issues found: 2 widgets missing "state" key
  Affected widgets: broken_widget_1, broken_widget_2
  Fixed widget broken_widget_1
  Fixed widget broken_widget_2
  Created backup: problematic_notebook.ipynb.bak
  Fixed 2 widgets in problematic_notebook.ipynb

=== Summary ===
Files processed: 1
Files with issues: 1
Files fixed: 1
```