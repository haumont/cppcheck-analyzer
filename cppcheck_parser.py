#!/usr/bin/env python3.13
"""
Cppcheck XML Parser

Copyright (c) 2025 Jeff Haumont

This script parses cppcheck XML output and generates three CSV files:
1. All error IDs with counts, sorted by count (descending)
2. All severity levels with counts, sorted alphabetically
3. Only error severity IDs with counts, sorted by count (ascending)

Usage: python3.13 cppcheck_parser.py <input_xml_file>
"""

import xml.etree.ElementTree as ET
import csv
import sys
import argparse
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


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
    Write CSV file with all error IDs and their counts, sorted by count (descending).
    
    Args:
        error_id_counter: Counter object with error IDs and counts
        output_file: Output CSV file path
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Error ID', 'Count'])
        
        # Sort by count in descending order
        for error_id, count in error_id_counter.most_common():
            writer.writerow([error_id, count])


def write_csv_severities(severity_counter: Counter, output_file: str):
    """
    Write CSV file with all severity levels and their counts, sorted alphabetically.
    
    Args:
        severity_counter: Counter object with severities and counts
        output_file: Output CSV file path
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Severity', 'Count'])
        
        # Sort alphabetically by severity name
        for severity in sorted(severity_counter.keys()):
            count = severity_counter[severity]
            writer.writerow([severity, count])


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
        writer.writerow(['Error ID', 'Count'])
        
        # Sort by count in ascending order
        for error_id, count in sorted(error_only_ids.items(), key=lambda x: x[1]):
            writer.writerow([error_id, count])


def main():
    """Main function to parse cppcheck XML and generate CSV files."""
    parser = argparse.ArgumentParser(
        description='Parse cppcheck XML output and generate CSV reports for Excel import'
    )
    parser.add_argument(
        'input_file',
        help='Path to the cppcheck XML output file'
    )
    parser.add_argument(
        '--output-dir',
        default='.',
        help='Output directory for CSV files (default: current directory)'
    )
    
    args = parser.parse_args()
    
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
    all_errors_file = output_dir / f"{base_name}_all_errors.csv"
    severities_file = output_dir / f"{base_name}_severities.csv"
    error_only_file = output_dir / f"{base_name}_error_severity_only.csv"
    
    # Write CSV files
    print(f"Generating CSV files in: {output_dir}")
    
    write_csv_all_errors(error_id_counter, all_errors_file)
    print(f"✓ All errors CSV: {all_errors_file}")
    
    write_csv_severities(severity_counter, severities_file)
    print(f"✓ Severities CSV: {severities_file}")
    
    write_csv_error_severity_only(error_id_counter, severity_counter, error_only_file)
    print(f"✓ Error severity only CSV: {error_only_file}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Total unique error IDs: {len(error_id_counter)}")
    print(f"  Total unique severities: {len(severity_counter)}")
    print(f"  Total error occurrences: {sum(error_id_counter.values())}")
    
    for severity, count in sorted(severity_counter.items()):
        print(f"  {severity}: {count} occurrences")


if __name__ == "__main__":
    main() 