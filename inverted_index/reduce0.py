#!/usr/bin/env python3
import sys

total = 0
for line in sys.stdin:
    key, value = line.strip().split('\t')
    total += int(value)

print(total)
