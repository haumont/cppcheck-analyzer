#!/usr/bin/env python3
"""
Test verification script for cppcheck parser

This script verifies that the generated CSV files contain the expected counts
and data based on the test XML file.
"""

import csv
import sys
from pathlib import Path

def load_csv_data(csv_file):
    """Load CSV data and return as a dictionary."""
    data = {}
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header
        for row in reader:
            if len(row) >= 2:
                count = int(row[0])
                key = row[1]
                data[key] = count
    return data

def verify_all_errors_csv(csv_file):
    """Verify the all errors CSV file."""
    print("Verifying All Errors CSV...")
    data = load_csv_data(csv_file)
    
    expected = {
        'arrayIndexOutOfBounds': 2,
        'nullPointer': 3,
        'uninitvar': 1,
        'memleak': 2,
        'doubleFree': 1,
        'uninitDerivedMemberVar': 1,
        'dupInheritedMember': 1,
        'unusedFunction': 2
    }
    
    errors = []
    for key, expected_count in expected.items():
        if key not in data:
            errors.append(f"Missing error ID: {key}")
        elif data[key] != expected_count:
            errors.append(f"Wrong count for {key}: expected {expected_count}, got {data[key]}")
    
    # Check for unexpected entries
    for key in data:
        if key not in expected:
            errors.append(f"Unexpected error ID: {key} with count {data[key]}")
    
    if errors:
        print("❌ All Errors CSV verification failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All Errors CSV verification passed")
        return True

def verify_severities_csv(csv_file):
    """Verify the severities CSV file."""
    print("Verifying Severities CSV...")
    data = load_csv_data(csv_file)
    
    expected = {
        'error': 10,
        'warning': 1,
        'style': 2
    }
    
    errors = []
    for key, expected_count in expected.items():
        if key not in data:
            errors.append(f"Missing severity: {key}")
        elif data[key] != expected_count:
            errors.append(f"Wrong count for {key}: expected {expected_count}, got {data[key]}")
    
    # Check for unexpected entries
    for key in data:
        if key not in expected:
            errors.append(f"Unexpected severity: {key} with count {data[key]}")
    
    if errors:
        print("❌ Severities CSV verification failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Severities CSV verification passed")
        return True

def verify_error_severity_only_csv(csv_file):
    """Verify the error severity only CSV file."""
    print("Verifying Error Severity Only CSV...")
    data = load_csv_data(csv_file)
    
    expected = {
        'arrayIndexOutOfBounds': 2,
        'nullPointer': 3,
        'uninitvar': 1,
        'memleak': 2,
        'doubleFree': 1,
        'uninitDerivedMemberVar': 1
    }
    
    errors = []
    for key, expected_count in expected.items():
        if key not in data:
            errors.append(f"Missing error ID: {key}")
        elif data[key] != expected_count:
            errors.append(f"Wrong count for {key}: expected {expected_count}, got {data[key]}")
    
    # Check for unexpected entries
    for key in data:
        if key not in expected:
            errors.append(f"Unexpected error ID: {key} with count {data[key]}")
    
    if errors:
        print("❌ Error Severity Only CSV verification failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Error Severity Only CSV verification passed")
        return True

def main():
    """Main verification function."""
    output_dir = Path("test/output")
    
    if not output_dir.exists():
        print("❌ Test output directory not found. Run 'make test' first.")
        sys.exit(1)
    
    all_errors_file = output_dir / "sample_cppcheck_all_errors.csv"
    severities_file = output_dir / "sample_cppcheck_severities.csv"
    error_only_file = output_dir / "sample_cppcheck_error_severity_only.csv"
    
    print("=" * 50)
    print("CSV VERIFICATION TESTS")
    print("=" * 50)
    
    success = True
    
    if not all_errors_file.exists():
        print("❌ All Errors CSV file not found")
        success = False
    else:
        success &= verify_all_errors_csv(all_errors_file)
    
    if not severities_file.exists():
        print("❌ Severities CSV file not found")
        success = False
    else:
        success &= verify_severities_csv(severities_file)
    
    if not error_only_file.exists():
        print("❌ Error Severity Only CSV file not found")
        success = False
    else:
        success &= verify_error_severity_only_csv(error_only_file)
    
    print("=" * 50)
    if success:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("Expected counts verified:")
        print("  - arrayIndexOutOfBounds: 2")
        print("  - nullPointer: 3")
        print("  - memleak: 2")
        print("  - unusedFunction: 2")
        print("  - error severity: 10")
        print("  - style severity: 2")
        print("  - warning severity: 1")
    else:
        print("❌ SOME VERIFICATION TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main() 