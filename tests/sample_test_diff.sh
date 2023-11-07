#!/bin/bash

# first install coverage.py:
# https://coverage.readthedocs.io/en/latest/install.html

# earse previous coverage
coverage erase
# start a hard-coded server in background by coverage and keep the output
coverage run --append tests/sample_server.py tests/sample.conf > tmp.actual.out &
# delay 2s to make sure the server is up and listening at port 1024
sleep 2
echo fake recursor sends EXIT
# terminate the server by sending EXIT command
cat tests/exit_1.in | nc localhost 1024
# delay 0.1s
sleep 0.1
# print the coverage report, expect 100% coverage rate
coverage report -m
# compare the actual output and the expected output, but they are different!?
diff tmp.actual.out tests/exit_1.out
