"""
Example showing how to retrieve the primary key of your own AirTag, or any other FindMy-accessory.

This key can be used to retrieve the device's location for a single day.
"""
import plistlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from csvutil import CSVWriter
from findmy.keys import KeyType

from findmy import FindMyAccessory

# Path to a .plist dumped from the Find My app.
PLIST_PATH = Path("decrypted.plist")

# == The variables below are auto-filled from the plist!! ==

with PLIST_PATH.open("rb") as f:
    device_data = plistlib.load(f)

# PRIVATE master key. 28 (?) bytes.
MASTER_KEY = device_data["privateKey"]["key"]["data"][-28:]

# "Primary" shared secret. 32 bytes.
SKN = device_data["sharedSecret"]["key"]["data"]

# "Secondary" shared secret. 32 bytes.
# This doesn't apply in case of MacBook, but is used for AirTags and other accessories.
SKS = device_data["secureLocationsSharedSecret"]["key"]["data"]


def main() -> None:
    paired_at = device_data["pairingDate"].replace(tzinfo=timezone.utc)
    airtag = FindMyAccessory(MASTER_KEY, SKN, SKS, paired_at)

    # Generate keys for 2 days ahead
    now = datetime.now(tz=timezone.utc) + timedelta(hours=48)
    lookup_time = paired_at.replace(
        minute=paired_at.minute // 15 * 15,
        second=0,
        microsecond=0,
    ) + timedelta(minutes=15)

    mycsv = CSVWriter('discovery-keys.csv')

    while lookup_time < now:
        keys = airtag.keys_at(lookup_time)
        for key in keys:
            if key.key_type == KeyType.PRIMARY:
                mycsv.write(lookup_time, key.adv_key_b64, key.private_key_b64, key.key_type, key.hashed_adv_key_b64)

        lookup_time += timedelta(minutes=15)

if __name__ == "__main__":
    main()