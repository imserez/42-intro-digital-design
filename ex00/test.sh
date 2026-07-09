#!/bin/bash

mkdir -p .tester/circ_files
mkdir -p .tester/student_output

cp mux.circ .tester/circ_files/student.circ

cd .tester
python3 tester.py