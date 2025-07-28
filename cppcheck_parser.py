#!/usr/bin/env python3
"""
Cppcheck XML Parser

Copyright (c) 2025 Jeff Haumont
Version: 0.1.1

This script parses cppcheck XML output and generates three CSV files:
1. All error IDs with counts, sorted by count (descending)
2. All severity levels with counts, sorted alphabetically
3. Only error severity IDs with counts, sorted by count (ascending)

Usage: python3 cppcheck_parser.py <input_xml_file>
"""

import sys

# Check Python version early - requires Python 3.6+ for f-strings and pathlib features
if sys.version_info < (3, 6):
    print("Error: This script requires Python 3.6 or higher.")
    print(f"Current Python version: {sys.version}")
    print("Please upgrade your Python installation.")
    sys.exit(1)

import xml.etree.ElementTree as ET
import csv
import argparse
import fnmatch
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

__version__ = "1.3.0"

def get_version():
    """Return the version string."""
    return __version__


def parse_cppcheck_xml(xml_file: str) -> Tuple[Counter, Counter]:
    """
    Parse cppcheck XML file and return counters for error IDs and severities.
    
    Args:
        xml_file: Path to the cppcheck XML output file
        
    Returns:
        Tuple of (error_id_counter, severity_counter)
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: XML file '{xml_file}' not found")
        sys.exit(1)
    
    error_id_counter = Counter()
    severity_counter = Counter()
    
    # Find all error elements
    errors = root.findall('.//error')
    
    for error in errors:
        error_id = error.get('id')
        severity = error.get('severity')
        
        if error_id:
            error_id_counter[error_id] += 1
        
        if severity:
            severity_counter[severity] += 1
    
    return error_id_counter, severity_counter


def write_csv_all_errors(error_id_counter: Counter, output_file: str):
    """
    Write CSV file with all error IDs and their counts, sorted by count (ascending).
    
    Args:
        error_id_counter: Counter object with error IDs and counts
        output_file: Output CSV file path
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Count', 'Error ID'])
        
        # Sort by count in ascending order (smallest to largest)
        for error_id, count in sorted(error_id_counter.items(), key=lambda x: x[1]):
            writer.writerow([count, error_id])


def write_csv_severities(severity_counter: Counter, output_file: str):
    """
    Write CSV file with all severity levels and their counts, sorted alphabetically.
    
    Args:
        severity_counter: Counter object with severities and counts
        output_file: Output CSV file path
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Count', 'Severity'])
        
        # Sort alphabetically by severity name
        for severity in sorted(severity_counter.keys()):
            count = severity_counter[severity]
            writer.writerow([count, severity])


def write_csv_error_severity_only(error_id_counter: Counter, severity_counter: Counter, output_file: str):
    """
    Write CSV file with only error severity IDs and their counts, sorted by count (ascending).
    
    Args:
        error_id_counter: Counter object with error IDs and counts
        severity_counter: Counter object with severities and counts (for validation)
        output_file: Output CSV file path
    """
    # Filter to only include error IDs that have 'error' severity
    # Since the XML structure doesn't directly link error IDs to severities in the counter,
    # we need to re-parse to get this information
    error_only_ids = Counter()
    
    try:
        tree = ET.parse(sys.argv[1] if len(sys.argv) > 1 else 'input.xml')
        root = tree.getroot()
        
        for error in root.findall('.//error'):
            error_id = error.get('id')
            severity = error.get('severity')
            
            if error_id and severity == 'error':
                error_only_ids[error_id] += 1
                
    except (ET.ParseError, FileNotFoundError):
        print("Warning: Could not re-parse XML for error-only filtering")
        return
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Count', 'Error ID'])
        
        # Sort by count in ascending order
        for error_id, count in sorted(error_only_ids.items(), key=lambda x: x[1]):
            writer.writerow([count, error_id])


def write_html_report(xml_file: str, output_file: str, severities: List[str] = None, 
                     error_ids: List[str] = None, not_error_ids: List[str] = None, 
                     file_pattern: str = None, github_url: str = None):
    """
    Write HTML report with errors grouped by file, sorted and filtered.
    
    Args:
        xml_file: Path to the cppcheck XML output file
        output_file: Output HTML file path
        severities: List of severities to include (None for all)
        error_ids: List of error IDs to include (None for all)
        not_error_ids: List of error IDs to exclude (None for none)
        file_pattern: Wildcard pattern for file names (None for all)
        github_url: GitHub repository URL for file links (None for no links)
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Error parsing XML file: {e}")
        return
    
    # Group errors by file
    file_errors = defaultdict(list)
    
    for error in root.findall('.//error'):
        error_id = error.get('id')
        severity = error.get('severity')
        msg = error.get('msg', '')
        verbose = error.get('verbose', '')
        
        # Apply filters
        if severities and severity not in severities:
            continue
        if error_ids and error_id not in error_ids:
            continue
        if not_error_ids and error_id in not_error_ids:
            continue
        
        # Get file information from locations
        locations = error.findall('.//location')
        if not locations:
            continue
            
        for location in locations:
            file_name = location.get('file', '')
            line = location.get('line', '')
            column = location.get('column', '')
            info = location.get('info', '')
            
            # Apply file pattern filter
            if file_pattern and not fnmatch.fnmatch(file_name, file_pattern):
                continue
            
            file_errors[file_name].append({
                'id': error_id,
                'severity': severity,
                'msg': msg,
                'verbose': verbose,
                'line': line,
                'column': column,
                'info': info
            })
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cppcheck Report - {Path(xml_file).stem}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .file-section {{ margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; }}
        .file-header {{ background-color: #f5f5f5; padding: 10px; font-weight: bold; font-size: 18px; }}
        .error {{ margin: 10px; padding: 10px; border-left: 4px solid #ff4444; background-color: #fff5f5; }}
        .error.error {{ border-left-color: #ff4444; }}
        .error.warning {{ border-left-color: #ffaa00; }}
        .error.style {{ border-left-color: #4444ff; }}
        .error.info {{ border-left-color: #44ff44; }}
        .error-header {{ font-weight: bold; margin-bottom: 5px; }}
        .error-id {{ color: #666; font-size: 12px; }}
        .error-msg {{ margin: 5px 0; }}
        .error-verbose {{ color: #666; font-size: 14px; margin: 5px 0; }}
        .error-location {{ color: #888; font-size: 12px; }}
        .error-info {{ color: #666; font-style: italic; }}
        .summary {{ background-color: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        a {{ color: #0366d6; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .file-header a {{ color: inherit; }}
        .file-header a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Cppcheck Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Source:</strong> {xml_file}</p>
        <p><strong>Files with errors:</strong> {len(file_errors)}</p>
        <p><strong>Total errors:</strong> {sum(len(errors) for errors in file_errors.values())}</p>
"""
    
    if severities:
        html_content += f'        <p><strong>Severities included:</strong> {", ".join(severities)}</p>\n'
    if error_ids:
        html_content += f'        <p><strong>Error IDs included:</strong> {", ".join(error_ids)}</p>\n'
    if not_error_ids:
        html_content += f'        <p><strong>Error IDs excluded:</strong> {", ".join(not_error_ids)}</p>\n'
    if file_pattern:
        html_content += f'        <p><strong>File pattern:</strong> {file_pattern}</p>\n'
    
    html_content += """    </div>
"""
    
    # Sort files alphabetically
    for file_name in sorted(file_errors.keys()):
        errors = file_errors[file_name]
        
        # Create file header with optional GitHub link
        if github_url:
            file_link = create_github_link(github_url, file_name)
            file_header = f'<a href="{file_link}" target="_blank">{file_name}</a> ({len(errors)} errors)'
        else:
            file_header = f"{file_name} ({len(errors)} errors)"
        
        html_content += f"""    <div class="file-section">
        <div class="file-header">{file_header}</div>
"""
        
        # Sort errors by line number
        errors.sort(key=lambda x: int(x['line']) if x['line'].isdigit() else 0)
        
        for error in errors:
            html_content += f"""        <div class="error {error['severity']}">
            <div class="error-header">
                <span class="error-id">{error['id']}</span> - {error['severity'].upper()}
            </div>
            <div class="error-msg">{error['msg']}</div>
"""
            
            if error['verbose'] and error['verbose'] != error['msg']:
                html_content += f"""            <div class="error-verbose">{error['verbose']}</div>
"""
            
            # Create line number with optional GitHub link
            if github_url and error['line'].isdigit():
                line_link = create_github_link(github_url, file_name, error['line'])
                location_text = f'<a href="{line_link}" target="_blank">Line {error["line"]}</a>, Column {error["column"]}'
            else:
                location_text = f'Line {error["line"]}, Column {error["column"]}'
            
            html_content += f"""            <div class="error-location">{location_text}</div>
"""
            
            if error['info']:
                html_content += f"""            <div class="error-info">{error['info']}</div>
"""
            
            html_content += """        </div>
"""
        
        html_content += """    </div>
"""
    
    html_content += """</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def create_github_link(base_url: str, file_path: str, line_number: str = None) -> str:
    """
    Create a GitHub link for a file and optionally a specific line.
    
    Args:
        base_url: Base GitHub repository URL
        file_path: Path to the file in the repository
        line_number: Line number to link to (optional)
    
    Returns:
        GitHub URL for the file/line
    """
    # Remove trailing slash from base URL if present
    base_url = base_url.rstrip('/')
    
    # Create the file link
    file_link = f"{base_url}/{file_path}"
    
    # Add line number if provided
    if line_number and line_number.isdigit():
        file_link += f"#L{line_number}"
    
    return file_link


def main():
    """Main function to parse cppcheck XML and generate reports."""
    parser = argparse.ArgumentParser(
        description='Parse cppcheck XML output and generate CSV or HTML reports'
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        help='Path to the cppcheck XML output file'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for files (default: current directory)'
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help='Generate CSV files (default behavior)'
    )
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML report'
    )
    parser.add_argument(
        '--severity',
        help='Comma-separated list of severities to include (for HTML output)'
    )
    parser.add_argument(
        '--error-id',
        help='Comma-separated list of error IDs to include (for HTML output)'
    )
    parser.add_argument(
        '--not-error-id',
        help='Comma-separated list of error IDs to exclude (for HTML output)'
    )
    parser.add_argument(
        '--file',
        help='Wildcard expression to match file names (for HTML output)'
    )
    parser.add_argument(
        '--github',
        help='GitHub repository URL (e.g., https://github.com/user/repo/blob/main) for file links'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'cppcheck-parser {get_version()}'
    )
    
    args = parser.parse_args()
    
    # Check if input file is provided
    if not args.input_file:
        parser.print_help()
        sys.exit(1)
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Parsing cppcheck XML file: {args.input_file}")
    
    # Parse the XML file
    error_id_counter, severity_counter = parse_cppcheck_xml(args.input_file)
    
    if not error_id_counter:
        print("Warning: No errors found in the XML file")
        return
    
    # Generate output file names
    base_name = Path(args.input_file).stem
    
    # Handle CSV output (default behavior if no specific output type specified)
    if args.csv or (not args.html and not args.csv):
        all_errors_file = output_dir / f"{base_name}_all_errors.csv"
        severities_file = output_dir / f"{base_name}_severities.csv"
        error_only_file = output_dir / f"{base_name}_error_severity_only.csv"
        
        # Write CSV files
        print(f"Generating CSV files in: {output_dir}")
        
        write_csv_all_errors(error_id_counter, all_errors_file)
        print(f"[OK] All errors CSV: {all_errors_file}")
        
        write_csv_severities(severity_counter, severities_file)
        print(f"[OK] Severities CSV: {severities_file}")
        
        write_csv_error_severity_only(error_id_counter, severity_counter, error_only_file)
        print(f"[OK] Error severity only CSV: {error_only_file}")
    
    # Handle HTML output
    if args.html:
        html_file = output_dir / f"{base_name}_report.html"
        
        # Parse filter options
        severities = None
        if args.severity:
            severities = [s.strip() for s in args.severity.split(',')]
        
        error_ids = None
        if args.error_id:
            error_ids = [e.strip() for e in args.error_id.split(',')]
        
        not_error_ids = None
        if args.not_error_id:
            not_error_ids = [e.strip() for e in args.not_error_id.split(',')]
        
        file_pattern = args.file
        github_url = args.github
        
        print(f"Generating HTML report: {html_file}")
        write_html_report(args.input_file, html_file, severities, error_ids, not_error_ids, file_pattern, github_url)
        print(f"[OK] HTML report: {html_file}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total unique error IDs: {len(error_id_counter)}")
    print(f"  Total unique severities: {len(severity_counter)}")
    print(f"  Total error occurrences: {sum(error_id_counter.values())}")
    
    for severity, count in sorted(severity_counter.items()):
        print(f"  {severity}: {count} occurrences")


if __name__ == "__main__":
    main() 