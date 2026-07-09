#!/bin/bash

set -e

# ============================================================================
# Configuration
# ============================================================================

STUDENT_FILE="traffic_light.circ"

# ============================================================================

TESTER_DIR=".tester"
CIRCUITS_DIR="$TESTER_DIR/circ_files"

# Check student submission
if [ ! -f "$STUDENT_FILE" ]; then
    echo "[FAIL]"
    echo
    echo "Missing submission:"
    echo "  $STUDENT_FILE"
    exit 1
fi

# Check tester
if [ ! -f "$TESTER_DIR/tester.py" ]; then
    echo "[FAIL]"
    echo
    echo "Missing tester.py"
    exit 1
fi

# Prepare directories
mkdir -p "$CIRCUITS_DIR"
mkdir -p "$TESTER_DIR/student_output"

# Clean previous output
rm -f "$TESTER_DIR/student_output/"*

# Copy student circuit
cp "$STUDENT_FILE" "$CIRCUITS_DIR/student.circ"

# Run tester
cd "$TESTER_DIR"
python3 tester.py