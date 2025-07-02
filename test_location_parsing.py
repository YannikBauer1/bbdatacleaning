#!/usr/bin/env python3

# Import the parse_location function from the clean.py file
import sys
import os
sys.path.append('all')

from clean import parse_location

# Test cases
test_cases = [
    "Wy, United States, MIgan",
    "Wy, United States, Mi", 
    "Wy, United States, Michigan",
    "TX, United States, Florida",
    "CA, United States, Texas",
    "Georgia - Usa",  # New pattern
    "Florida - Usa",  # New pattern
    "New York - Usa",  # New pattern
    "Washington - Usa",  # New pattern
    "Atlanta, Georgia",  # Normal case
    "New York, NY, USA",  # Normal case
]

print("Testing location parsing fixes:")
print("=" * 60)
for test_case in test_cases:
    result = parse_location(test_case)
    print(f"'{test_case}' -> {result}") 