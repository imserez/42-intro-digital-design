#!/usr/bin/env python3

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter

# ==============================================================================
# Exercise Configuration
# ==============================================================================

EXERCISE_NAME = "00.01 - Traffic Light"

JAR = "logisim-evolution.jar"
HARNESS = "circ_files/harness.circ"
EXPECTED = "expected.out"

# Circuit copied by test.sh
STUDENT = "circ_files/student.circ"

# Output generated after simulation
STUDENT_OUTPUT = "student_output/output.txt"

# ------------------------------------------------------------------------------
# Checks
# ------------------------------------------------------------------------------

CHECK_OUTPUT = True
CHECK_ALLOWED_GATES = False
CHECK_FORBIDDEN_GATES = True
CHECK_GATE_COUNT = False
CHECK_COMPONENT_LIMITS = False
CHECK_SUBCIRCUITS = True

# ------------------------------------------------------------------------------
# Restrictions
# ------------------------------------------------------------------------------

MAX_GATES = 4

MAX_COMPONENTS = {

    "AND Gate": 2,
    "OR Gate": 1,
    "NOT Gate": 1,

}

ALLOWED_GATES = {
    # Gates
    "AND Gate",
    "OR Gate",
    "NOT Gate",

    # Wiring
    "Pin",
    "Tunnel",
    "Splitter",
    "Probe",
    "Constant",

    # Misc
    "Text",
}

FORBIDDEN_COMPONENTS = {
    "Multiplexer",
    "Demultiplexer",
    "Decoder",
    "Priority Encoder",
    "XOR Gate",
    "XNOR Gate",
}

# ==============================================================================
# Helper Functions
# ==============================================================================

def fail(message):
    print("\n[FAIL]")
    print(message)
    sys.exit(1)


def ok(step):
    print(f"{step:<28} OK")


def normalize(line):
    return (
        line.replace(" ", "")
            .replace("U", "0")
            .replace("u", "0")
            .replace("X", "0")
            .replace("x", "0")
    )

# ==============================================================================
# Environment
# ==============================================================================

def check_environment():

    required = [
        JAR,
        HARNESS,
        STUDENT
    ]

    if CHECK_OUTPUT:
        required.append(EXPECTED)

    for file in required:

        if not os.path.exists(file):
            fail(f"Missing file:\n\n{file}")

    os.makedirs(os.path.dirname(STUDENT_OUTPUT), exist_ok=True)

    ok("Environment")

# ==============================================================================
# Logisim
# ==============================================================================

def run_logisim():

    try:

        process = subprocess.Popen(

            [
                "java",
                "-jar",
                JAR,
                "-tty",
                "table",
                HARNESS
            ],

            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True

        )

        stdout, stderr = process.communicate()

    except Exception as e:

        fail(f"Unable to execute Logisim.\n\n{e}")

    with open(STUDENT_OUTPUT, "w") as f:
        f.write(stdout)

    ok("Simulation")

    return stdout

# ==============================================================================
# Output
# ==============================================================================

def compare_output(output):

    with open(EXPECTED) as f:
        expected = [x.strip() for x in f.readlines() if x.strip()]

    student = [x.strip() for x in output.splitlines() if x.strip()]

    if not student:
        fail("No output generated.")

    if expected and "RESULT" in expected[0]:
        expected = expected[1:]

    if student and "RESULT" in student[0]:
        student = student[1:]

    if len(expected) != len(student):

        fail(
            "Output length mismatch.\n\n"
            f"Expected : {len(expected)} lines\n"
            f"Received : {len(student)} lines"
        )

    for line, (exp, stu) in enumerate(zip(expected, student), start=1):

        exp = normalize(exp)
        stu = normalize(stu)

        if exp != stu:

            fail(
                f"Output mismatch (line {line})\n\n"
                f"Expected : {exp}\n"
                f"Received : {stu}"
            )

    ok("Output")

# ==============================================================================
# XML
# ==============================================================================

def load_student():

    try:
        tree = ET.parse(STUDENT)
        return tree.getroot()

    except Exception as e:

        fail(f"Unable to parse student circuit.\n\n{e}")


def get_components():

    root = load_student()

    components = Counter()

    for comp in root.iter("comp"):

        name = comp.attrib.get("name")

        if name:
            components[name] += 1

    return components


# ==============================================================================
# Restrictions
# ==============================================================================

def check_allowed():

    used = get_components()

    for component in sorted(used):

        if component not in ALLOWED_GATES:

            fail(
                "Component not allowed.\n\n"
                f"{component}"
            )

    ok("Allowed components")


def check_forbidden():

    used = get_components()

    for component in sorted(used):

        if component in FORBIDDEN_COMPONENTS:

            fail(
                "Forbidden component detected.\n\n"
                f"{component}"
            )

    ok("Forbidden components")


def check_gate_count():

    if MAX_GATES is None:
        return

    used = get_components()

    gates = sum(
        count
        for name, count in used.items()
        if name.endswith("Gate")
    )

    if gates > MAX_GATES:

        fail(
            "Gate limit exceeded.\n\n"
            f"Maximum : {MAX_GATES}\n"
            f"Found   : {gates}"
        )

    ok("Gate count")

def check_component_limits():

    if not MAX_COMPONENTS:
        return

    used = get_components()

    for component, maximum in MAX_COMPONENTS.items():

        found = used.get(component, 0)

        if found > maximum:

            fail(
                "Component limit exceeded.\n\n"
                f"{component}\n"
                f"Maximum : {maximum}\n"
                f"Found   : {found}"
            )

    ok("Component limits")


def check_subcircuits():

    root = load_student()

    #
    # Standard libraries:
    #
    # 0  Wiring
    # 1  Gates
    # 2  Plexers
    # 3  Arithmetic
    # 4  Memory
    # 5  I/O
    # 6  TTL
    # 7  TCL
    # 8  Base
    # 9  BFH
    # 10 Extras
    # 11 SoC
    #
    # Any library above 11 is a custom circuit.
    #

    for comp in root.iter("comp"):

        lib = comp.attrib.get("lib")

        if lib is None:
            continue

        try:
            lib = int(lib)
        except ValueError:
            continue

        if lib > 11:

            name = comp.attrib.get("name", "Unknown")

            fail(
                "Custom subcircuits are not allowed.\n\n"
                f"{name}"
            )

    ok("Subcircuits")


# ==============================================================================
# Main
# ==============================================================================

def main():

    print(f"\nExercise : {EXERCISE_NAME}\n")

    check_environment()

    output = run_logisim()

    if CHECK_OUTPUT:
        compare_output(output)

    if CHECK_ALLOWED_GATES:
        check_allowed()

    if CHECK_COMPONENT_LIMITS:
        check_component_limits()

    if CHECK_FORBIDDEN_GATES:
        check_forbidden()

    if CHECK_GATE_COUNT:
        check_gate_count()

    if CHECK_SUBCIRCUITS:
        check_subcircuits()

    print("\n[PASS]")
    print("All tests passed.")


if __name__ == "__main__":
    main()