#!/usr/bin/env python3

import time
import json
from pathlib import Path
from binascii import hexlify
import sys
import subprocess

try:
    import board
    import busio
    from adafruit_pn532.i2c import PN532_I2C
except Exception as e:
    print("Missing CircuitPython libs. Ensure adafruit-blinka and adafruit-circuitpython-pn532 are installed in your venv.")
    print("Error:", e)
    raise

HOME = Path.home()
WHITELIST_PATH = HOME / "pn532_ultralight_whitelist.json"
LOG_PATH = HOME / "pn532_access_log.csv"

POLL_INTERVAL = 0.3      
MAX_PAGES_TO_TRY = 64    

def load_whitelist(path=WHITELIST_PATH):
    if not path.exists():
        print("Whitelist not found; creating empty one at:", path)
        path.write_text("[]")
        return []
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print("Failed to parse whitelist JSON:", e)
        return []

def append_log(ts, uid_hex, pages_hex, pages_read_count, allowed, notes=""):
    try:
        if not LOG_PATH.exists():
            LOG_PATH.write_text("timestamp,uid,pages_read_count,pages_hash,allowed,notes\n")
        import hashlib
        h = hashlib.sha256(bytes.fromhex(pages_hex)).hexdigest()[:12] if pages_hex else ""
        entry = f'"{ts}","{uid_hex}",{pages_read_count},"{h}",{int(bool(allowed))},"{notes}"\n'
        LOG_PATH.write_text(LOG_PATH.read_text() + entry)
    except Exception as e:
        print("Warning: failed to append log:", e)

def find_matching_entry(whitelist, pages_hex, pages_read_count):
    """
    Return matching whitelist entry or None.
    Rules:
      - exact match: entry.pages == pages_hex and entry.pages_count == pages_read_count => match
      - if entry['partial'] is True and entry.pages == pages_hex (and pages_count == pages_read_count) => match
    We do NOT do prefix matching (partial read should match only stored partial reads).
    """
    pages_hex_norm = pages_hex.upper()
    for entry in whitelist:
        ent_pages = entry.get("pages","").upper()
        ent_count = int(entry.get("pages_count", 0) or 0)
        ent_partial = bool(entry.get("partial", False))
        if ent_pages == pages_hex_norm and ent_count == pages_read_count:
            return entry
        if ent_partial and ent_pages == pages_hex_norm and ent_count == pages_read_count:
            return entry
    return None

def read_tag_pages(pn532, max_pages=MAX_PAGES_TO_TRY, per_page_timeout=0.6):
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        return None, "", 0, False
    uid_hex = hexlify(bytes(uid)).upper().decode("ascii")

    pages_bytes = bytearray()
    pages_read = 0

    
    for p in range(max_pages):
        try:
            block = pn532.ntag2xx_read_block(p)  # returns 4 bytes on success, None on read failure
            if block is None:
                # stop reading further pages
                break
            pages_bytes.extend(bytes(block))
            pages_read += 1
            # small per-page pause to be gentle with radio
            time.sleep(0.02)
        except Exception as e:
            # exception reading page; treat as failure and stop
            print("Exception reading page", p, ":", e)
            break

    pages_hex = hexlify(bytes(pages_bytes)).upper().decode("ascii")
    return uid_hex, pages_hex, pages_read, pages_read > 0

def main():
    print("Initializing I2C PN532...")
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)
    pn532.SAM_configuration()

    print("PN532 Ultralight matcher starting (dynamic read)")
    whitelist = load_whitelist()

    try:
        while True:
            uid_hex, pages_hex, pages_read_count, success = read_tag_pages(pn532)
            if not success:
                time.sleep(POLL_INTERVAL)
                continue
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = find_matching_entry(whitelist, pages_hex, pages_read_count)
            if entry:
                message = f"[{ts}] UID {uid_hex} MATCH => ALLOW  (pages read {pages_read_count})"
                print(message)
                subprocess.run(['zenity', "--info", '--text', message, '--title', 'Access Granted'])

                append_log(ts, uid_hex, pages_hex, pages_read_count, True, entry.get('notes',''))
                # TODO: trigger a GPIO/relay/beep here for allow
            else:
                # Not found exact/partial match
                message = f"[{ts}] UID {uid_hex} NO MATCH => DENY  (pages read {pages_read_count})"
                print(message)
                subprocess.run(['zenity', '--info', '--text', message, '--title', 'Access Denied'])

                append_log(ts, uid_hex, pages_hex, pages_read_count, False, "")
            # small delay so same tag doesn't spam log repeatedly
            time.sleep(0.6)
    except KeyboardInterrupt:
        print("Exiting.")
    except Exception as e:
        print("Fatal error:", e)
        raise

if __name__ == "__main__":
    main()

