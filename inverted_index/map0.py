#!/usr/bin/env python3
import sys

for line in sys.stdin:
    if "<!DOCTYPE html>" in line:
        print("doc\t1")