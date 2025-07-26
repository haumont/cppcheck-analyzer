# Cppcheck XML Parser

A Python 3.13 parser that reads cppcheck XML output and generates three CSV files intended for Excel import.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Jeff Haumont

## Features

The parser generates three CSV files:

1. **All Errors CSV**: Contains all error IDs with their occurrence counts, sorted by count (descending)
2. **Severities CSV**: Contains all severity levels with their counts, sorted alphabetically
3. **Error Severity Only CSV**: Contains only error IDs with "error" severity, sorted by count (ascending)

## Requirements

- Python 3.13
- No external dependencies (uses only standard library)
- Make (for using the Makefile targets)

## Project Structure

```
cppcheck-analyzer/
├── cppcheck_parser.py      # Main parser script
├── Makefile               # Build and test automation
├── README.md              # This documentation
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
└── test/                  # Test directory
    ├── sample_cppcheck.xml    # Sample input data for testing
    └── output/            # Generated CSV files (created by make test, ignored by git)
        ├── *_all_errors.csv
        ├── *_severities.csv
        └── *_error_severity_only.csv
```

## Usage

### Basic Usage

```bash
python3.13 cppcheck_parser.py <input_xml_file>
```

### With Custom Output Directory

```bash
python3.13 cppcheck_parser.py <input_xml_file> --output-dir /path/to/output
```

### Example

```bash
python3.13 cppcheck_parser.py sample_cppcheck.xml
```

This will generate:
- `sample_cppcheck_all_errors.csv`
- `sample_cppcheck_severities.csv`
- `sample_cppcheck_error_severity_only.csv`

## Output Files

### 1. All Errors CSV
Contains all error IDs found in the XML, regardless of severity, with counts sorted from highest to lowest.

Example:
```csv
Error ID,Count
arrayIndexOutOfBounds,1
nullPointer,1
uninitvar,1
memleak,1
doubleFree,1
uninitDerivedMemberVar,1
dupInheritedMember,1
```

### 2. Severities CSV
Contains all severity levels found in the XML, with counts sorted alphabetically by severity name.

Example:
```csv
Severity,Count
error,6
warning,1
```

### 3. Error Severity Only CSV
Contains only error IDs that have "error" severity, with counts sorted from lowest to highest.

Example:
```csv
Error ID,Count
arrayIndexOutOfBounds,1
nullPointer,1
uninitvar,1
memleak,1
doubleFree,1
uninitDerivedMemberVar,1
```

## Input Format

The parser expects cppcheck XML output in the standard format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
    <cppcheck version="2.13.0"/>
    <errors>
        <error id="errorId" severity="severity" msg="message" ...>
            <location file="file.c" line="10" column="5"/>
        </error>
        <!-- more errors... -->
    </errors>
</results>
```

## Error Handling

- Invalid XML files will result in an error message and exit
- Missing input files will result in an error message and exit
- Empty XML files (no errors) will generate empty CSV files with headers only

## Testing

A sample XML file (`sample_cppcheck.xml`) is included for testing purposes. You can test the parser using the provided Makefile:

### Using Makefile (Recommended)

```bash
# Run tests with organized test directory structure
make test

# Clean up test files and directories
make clean

# Show available targets
make help
```

### Manual Testing

```bash
python3.13 cppcheck_parser.py sample_cppcheck.xml
```

### Makefile Targets

- `make test` - Run the parser tests with sample data and verification
- `make clean` - Remove test output files (preserves test input data)
- `make setup` - Set up test directory structure
- `make show-test-dir` - Show test directory structure
- `make help` - Show available targets 