# Cppcheck XML Parser

A Python 3.6+ parser that reads cppcheck XML output and generates CSV files and HTML reports for analysis and visualization.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Jeff Haumont

## Features

The parser generates multiple output formats:

### CSV Reports
1. **All Errors CSV**: Contains all error IDs with their occurrence counts, sorted by count (ascending)
2. **Severities CSV**: Contains all severity levels with their counts, sorted alphabetically
3. **Error Severity Only CSV**: Contains only error IDs with "error" severity, sorted by count (ascending)

### HTML Reports
- **Interactive HTML Reports**: Generate detailed HTML reports with error grouping by file
- **GitHub Integration**: Direct links to source code files and line numbers
- **Filtering Options**: Filter by severity, error ID, file patterns, and exclude specific errors
- **Responsive Design**: Modern, mobile-friendly HTML output with CSS styling

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)
- Make (for using the Makefile targets)

## Downloads

A release archive is available containing:
- The main script (`cppcheck_parser.py`)
- Sample test data
- Documentation and license
- Makefile for easy testing

Download the latest release from the [Releases page](https://github.com/your-username/cppcheck-analyzer/releases).

## Project Structure

```
cppcheck-analyzer/
├── cppcheck_parser.py      # Main parser script
├── Makefile               # Build and test automation
├── README.md              # This documentation
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules
├── test_verification.py   # CSV verification tests
└── test/                  # Test directory
    ├── sample_cppcheck.xml    # Sample input data for testing
    └── output/            # Generated CSV files (created by make test, ignored by git)
        ├── *_all_errors.csv
        ├── *_severities.csv
        ├── *_error_severity_only.csv
        └── *_report.html
```

## Usage

### Basic Usage

```bash
python3 cppcheck_parser.py <input_xml_file>
```

### Command Line Options

```bash
python3 cppcheck_parser.py <input_xml_file> [OPTIONS]
```

#### Output Options
- `--output-dir <directory>` - Specify output directory (default: current directory)
- `--csv` - Generate CSV files (default behavior)
- `--html` - Generate HTML report

#### HTML Report Filtering Options
- `--severity <list>` - Comma-separated list of severities to include (e.g., "error,warning")
- `--error-id <list>` - Comma-separated list of error IDs to include
- `--not-error-id <list>` - Comma-separated list of error IDs to exclude
- `--file <pattern>` - Wildcard pattern for file names (e.g., "*.cpp")
- `--github <url>` - GitHub repository URL for file links (e.g., "https://github.com/user/repo/blob/main")

#### General Options
- `--version` - Show version information
- `-h, --help` - Show help message

### Examples

#### Basic CSV Generation
```bash
python3 cppcheck_parser.py sample_cppcheck.xml
```

#### Custom Output Directory
```bash
python3 cppcheck_parser.py sample_cppcheck.xml --output-dir /path/to/output
```

#### HTML Report Generation
```bash
python3 cppcheck_parser.py sample_cppcheck.xml --html
```

#### HTML Report with GitHub Integration
```bash
python3 cppcheck_parser.py sample_cppcheck.xml --html --github "https://github.com/user/repo/blob/main"
```

#### HTML Report with Filtering
```bash
# Only show error severity issues
python3 cppcheck_parser.py sample_cppcheck.xml --html --severity error

# Exclude specific error types
python3 cppcheck_parser.py sample_cppcheck.xml --html --not-error-id unusedFunction,style

# Filter by file pattern
python3 cppcheck_parser.py sample_cppcheck.xml --html --file "*.cpp"

# Combine multiple filters
python3 cppcheck_parser.py sample_cppcheck.xml --html --severity error --not-error-id unusedFunction --file "src/*.cpp"
```

## Output Files

### CSV Files

#### 1. All Errors CSV
Contains all error IDs found in the XML, regardless of severity, with counts sorted from lowest to highest.

Example:
```csv
Count,Error ID
1,uninitvar
1,doubleFree
1,uninitDerivedMemberVar
1,dupInheritedMember
2,arrayIndexOutOfBounds
2,memleak
2,unusedFunction
3,nullPointer
```

#### 2. Severities CSV
Contains all severity levels found in the XML, with counts sorted alphabetically by severity name.

Example:
```csv
Count,Severity
10,error
2,style
1,warning
```

#### 3. Error Severity Only CSV
Contains only error IDs that have "error" severity, with counts sorted from lowest to highest.

Example:
```csv
Count,Error ID
1,uninitvar
1,doubleFree
1,uninitDerivedMemberVar
2,arrayIndexOutOfBounds
2,memleak
3,nullPointer
```

### HTML Reports

The HTML reports provide:
- **File-based grouping**: Errors organized by source file
- **Line-by-line details**: Each error shows file, line, and column information
- **Severity color coding**: Different colors for error, warning, style, and info severities
- **GitHub integration**: Direct links to source code when GitHub URL is provided
- **Filtering support**: Reports can be filtered by severity, error ID, or file patterns
- **Responsive design**: Works on desktop and mobile devices

#### HTML Report Features
- **Summary section**: Shows total files, errors, and applied filters
- **File sections**: Each file with errors gets its own collapsible section
- **Error details**: Full error messages, verbose descriptions, and location information
- **Multi-location support**: Handles errors that span multiple files/lines
- **GitHub links**: Clickable links to specific lines in the repository

## Input Format

The parser expects cppcheck XML output in the standard format:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<results version="2">
    <cppcheck version="2.13.0"/>
    <errors>
        <error id="errorId" severity="severity" msg="message" verbose="detailed message">
            <location file="file.c" line="10" column="5" info="additional info"/>
            <location file="file.c" line="15" column="8"/>
        </error>
        <!-- more errors... -->
    </errors>
</results>
```

## Error Handling

- Invalid XML files will result in an error message and exit
- Missing input files will result in an error message and exit
- Empty XML files (no errors) will generate empty CSV files with headers only
- Invalid command line options will show help and exit
- Non-existent output directories will be created automatically

## Testing

A comprehensive test suite is included with sample data and verification scripts.

### Using Makefile (Recommended)

```bash
# Run complete tests with CSV and HTML generation
make test

# Run detailed CSV verification tests
make verify

# Clean up test files and directories
make clean

# Set up test directory structure
make setup

# Show available targets
make help

# Show version information
make version

# Show test directory structure
make show-test-dir
```

### Manual Testing

```bash
# Test CSV generation
python3 cppcheck_parser.py test/sample_cppcheck.xml --output-dir test/output --csv

# Test HTML generation
python3 cppcheck_parser.py test/sample_cppcheck.xml --output-dir test/output --html

# Test with GitHub integration
python3 cppcheck_parser.py test/sample_cppcheck.xml --output-dir test/output --html --github "https://github.com/user/repo/blob/main"
```

### Verification Tests

The included `test_verification.py` script validates that generated CSV files contain the expected data:

```bash
python3 test_verification.py
```

This verifies:
- Correct error ID counts
- Proper severity distributions
- Accurate error-only filtering
- Expected total counts

## Installation

### Quick Start

```bash
# Download and extract the release
wget https://github.com/your-username/cppcheck-analyzer/releases/latest/download/cppcheck-parser-v1.4.0.tar.gz
tar -xzf cppcheck-parser-v1.4.0.tar.gz
cd cppcheck-parser-v1.4.0

# Make the script executable
chmod +x cppcheck_parser.py

# Run tests
make test

# Use the parser
./cppcheck_parser.py your_cppcheck_output.xml
```

### From Source

```bash
# Clone the repository
git clone https://github.com/your-username/cppcheck-analyzer.git
cd cppcheck-analyzer

# Make the script executable
make build

# Run tests
make test
```

### Makefile Targets

- `make test` - Run complete parser tests with CSV and HTML generation
- `make verify` - Run detailed CSV verification tests
- `make clean` - Remove test output files (preserves test input data)
- `make setup` - Set up test directory structure
- `make build` - Make script executable
- `make version` - Show version information
- `make show-test-dir` - Show test directory structure
- `make help` - Show available targets

## Version History

- **v1.4.0** - Updated HTML reports to use "issues" terminology and added severity breakdown
- **v1.3.0** - Added HTML report generation with filtering and GitHub integration
- **v0.1.1** - Initial CSV-only version with basic error parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run `make test` to ensure everything works
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 