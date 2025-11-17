#!/usr/bin/env bash
# scan_and_add.sh
# Continuously poll proxmark3 for a tag; when a tag is seen, call auto_add_ultralight.py
# Usage: ./scan_and_add.sh
# Configure DEVICE, PROXMARK_BIN, ADD_SCRIPT, and VENV_PATH as needed.

set -euo pipefail

DEVICE="/dev/ttyACM0"
PROXMARK_BIN="$(command -v proxmark3 || echo /usr/bin/proxmark3)"
ADD_SCRIPT="${HOME}/auto_add_ultralight.py"
VENV_PATH="${HOME}/pn532env/bin/activate"
POLL_INTERVAL=2
DEBOUNCE_SECONDS=6
TIMEOUT=6

if [[ ! -x "$PROXMARK_BIN" ]]; then
  echo "Warning: proxmark3 binary not found at PATH. Is proxmark3 installed? (expected at: $PROXMARK_BIN)"
fi

if [[ ! -f "$ADD_SCRIPT" ]]; then
  echo "Error: add script not found at: $ADD_SCRIPT"
  echo "Place auto_add_ultralight.py at that path or edit ADD_SCRIPT variable."
  exit 1
fi

echo "Scan-and-add starting..."
echo "Proxmark device: $DEVICE"
echo "Add script: $ADD_SCRIPT"
echo "Using venv activation script: $VENV_PATH (if present)"
echo

last_added_ts=0

run_proxmark_cmd() {
  local cmd="$1"
  
  timeout "$TIMEOUT" sudo "$PROXMARK_BIN" "$DEVICE" -c "$cmd" 2>&1 || true
}

# parse UID from proxmark output. prefer lines containing UID:, fallback to any 4-8 byte hex group
extract_uid() {
  local out="$1"
  # Look for a line containing 'UID' (common format: "UID : 04 A2 1B CF 2A 80 01")
  local uid_line
  uid_line="$(printf "%s\n" "$out" | awk 'tolower($0) ~ /uid/ { print; exit }' || true)"
  if [[ -n "$uid_line" ]]; then
    # extract hex bytes from that line
    # remove everything except hex digits and separators, then strip separators
    local hex
    hex="$(printf "%s\n" "$uid_line" | grep -Eo '([0-9A-Fa-f]{2}([ :\-]?|$)){4,8}' | head -n1 | tr -d ' :-' )"
    printf "%s\n" "$hex"
    return 0
  fi

  # fallback: try to find the first 4-8 byte-looking hex group in the whole output
  local fallback
  fallback="$(printf "%s\n" "$out" | grep -Eo '([0-9A-Fa-f]{2}[: -]?){4,8}' | head -n1 | tr -d ' :-' || true)"
  if [[ -n "$fallback" ]]; then
    printf "%s\n" "$fallback"
    return 0
  fi

  return 1
}

while true; do
  # poll proxmark for a quick tag check; hf 14a info is commonly available
  echo "Polling for tag (press Ctrl+C to stop)..."
  OUT="$(run_proxmark_cmd "hf 14a info")"

  UIDHEX="$(extract_uid "$OUT" || true)"

  if [[ -n "$UIDHEX" ]]; then
    ts_now=$(date +%s)
    elapsed=$((ts_now - last_added_ts))
    # Debounce to avoid adding repeatedly while card remains on antenna
    if (( elapsed < DEBOUNCE_SECONDS )); then
      echo "Detected UID ${UIDHEX}, but still within debounce (${elapsed}s elapsed). Skipping."
      sleep 1
      continue
    fi

    echo
    echo ">>> Tag detected: $UIDHEX"
    echo "Running add script to dump & add the tag. Keep the tag on the proxmark antenna..."
    # activate venv if available
    if [[ -f "$VENV_PATH" ]]; then
      # shellcheck disable=SC1090
      source "$VENV_PATH"
    fi

    # call add script - it will run proxmark again to perform the full dump
    if python3 "$ADD_SCRIPT"; then
      echo "Add script completed successfully."
      last_added_ts=$(date +%s)
      exit
    else
      echo "Add script failed. See its output for details."
      exit
    fi
    echo
    # small pause after adding
    sleep 1
  else
    # no tag found
    sleep "$POLL_INTERVAL"
  fi
done
