#!/bin/bash

./scan_and_add_demo.sh || { echo "Add card failed, beginning authentication"; exit 1; }

python3 pn532_ultralight_matcher.py || { echo "Authentication scan failed. If you get this consistently, call J."; exit 1; }
echo "Task End"
