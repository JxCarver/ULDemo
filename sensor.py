import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import binascii
import string
import time

# I2C connection
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to read MiFare cards / enable SAM
pn532.SAM_configuration()

# Print firmware version (if available)
try:
    ic, ver, rev, support = pn532.firmware_version
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
except Exception:
    print("Couldn't read PN532 firmware version (driver may differ).")

def pretty_print_block(index, data):
    """Print block/page data in hex and ASCII (dots for non-printable)."""
    hexstr = ' '.join('{:02X}'.format(b) for b in data)
    ascii_str = ''.join(chr(b) if chr(b) in string.printable and b >= 0x20 else '.' for b in data)
    print(f"{index:03d}: {hexstr}    |{ascii_str}|")

print('Waiting for NFC card...')

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        # no card, continue polling
        continue

    print("Card detected!")
    print("UID:", [hex(i) for i in uid])

    time.sleep(1.0)

