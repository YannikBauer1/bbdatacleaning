#!/usr/bin/env python3
"""
CSV Validation Script
Checks for common CSV issues like inconsistent field counts, improper quoting, etc.
"""

import csv
import sys
import os

def validate_csv(file_path):
    """Validate a CSV file for common issues."""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return False
    
    issues = []
    total_rows = 0
    header_fields = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            total_rows = len(rows)
            
            if total_rows == 0:
                issues.append("File is empty")
                return False
            
            header_fields = len(rows[0])
            print(f"Header has {header_fields} fields")
            
            # Check each row for field count consistency
            for i, row in enumerate(rows, 1):
                if len(row) != header_fields:
                    issues.append(f"Row {i}: Expected {header_fields} fields, got {len(row)} fields")
                    if len(issues) >= 10:  # Limit the number of issues reported
                        issues.append("... (more issues found)")
                        break
            
            # Check for empty fields that might indicate data issues
            empty_field_rows = []
            for i, row in enumerate(rows[1:], 2):  # Skip header
                empty_count = sum(1 for field in row if field.strip() == '')
                if empty_count > len(row) * 0.8:  # More than 80% empty
                    empty_field_rows.append(i)
                    if len(empty_field_rows) >= 5:
                        break
            
            if empty_field_rows:
                issues.append(f"Rows with mostly empty fields: {empty_field_rows[:5]}")
    
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    # Report results
    print(f"Total rows: {total_rows}")
    print(f"Issues found: {len(issues)}")
    
    if issues:
        print("\nIssues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✓ CSV file appears to be valid")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_csv.py <csv_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    is_valid = validate_csv(file_path)
    sys.exit(0 if is_valid else 1) 