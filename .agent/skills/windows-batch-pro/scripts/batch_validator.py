import sys
import os
import re

def validate_batch(file_path):
    """
    Performs a static syntax validation of Batch files for A2LT standards.
    """
    print(f"--- A2LT Batch Validator ---")
    print(f"File: {file_path}")
    
    errors = []
    
    if not os.path.exists(file_path):
        print("[CRITICAL] File not found.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='cp1252', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[CRITICAL] Could not read file: {e}")
        sys.exit(1)

    # 1. Check for @echo off
    if not any('@echo off' in line.lower() for line in lines):
        errors.append("Warning: Missing '@echo off'. Script might be too verbose.")

    # 2. Check for setlocal
    if not any('setlocal' in line.lower() for line in lines):
        errors.append("Warning: Missing 'setlocal'. Variables might leak to global scope.")

    # 3. Label Validation
    # Correct label format: :label_name at the START of the line
    labels = [line.strip().replace(':', '').lower() for line in lines if line.strip().startswith(':')]
    
    # Catch GOTO targets
    gotos = [re.search(r'goto\s+([a-zA-Z0-9_\-]+)', line.lower()) for line in lines if 'goto' in line.lower()]
    calls = [re.search(r'call\s+:([a-zA-Z0-9_\-]+)', line.lower()) for line in lines if 'call :' in line.lower()]
    
    targets = [g.group(1) for g in gotos if g] + [c.group(1) for c in calls if c]
    
    for t in targets:
        if t not in labels and t != 'eof':
            errors.append(f"Error: Target ':{t}' not found in script.")

    # 4. Dangerous Commands Check
    dangerous = ['rd /s /q c:\\', 'format c:']
    for idx, line in enumerate(lines):
        for cmd in dangerous:
            if cmd in line.lower():
                errors.append(f"CRITICAL: Highly dangerous command detected at line {idx+1}: {cmd}")

    if errors:
        print("\nValidation Issues Found:")
        for err in errors:
            print(f"- {err}")
        
        if any(e.startswith("Error") or e.startswith("CRITICAL") for e in errors):
            print("\n[RESULT] FAILED: Fix critical errors before deploying.")
            sys.exit(1)
    
    print("\n[RESULT] SUCCESS: Basic architecture validated.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_validator.py <file.bat>")
        sys.exit(1)
    validate_batch(sys.argv[1])
