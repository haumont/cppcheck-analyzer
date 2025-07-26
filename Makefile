# Makefile for cppcheck-analyzer
# Targets: test, clean, help

# Variables
PYTHON = python3
PARSER = cppcheck_parser.py
TEST_DIR = test
TEST_INPUT = $(TEST_DIR)/sample_cppcheck.xml
TEST_OUTPUT_DIR = $(TEST_DIR)/output
TEST_OUTPUT_FILES = $(TEST_OUTPUT_DIR)/sample_cppcheck_all_errors.csv \
                   $(TEST_OUTPUT_DIR)/sample_cppcheck_severities.csv \
                   $(TEST_OUTPUT_DIR)/sample_cppcheck_error_severity_only.csv

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  test    - Run the parser tests with sample data and verification"
	@echo "  clean   - Remove test output files (preserves test input)"
	@echo "  setup   - Set up test directory structure"
	@echo "  help    - Show this help message"

# Set up test directory structure
.PHONY: setup
setup:
	@echo "Setting up test directory structure..."
	@mkdir -p $(TEST_DIR)
	@mkdir -p $(TEST_OUTPUT_DIR)
	@if [ ! -f $(TEST_INPUT) ]; then \
		echo "Error: Test input file $(TEST_INPUT) not found"; \
		echo "Please ensure sample_cppcheck.xml is in the test directory"; \
		exit 1; \
	fi
	@echo "Test directory setup complete."

# Run tests
.PHONY: test
test: setup
	@echo "Running cppcheck parser tests..."
	@echo "Input file: $(TEST_INPUT)"
	@echo "Output directory: $(TEST_OUTPUT_DIR)"
	@$(PYTHON) $(PARSER) $(TEST_INPUT) --output-dir $(TEST_OUTPUT_DIR)
	@echo ""
	@echo "Test results:"
	@echo "Generated files:"
	@ls -la $(TEST_OUTPUT_DIR)/*.csv
	@echo ""
	@echo "CSV file contents:"
	@echo "=== All Errors CSV ==="
	@cat $(TEST_OUTPUT_DIR)/sample_cppcheck_all_errors.csv
	@echo ""
	@echo "=== Severities CSV ==="
	@cat $(TEST_OUTPUT_DIR)/sample_cppcheck_severities.csv
	@echo ""
	@echo "=== Error Severity Only CSV ==="
	@cat $(TEST_OUTPUT_DIR)/sample_cppcheck_error_severity_only.csv
	@echo ""
	@echo "Verifying parser functionality..."
	@echo "Checking if all expected files were created..."
	@for file in $(TEST_OUTPUT_FILES); do \
		if [ -f $$file ]; then \
			echo "✓ $$file exists"; \
		else \
			echo "✗ $$file missing"; \
			exit 1; \
		fi; \
	done
	@echo "All verification checks passed!"
	@echo "Tests completed successfully!"

# Clean up test files and directories
.PHONY: clean
clean:
	@echo "Cleaning up test output files..."
	@rm -rf $(TEST_OUTPUT_DIR)
	@echo "Cleanup complete."



# Show test directory structure
.PHONY: show-test-dir
show-test-dir:
	@echo "Test directory structure:"
	@if [ -d $(TEST_DIR) ]; then \
		find $(TEST_DIR) -type f -name "*.csv" -o -name "*.xml" | sort; \
	else \
		echo "Test directory does not exist. Run 'make setup' first."; \
	fi 